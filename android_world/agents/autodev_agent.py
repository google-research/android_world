import json

from android_world.agents import base_agent
from android_world.agents.autodev_agent.llm import AutoDevLLM, ToolCall
from android_world.agents.autodev_agent.prompts import (
    EXECUTOR_SYSTEM_PROMPT,
    PLANNER_SYSTEM_PROMPT,
)
from android_world.agents.autodev_agent.util import (
    get_all_executor_tools_dict,
    get_all_planner_tools_dict,
    get_executor_registry,
    tool_call_to_query,
)
from android_world.env import interface

MAX_EXECUTOR_STEPS = 10


class AutoDev(base_agent.EnvironmentInteractingAgent):
    """Autodevice style agent."""

    def __init__(
        self,
        env: interface.AsyncEnv,
        name: str = "autodev",
    ):
        super().__init__(env, name)
        self._step_count = 0
        self.planner_llm = AutoDevLLM("sonnet", PLANNER_SYSTEM_PROMPT)

        self.planner_tools_dict = get_all_planner_tools_dict()
        self.executor_tools_dict = get_all_executor_tools_dict()

        self.executor_registry = get_executor_registry()

    def step(self, goal: str) -> base_agent.AgentInteractionResult:
        self._step_count += 1

        state = self.get_post_transition_state()
        screenshot = state.pixels.copy()
        planned_step = self.planner_llm.chat(
            goal if self._step_count == 1 else None,
            screenshot,
            tools=self.planner_tools_dict,
        )

        if planned_step["tool_calls"]:
            for tool_call in planned_step["tool_calls"]:
                if tool_call["function"]["name"] == "go_back":
                    self.env.execute_action(JSONAction(action_type="navigate_back"))
                elif tool_call["function"]["name"] == "answer":
                    self.env.execute_action(
                        JSONAction(
                            action_type="answer",
                            text=tool_call["function"]["arguments"]["text"],
                        )
                    )
                elif tool_call["function"]["name"] == "finish_task":
                    self.env.execute_action(JSONAction(action_type="finish_task"))
                else:
                    status = self.execute_step(tool_call)
                    self.planner_llm.add_tool_result(
                        tool_call["id"], json.dumps({"success": status})
                    )

        return base_agent.AgentInteractionResult(
            done=True,
            data={
                "agent_output": planned_step["content"],
                "step_count": self._step_count,
                "goal": goal,
                "error": False,
            },
        )

    def execute_step(self, tool_call: ToolCall) -> bool:
        executor_llm = AutoDevLLM("sonnet", EXECUTOR_SYSTEM_PROMPT)
        query = tool_call_to_query(tool_call)
        for i in range(MAX_EXECUTOR_STEPS):
            state = self.get_post_transition_state()
            screenshot = state.pixels.copy()
            execution_step = executor_llm.chat(
                query if i == 0 else None, screenshot, tools=self.executor_tools_dict
            )
            if execution_step["tool_calls"]:
                for tool_call in execution_step["tool_calls"]:
                    if tool_call["function"]["name"] == "done":
                        return tool_call["function"]["arguments"]["success"]
                    json_action = self.executor_registry[tool_call["function"]["name"]](
                        **tool_call["function"]["args"]
                    )
                    self.env.execute_action(json_action)
                    executor_llm.add_tool_result(tool_call["id"], "Done")
            else:
                print("ERROR, no tool call returned by executor LLM")
                return False

    def reset(self, go_home: bool = False) -> None:
        """Reset the agent."""
        super().reset(go_home)
        # Hide the coordinates/pointer visualization on screen
        self.env.hide_automation_ui()
        self._step_count = 0
        self._session_id = None  # Clear session ID on reset
