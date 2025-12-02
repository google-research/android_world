import json
from typing import Optional

import cv2
import numpy as np

from android_world.agents import base_agent
from android_world.agents.autodev import executor_tools
from android_world.agents.autodev.llm import AutoDevLLM, ToolCall

# Import the logging system
from android_world.agents.autodev.logging_system import TestRunLogger, serialize_tool_call
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
        log_dir: str = "./test_runs",
        enable_logging: bool = True,
        task_name: Optional[str] = None,
    ):
        super().__init__(env, name)
        self._step_count = 0
        self.scale = scale
        # Set the global scale in executor_tools
        executor_tools.SCALE = scale
        self.planner_llm = AutoDevLLM(
            "gemini/gemini-3-pro-preview", PLANNER_SYSTEM_PROMPT, True
        )

        self.planner_tools_dict = get_all_planner_tools_dict()
        self.executor_tools_dict = get_all_executor_tools_dict()
        self.target_width = 0
        self.target_height = 0
        self.executor_registry = get_executor_registry()
        self._is_done = False

        # Initialize logging
        self.enable_logging = enable_logging
        self.task_name = task_name
        # Pass env controller for ADB screenshot capture
        env_controller = env.controller if hasattr(env, 'controller') else None
        self.logger: TestRunLogger = TestRunLogger(log_dir, env_controller=env_controller) if enable_logging else None
        self.current_goal = None
        self.current_executor_session_id = None

    def _resize_screenshot_to_logical_size(self, screenshot: np.ndarray) -> np.ndarray:
        """Resize screenshot to scaled logical screen size."""
        logical_width, logical_height = self.env.logical_screen_size
        # Scale down by self.scale for model input
        self.target_width = int(logical_width * self.scale)
        self.target_height = int(logical_height * self.scale)
        current_height, current_width = screenshot.shape[:2]

        if current_width != self.target_width or current_height != self.target_height:
            resized = cv2.resize(
                screenshot,
                (self.target_width, self.target_height),
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

        # Start new logging run on first step
        if self._step_count == 1 and self.enable_logging:
            self.current_goal = goal
            run_id = self.logger.start_new_run(
                goal=goal,
                task_name=self.task_name,
                scale=self.scale,
                logical_screen_size=self.env.logical_screen_size,
                planner_model="gemini/gemini-3-pro-preview",
                executor_model="anthropic/claude-sonnet-4-5-20250929",
                agent_name="autodev",
            )
            print(f"📝 Logging enabled. Run ID: {run_id}")

        state = self.get_post_transition_state()
        screenshot = self._resize_screenshot_to_logical_size(state.pixels.copy())
        planned_step = self.planner_llm.chat(
            goal if self._step_count == 1 else None,
            screenshot,
            tools=self.planner_tools_dict,
        )

        # Show simplified planner step info (not full JSON)
        if planned_step.get("tool_calls"):
            tool_names = []
            for tc in planned_step["tool_calls"]:
                if isinstance(tc, dict):
                    name = tc.get("function", {}).get("name", "unknown")
                else:
                    tc_dict = serialize_tool_call(tc)
                    name = tc_dict.get("function", {}).get("name", "unknown")
                # Skip todo updates in terminal output
                if name != "update_todos":
                    tool_names.append(name)
            if tool_names:
                print(f"Step {self._step_count}: {', '.join(tool_names)}")
            else:
                print(f"Step {self._step_count}: Planning")
        else:
            print(f"Step {self._step_count}: No tool calls")

        # Log planner step
        if self.enable_logging:
            todo_state = None
            if hasattr(self.planner_llm, "todo_list"):
                todo_state = {
                    "todos": self.planner_llm.todo_list.todos
                    if hasattr(self.planner_llm.todo_list, "todos")
                    else []
                }

            self.logger.log_planner_step(
                step_number=self._step_count,
                user_input=goal if self._step_count == 1 else None,
                thinking=planned_step.get("content", ""),
                tool_calls=planned_step.get("tool_calls", []),
                screenshot=screenshot,
                todo_list_state=todo_state,
            )

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
                    if self.enable_logging:
                        # Note: success will be determined by task.is_successful() in the runner
                        self.logger.end_run(status="completed", success=None)
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

        DIMENSIONS = f"""\n\n === DIMENSIONS ===
        The screenshot being sent is {self.target_width}x{self.target_height}
        it is {self.target_width} pixels in width.
        it is {self.target_height} pixels in height.
        The top left corner is 0,0.

        Please point to things given its current width and height.

        NEVER EXCEED width and height dimensions.

        """
        executor_llm = AutoDevLLM(
            "anthropic/claude-sonnet-4-5-20250929", EXECUTOR_SYSTEM_PROMPT + DIMENSIONS
        )

        # Start new executor session for logging
        if self.enable_logging:
            self.current_executor_session_id = self.logger.start_executor_session(
                f"planner_step_{self._step_count}"
            )

        # This is the "intent" or high-level description from the planner.
        query = tool_call_to_query(planner_tool_call)

        # Track executor steps and results for logging
        executor_step_count = 0

        for i in range(MAX_EXECUTOR_STEPS):
            executor_step_count += 1
            state = self.get_post_transition_state()
            screenshot = self._resize_screenshot_to_logical_size(state.pixels.copy())

            execution_step = executor_llm.chat(
                query if i == 0 else None,
                screenshot,
                tools=self.executor_tools_dict,
            )
            # Show simplified executor step info (not full JSON)
            if execution_step.get("tool_calls"):
                tool_names = [tc.get("function", {}).get("name", "unknown") if isinstance(tc, dict)
                             else "unknown" for tc in execution_step["tool_calls"]]
                print(f"  Executor: {', '.join(tool_names)}")

            # Track tool results for logging
            tool_results = []

            if execution_step["tool_calls"]:
                for exec_call in execution_step["tool_calls"]:
                    fname = exec_call["function"]["name"]
                    args = exec_call["function"]["arguments"]
                    if isinstance(args, str):
                        args = json.loads(args)

                    # 1) Executor is done: return success back to planner
                    if fname == "report":
                        tool_results.append(
                            {"tool_call_id": exec_call["id"], "result": args}
                        )
                        # Only log executor step when it completes and reports back
                        if self.enable_logging:
                            final_state = self.get_post_transition_state()
                            final_screenshot = self._resize_screenshot_to_logical_size(final_state.pixels.copy())
                            self.logger.log_executor_step(
                                session_id=self.current_executor_session_id,
                                step_number=executor_step_count,
                                query=query,  # Always use the original query from planner
                                thinking=execution_step.get("content", ""),
                                tool_calls=execution_step["tool_calls"],
                                tool_results=tool_results,
                                screenshot=final_screenshot,  # Save final screenshot
                                dimensions={
                                    "width": self.target_width,
                                    "height": self.target_height,
                                },
                            )
                        self.planner_llm.add_tool_result(
                            planner_tool_call["id"],
                            json.dumps(args),
                        )
                        return

                    # 2) Executor extracted data: return that back to planner
                    if fname == "extracted_data":
                        tool_results.append(
                            {"tool_call_id": exec_call["id"], "result": args}
                        )
                        # Only log executor step when it completes
                        if self.enable_logging:
                            final_state = self.get_post_transition_state()
                            final_screenshot = self._resize_screenshot_to_logical_size(final_state.pixels.copy())
                            self.logger.log_executor_step(
                                session_id=self.current_executor_session_id,
                                step_number=executor_step_count,
                                query=query,  # Always use the original query from planner
                                thinking=execution_step.get("content", ""),
                                tool_calls=execution_step["tool_calls"],
                                tool_results=tool_results,
                                screenshot=final_screenshot,
                                dimensions={
                                    "width": self.target_width,
                                    "height": self.target_height,
                                },
                            )
                        self.planner_llm.add_tool_result(
                            planner_tool_call["id"],
                            json.dumps(args),
                        )
                        return

                    # 3) Normal executor actions (tap, swipe, etc.)
                    # Don't log intermediate micro-steps, only log when executor completes
                    try:
                        json_action = self.executor_registry[fname](**args)
                        self.env.execute_action(json_action)
                        executor_llm.add_tool_result(exec_call["id"], "Done")
                        tool_results.append(
                            {"tool_call_id": exec_call["id"], "result": "Done"}
                        )
                    except (ValueError, TypeError) as e:
                        error_msg = (
                            f"Error with coordinates: {e}. "
                            "Please provide x and y as separate integer values."
                        )
                        executor_llm.add_tool_result(exec_call["id"], error_msg)
                        tool_results.append(
                            {"tool_call_id": exec_call["id"], "result": error_msg}
                        )

            else:
                print(f"  Executor: ERROR - No tool call returned")

                # Log error state only (this is a meaningful completion point)
                if self.enable_logging:
                    error_state = self.get_post_transition_state()
                    error_screenshot = self._resize_screenshot_to_logical_size(error_state.pixels.copy())
                    self.logger.log_executor_step(
                        session_id=self.current_executor_session_id,
                        step_number=executor_step_count,
                        query=query,  # Always use the original query from planner
                        thinking=execution_step.get("content", ""),
                        tool_calls=[],
                        tool_results=[{"error": "No tool call returned"}],
                        screenshot=error_screenshot,
                        dimensions={
                            "width": self.target_width,
                            "height": self.target_height,
                        },
                    )

                self.planner_llm.add_tool_result(
                    planner_tool_call["id"],
                    json.dumps({"status": execution_step["content"]}),
                )
                return

    def reset(self, go_home: bool = False) -> None:
        """Reset the agent."""
        super().reset(go_home)
        # Hide the coordinates/pointer visualization on screen
        self.env.hide_automation_ui()
        self._step_count = 0
        self.planner_llm = AutoDevLLM(
            "gemini/gemini-3-pro-preview", PLANNER_SYSTEM_PROMPT, True
        )
        self._is_done = False
        self._session_id = None  # Clear session ID on reset

        # End any active logging run
        if self.enable_logging and self.logger and self.logger.run_metadata:
            self.logger.end_run(status="reset", success=False, success_reason="Agent reset")

    def log_task_validation(self, task, env) -> float:
        """
        Check task validation and log debugging information.
        This should be called by the runner after the agent finishes.
        
        Args:
            task: The task object to validate
            env: The environment object
            
        Returns:
            The success score (0.0 to 1.0) from task.is_successful(env)
        """
        if not self.enable_logging or not self.logger:
            return task.is_successful(env)
        
        success_score = task.is_successful(env)
        self.logger.log_validation_debug(task, env, success_score)
        return success_score

    def on_error(self, error: Exception) -> None:
        """Handle errors during execution."""
        if self.enable_logging and self.logger:
            self.logger.end_run(
                status="failed",
                error_details=str(error),
                success=False,
                success_reason=f"Error: {str(error)}"
            )