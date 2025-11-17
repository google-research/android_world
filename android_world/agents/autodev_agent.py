import json

import cv2
import numpy as np

from android_world.agents import base_agent
from android_world.agents.autodev import executor_tools
from android_world.agents.autodev.llm import AutoDevLLM, ToolCall
from android_world.agents.autodev.prompts import (
    EXECUTOR_SYSTEM_PROMPT,
    PLANNER_SYSTEM_PROMPT,
)
from android_world.agents.autodev.util import (
    get_all_executor_tools_dict,
    get_all_planner_tools_dict,
    get_executor_registry,
    tool_call_to_query,
)
from android_world.env import interface
from android_world.env.json_action import JSONAction

MAX_EXECUTOR_STEPS = 10


class AutoDev(base_agent.EnvironmentInteractingAgent):
    """Autodevice style agent."""

    def __init__(
        self,
        env: interface.AsyncEnv,
        name: str = "autodev",
        scale: float = 0.4,
    ):
        super().__init__(env, name)
        self._step_count = 0
        self.scale = scale
        # Set the global scale in executor_tools
        executor_tools.SCALE = scale
        self.planner_llm = AutoDevLLM("openai/gpt-5.1", PLANNER_SYSTEM_PROMPT, True)

        self.planner_tools_dict = get_all_planner_tools_dict()
        self.executor_tools_dict = get_all_executor_tools_dict()

        self.executor_registry = get_executor_registry()
        self._is_done = False

    def _resize_screenshot_to_logical_size(self, screenshot: np.ndarray) -> np.ndarray:
        """Resize screenshot to scaled logical screen size."""
        logical_width, logical_height = self.env.logical_screen_size
        # Scale down by self.scale for model input
        target_width = int(logical_width * self.scale)
        target_height = int(logical_height * self.scale)
        print(f"logical width: {logical_width}, logical_height: {logical_height}")
        print(f"target_width: {target_width}, target_height: {target_height}")
        current_height, current_width = screenshot.shape[:2]
        print(f"current_width: {current_width}, current_height: {current_height}")
        if current_width != target_width or current_height != target_height:
            resized = cv2.resize(
                screenshot,
                (target_width, target_height),
                interpolation=cv2.INTER_LINEAR,
            )
            return resized
        return screenshot

    def step(self, goal: str) -> base_agent.AgentInteractionResult:
        """
        This is the main agent loop.
        The android_world framework calls this in a loop until done = True or timeout/max_steps reached.
        """
        self._step_count += 1

        state = self.get_post_transition_state()
        screenshot = self._resize_screenshot_to_logical_size(state.pixels.copy())
        planned_step = self.planner_llm.chat(
            goal if self._step_count == 1 else None,
            screenshot,
            tools=self.planner_tools_dict,
        )

        print(planned_step)

        if planned_step["tool_calls"]:
            for tool_call in planned_step["tool_calls"]:
                if tool_call["function"]["name"] == "go_back":
                    self.env.execute_action(JSONAction(action_type="navigate_back"))
                    self.planner_llm.add_tool_result(
                        tool_call["id"], json.dumps({"success": True})
                    )
                elif tool_call["function"]["name"] == "answer":
                    args = tool_call["function"]["arguments"]
                    if isinstance(args, str):
                        args = json.loads(args)

                    self.env.execute_action(
                        JSONAction(
                            action_type="answer",
                            text=args["text"],
                        )
                    )
                    self.planner_llm.add_tool_result(
                        tool_call["id"], json.dumps({"success": True})
                    )
                elif tool_call["function"]["name"] == "finish_task":
                    # self.env.execute_action(JSONAction(action_type="finish_task"))
                    self._is_done = True
                elif tool_call["function"]["name"] == "update_todos":
                    args = tool_call["function"]["arguments"]
                    if isinstance(args, str):
                        args = json.loads(args)

                    res = self.planner_llm.todo_list.update(args["todos"])
                    print(self.planner_llm.todo_list.pretty_print())
                    self.planner_llm.add_tool_result(tool_call["id"], json.dumps(res))
                else:
                    self.execute_step(tool_call)

        return base_agent.AgentInteractionResult(
            done=self._is_done,
            data={
                "agent_output": planned_step["content"],
                "step_count": self._step_count,
                "goal": goal,
                "error": False,
            },
        )

    def execute_step(self, planner_tool_call: ToolCall) -> None:
        """Run the executor loop for a single planner tool call and
        send the final result back to the planner via add_tool_result."""
        executor_llm = AutoDevLLM(
            "anthropic/claude-sonnet-4-5-20250929", EXECUTOR_SYSTEM_PROMPT
        )

        # This is the "intent" or high-level description from the planner.
        query = tool_call_to_query(planner_tool_call)

        for i in range(MAX_EXECUTOR_STEPS):
            state = self.get_post_transition_state()
            screenshot = self._resize_screenshot_to_logical_size(state.pixels.copy())

            execution_step = executor_llm.chat(
                query if i == 0 else None,
                screenshot,
                tools=self.executor_tools_dict,
            )

            if execution_step["tool_calls"]:
                for exec_call in execution_step["tool_calls"]:
                    fname = exec_call["function"]["name"]
                    args = exec_call["function"]["arguments"]
                    if isinstance(args, str):
                        args = json.loads(args)

                    # 1) Executor is done: return success back to planner
                    if fname == "done":
                        # expected schema: {"success": bool}
                        self.planner_llm.add_tool_result(
                            planner_tool_call["id"],
                            json.dumps(args),
                        )
                        return

                    # 2) Executor extracted data: return that back to planner
                    if fname == "extracted_data":
                        # e.g. {"data": ...}
                        self.planner_llm.add_tool_result(
                            planner_tool_call["id"],
                            json.dumps(args),
                        )
                        return

                    # 3) Normal executor actions (tap, swipe, etc.)
                    try:
                        json_action = self.executor_registry[fname](**args)
                        self.env.execute_action(json_action)
                        executor_llm.add_tool_result(exec_call["id"], "Done")
                    except (ValueError, TypeError) as e:
                        error_msg = (
                            f"Error with coordinates: {e}. "
                            "Please provide x and y as separate integer values."
                        )
                        executor_llm.add_tool_result(exec_call["id"], error_msg)

            else:
                print("ERROR, no tool call returned by executor LLM")
                # optional: tell planner it failed
                self.planner_llm.add_tool_result(
                    planner_tool_call["id"],
                    json.dumps({"success": False, "error": "no_executor_tool_calls"}),
                )
                return

    def reset(self, go_home: bool = False) -> None:
        """Reset the agent."""
        super().reset(go_home)
        # Hide the coordinates/pointer visualization on screen
        self.env.hide_automation_ui()
        self._step_count = 0
        self.planner_llm = AutoDevLLM("openai/gpt-5.1", PLANNER_SYSTEM_PROMPT, True)
        self._is_done = False
        self._session_id = None  # Clear session ID on reset
