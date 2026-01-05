"""
Updated logging system with proper ChatCompletionMessageToolCall serialization.
"""

import json
import os
import re
import shutil
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np


def serialize_tool_call(tool_call: Any) -> Dict[str, Any]:
    """
    Convert a ChatCompletionMessageToolCall object to a JSON-serializable dictionary.

    This handles the litellm.types.utils.ChatCompletionMessageToolCall object
    which has the following structure:
    - id: string identifier
    - type: typically "function"
    - function: Function object with name and arguments
    """
    # If it's already a dict, return it
    if isinstance(tool_call, dict):
        return tool_call

    result = {}

    # Extract basic fields
    if hasattr(tool_call, "id"):
        result["id"] = tool_call.id
    elif hasattr(tool_call, "get"):
        result["id"] = tool_call.get("id")

    if hasattr(tool_call, "type"):
        result["type"] = tool_call.type
    elif hasattr(tool_call, "get"):
        result["type"] = tool_call.get("type", "function")

    # Extract function information
    if hasattr(tool_call, "function"):
        func = tool_call.function
        result["function"] = {}

        if isinstance(func, dict):
            result["function"] = func
        else:
            if hasattr(func, "name"):
                result["function"]["name"] = func.name
            if hasattr(func, "arguments"):
                result["function"]["arguments"] = func.arguments

            # Try to get any other attributes
            if hasattr(func, "__dict__"):
                for key, value in func.__dict__.items():
                    if not key.startswith("_") and key not in ["name", "arguments"]:
                        result["function"][key] = value

    return result


@dataclass
class PlannerStep:
    """Data structure for planner step information"""

    step_number: int
    timestamp: str
    user_input: Optional[str]  # Goal or None for subsequent steps
    thinking: str  # The planner's reasoning/content
    tool_calls: List[Any]  # Will be serialized when saving
    todo_list_state: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None
    status: str = "success"  # "success", "error", "failed"
    error_message: Optional[str] = None


@dataclass
class ExecutorStep:
    """Data structure for executor step information"""

    step_number: int
    timestamp: str
    query: str  # The intent/query from planner
    thinking: str  # The executor's reasoning/content
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    screenshot_path: Optional[str] = None
    dimensions: Dict[str, int] = None  # width, height info
    status: str = "success"  # "success", "error", "failed"
    error_message: Optional[str] = None
    planner_tool_call_id: Optional[str] = None  # ADD THIS: Link to planner step


@dataclass
class TestRunMetadata:
    """Metadata for the entire test run"""

    run_id: str
    start_time: str
    end_time: Optional[str]
    goal: str
    task_name: Optional[str] = None  # Task name for directory structure
    model_config: Dict[str, Any] = None
    scale_factor: float = 1.0
    logical_screen_size: tuple = None
    total_planner_steps: int = 0
    total_executor_steps: int = 0
    final_status: str = "in_progress"  # in_progress, completed, failed, timeout
    error_details: Optional[str] = None
    success: Optional[bool] = None  # Task success status
    success_reason: Optional[str] = None  # Reason for success/failure
    agent_name: Optional[str] = None  # Agent name (e.g., "autodev", "t3a")


class TestRunLogger:
    """Main logging class for AutoDev test runs with proper serialization."""

    def __init__(self, base_log_dir: str = "./test_runs", env_controller=None):
        """
        Initialize the logger with a base directory for all test runs.

        Args:
            base_log_dir: Base directory where all test run logs will be stored
            env_controller: Optional environment controller for ADB screenshot capture
        """
        self.base_log_dir = Path(base_log_dir)
        self.base_log_dir.mkdir(parents=True, exist_ok=True)
        self.env_controller = env_controller  # For ADB screenshot capture

        # Current run state
        self.current_run_dir: Optional[Path] = None
        self.run_metadata: Optional[TestRunMetadata] = None
        self.planner_steps: List[PlannerStep] = []
        self.executor_sessions: Dict[str, List[ExecutorStep]] = []
        
        # Unified steps tracking (for general agents)
        self.unified_steps: List[Dict[str, Any]] = []
        self.step_counter: int = 0

    def start_new_run(
        self,
        goal: str,
        task_name: Optional[str] = None,
        scale: float = 1.0,
        logical_screen_size: tuple = None,
        planner_model: str = "gemini/gemini-3-pro-preview",
        executor_model: str = "anthropic/claude-sonnet-4-5-20250929",
        agent_name: Optional[str] = None,
    ) -> str:
        """
        Initialize a new test run with its own directory.

        Args:
            goal: Task goal/description
            task_name: Optional task name (e.g., "ContactsAddContact")
            scale: Scale factor for screenshots (default 1.0)
            logical_screen_size: Logical screen size tuple
            planner_model: Planner model name
            executor_model: Executor model name
            agent_name: Agent name (e.g., "autodev", "t3a")

        Returns:
            run_id: Unique identifier for this run
        """
        # Generate unique run ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create directory name with task name if provided
        if task_name:
            # Sanitize task name for filesystem
            safe_task_name = re.sub(r'[^\w\-_\.]', '_', task_name)
            dir_name = f"{safe_task_name}_{timestamp}"
        else:
            dir_name = f"run_{timestamp}_{uuid.uuid4().hex[:8]}"
        
        run_id = dir_name

        # Create run directory structure
        self.current_run_dir = self.base_log_dir / run_id
        self.current_run_dir.mkdir(parents=True, exist_ok=True)

        # Create screenshots directory (unified for all screenshots)
        (self.current_run_dir / "screenshots").mkdir(exist_ok=True)
        
        # Create logs.txt file for terminal output
        self.logs_file = self.current_run_dir / "logs.txt"
        self.logs_file.touch()

        # Initialize metadata
        model_config = {}
        if planner_model and executor_model:
            model_config = {
                "planner_model": planner_model,
                "executor_model": executor_model,
            }
        
        self.run_metadata = TestRunMetadata(
            run_id=run_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            goal=goal,
            task_name=task_name,
            model_config=model_config,
            scale_factor=scale,
            logical_screen_size=logical_screen_size or (0, 0),
            agent_name=agent_name,
        )

        # Reset step tracking
        self.planner_steps = []
        self.executor_sessions = {}  # Keep as dict for AutoDev compatibility
        self.unified_steps = []
        self.step_counter = 0

        # Capture initial screenshot if env_controller is available
        if self.env_controller:
            self._capture_adb_screenshot("screenshots/step_000_initial.png")

        # Save initial metadata
        self._save_metadata()

        return run_id
    
    def log_to_file(self, message: str) -> None:
        """Write a message to logs.txt file."""
        if self.logs_file and self.logs_file.exists():
            with open(self.logs_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")

    def log_planner_step(
        self,
        step_number: int,
        user_input: Optional[str],
        thinking: str,
        tool_calls: List[Any],  # These are ChatCompletionMessageToolCall objects
        screenshot: np.ndarray,
        todo_list_state: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        """
        Log a planner step with its screenshot.

        The tool_calls parameter contains ChatCompletionMessageToolCall objects
        which will be properly serialized when saving.
        """
        if not self.current_run_dir:
            raise ValueError("No active run. Call start_new_run first.")

        # Save screenshot to unified screenshots directory
        screenshot_filename = f"step_{step_number:03d}_planner.png"
        screenshot_path = self.current_run_dir / "screenshots" / screenshot_filename
        cv2.imwrite(str(screenshot_path), screenshot)

        # Create planner step record (store original objects, serialize on save)
        planner_step = PlannerStep(
            step_number=step_number,
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            thinking=thinking,
            tool_calls=tool_calls,
            todo_list_state=todo_list_state,
            screenshot_path=f"screenshots/{screenshot_filename}",
            status=status,
            error_message=error_message,
        )

        self.planner_steps.append(planner_step)
        self.run_metadata.total_planner_steps = len(self.planner_steps)

        # Save updated data
        self._save_planner_steps()
        self._save_metadata()

    def start_executor_session(self, planner_step_id: str, planner_tool_call_id: Optional[str] = None) -> str:
        """
        Start tracking a new executor session for a planner tool call.

        Args:
            planner_step_id: Unique identifier for the planner step
            planner_tool_call_id: The actual planner tool call ID for linking

        Returns:
            session_id: Unique identifier for this executor session
        """
        session_id = f"exec_session_{len(self.executor_sessions):03d}"
        self.executor_sessions[session_id] = []
        # Store planner tool call ID in session metadata (we'll need to add this)
        # For now, we'll pass it to each log_executor_step call
        return session_id

    def log_executor_step(
        self,
        session_id: str,
        step_number: int,
        query: str,
        thinking: str,
        tool_calls: List[Any],
        tool_results: List[Dict[str, Any]],
        screenshot: Optional[np.ndarray],
        dimensions: Dict[str, int],
        status: str = "success",
        error_message: Optional[str] = None,
        planner_tool_call_id: Optional[str] = None,  # ADD THIS
    ) -> None:
        """
        Log an executor step within a session.
        """
        if not self.current_run_dir:
            raise ValueError("No active run. Call start_new_run first.")

        if session_id not in self.executor_sessions:
            raise ValueError(f"Unknown session_id: {session_id}")

        screenshot_path_str = None
        
        # Only save screenshot if provided (skip intermediate micro-steps)
        if screenshot is not None:
            # Calculate global step number for unified screenshot naming
            global_step = self.run_metadata.total_planner_steps + len(self.executor_sessions[session_id]) + 1
            
            # Save screenshot to unified screenshots directory
            screenshot_filename = f"step_{global_step:03d}_executor.png"
            screenshot_path = self.current_run_dir / "screenshots" / screenshot_filename
            cv2.imwrite(str(screenshot_path), screenshot)  # FIX: This was incorrectly indented
            screenshot_path_str = f"screenshots/{screenshot_filename}"

        # Serialize tool_calls if they're ChatCompletionMessageToolCall objects
        serialized_tool_calls = []
        for tc in tool_calls:
            if isinstance(tc, dict):
                serialized_tool_calls.append(tc)
            else:
                serialized_tool_calls.append(serialize_tool_call(tc))

        # Create executor step record
        executor_step = ExecutorStep(
            step_number=step_number,
            timestamp=datetime.now().isoformat(),
            query=query,
            thinking=thinking,
            tool_calls=serialized_tool_calls,
            tool_results=tool_results,
            screenshot_path=screenshot_path_str,  # None if no screenshot saved
            dimensions=dimensions,
            status=status,
            error_message=error_message,
            planner_tool_call_id=planner_tool_call_id,  # ADD THIS
        )

        self.executor_sessions[session_id].append(executor_step)
        self.run_metadata.total_executor_steps += 1

        # Save updated data
        self._save_executor_sessions()
        self._save_metadata()

    def set_success(self, success: bool, reason: Optional[str] = None) -> None:
        """
        Set the success status of the task (can be called before end_run).
        
        Args:
            success: Whether the task was successful
            reason: Human-readable reason for success/failure
        """
        if self.run_metadata:
            self.run_metadata.success = success
            if reason:
                self.run_metadata.success_reason = reason
            elif success:
                self.run_metadata.success_reason = "Task completed successfully"
            else:
                self.run_metadata.success_reason = "Task failed"

    def log_validation_debug(
        self,
        task,
        env,
        success_score: float,
    ) -> None:
        """
        Log validation debugging information for tasks that have validation.
        This helps understand why a task passed or failed validation.
        
        Args:
            task: The task object (must have params attribute for contact tasks)
            env: The environment object (must have controller attribute)
            success_score: The result from task.is_successful(env)
        """
        if not self.run_metadata:
            return
        
        # Check if this is a contact task and log debugging info
        if hasattr(task, 'params') and 'name' in task.params:
            try:
                from android_world.utils import contacts_utils
                expected_name = task.params['name']
                expected_number = contacts_utils.clean_phone_number(task.params.get('number', ''))
                actual_contacts = contacts_utils.list_contacts(env.controller)
                
                debug_info = {
                    "expected_name": expected_name,
                    "expected_number": expected_number,
                    "actual_contacts": [
                        {"name": c.name, "number": c.number}
                        for c in actual_contacts
                    ],
                    "success_score": success_score,
                }
                
                # Save to validation_debug.json
                if self.current_run_dir:
                    debug_path = self.current_run_dir / "validation_debug.json"
                    with open(debug_path, "w") as f:
                        json.dump(debug_info, f, indent=2)
                
                # Print debugging info
                print(f"\n🔍 Validation Debug:")
                print(f"   Expected: {expected_name} ({expected_number})")
                print(f"   Found {len(actual_contacts)} contact(s):")
                for contact in actual_contacts:
                    match_name = "✅" if contact.name == expected_name else "❌"
                    match_num = "✅" if contact.number == expected_number else "❌"
                    print(f"     {match_name} Name: '{contact.name}' | {match_num} Number: '{contact.number}'")
                print(f"   Success score: {success_score}")
                
            except Exception as e:
                print(f"Warning: Could not log validation debug info: {e}")

    def end_run(
        self,
        status: str = "completed",
        error_details: Optional[str] = None,
        success: Optional[bool] = None,
        success_reason: Optional[str] = None,
    ) -> None:
        """
        Finalize the current test run.

        Args:
            status: Final status of the run
            error_details: Any error information if applicable
            success: Whether the task was successful (True/False)
            success_reason: Human-readable reason for success/failure
        """
        if not self.run_metadata:
            return

        # Update success status if provided
        if success is not None:
            self.set_success(success, success_reason)

        self.run_metadata.end_time = datetime.now().isoformat()
        self.run_metadata.final_status = status
        if error_details:
            self.run_metadata.error_details = error_details

        # Capture final screenshot if env_controller is available
        if self.env_controller:
            self._capture_adb_screenshot("screenshots/step_final.png")

        # Save all data files
        self._save_metadata()
        self._save_planner_steps()
        self._save_executor_sessions()
        self._save_unified_steps()
        self._save_success_json()
        self._create_summary_report()
        self._create_timeline_md()

    def _save_metadata(self) -> None:
        """Save run metadata to JSON file"""
        if not self.current_run_dir or not self.run_metadata:
            return

        metadata_path = self.current_run_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(asdict(self.run_metadata), f, indent=2)

    def _save_planner_steps(self) -> None:
        """Save all planner steps to JSON file with proper serialization"""
        if not self.current_run_dir:
            return

        planner_path = self.current_run_dir / "planner_steps.json"

        # Convert steps to dictionaries with proper tool_call serialization
        steps_data = []
        for step in self.planner_steps:
            step_dict = asdict(step)

            # Serialize tool_calls properly
            serialized_tool_calls = []
            for tc in (step.tool_calls or []):
                if isinstance(tc, dict):
                    serialized_tool_calls.append(tc)
                else:
                    serialized_tool_calls.append(serialize_tool_call(tc))

            step_dict["tool_calls"] = serialized_tool_calls
            steps_data.append(step_dict)

        with open(planner_path, "w") as f:
            json.dump(steps_data, f, indent=2)

    def _save_executor_sessions(self) -> None:
        """Save all executor sessions to JSON file"""
        if not self.current_run_dir:
            return

        executor_path = self.current_run_dir / "executor_sessions.json"
        sessions_data = {
            session_id: [asdict(step) for step in steps]
            for session_id, steps in self.executor_sessions.items()
        }
        with open(executor_path, "w") as f:
            json.dump(sessions_data, f, indent=2)

    def _create_summary_report(self) -> None:
        """Create a human-readable summary report"""
        if not self.current_run_dir or not self.run_metadata:
            return

        summary_path = self.current_run_dir / "summary.txt"
        with open(summary_path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write(f"TEST RUN SUMMARY: {self.run_metadata.run_id}\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Goal: {self.run_metadata.goal}\n")
            f.write(f"Status: {self.run_metadata.final_status}\n")
            f.write(f"Start Time: {self.run_metadata.start_time}\n")
            f.write(f"End Time: {self.run_metadata.end_time}\n")
            f.write(f"Total Planner Steps: {self.run_metadata.total_planner_steps}\n")
            f.write(f"Total Executor Steps: {self.run_metadata.total_executor_steps}\n")
            f.write(f"Scale Factor: {self.run_metadata.scale_factor}\n")
            f.write(f"Screen Size: {self.run_metadata.logical_screen_size}\n")

            if self.run_metadata.error_details:
                f.write(f"\nError Details:\n{self.run_metadata.error_details}\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("PLANNER STEPS SUMMARY\n")
            f.write("=" * 60 + "\n")

            for step in self.planner_steps:
                f.write(f"\nStep {step.step_number}:\n")
                if step.user_input:
                    f.write(f"  Input: {step.user_input}\n")
                f.write(f"  Time: {step.timestamp}\n")
                
                # Safely handle None tool_calls
                tool_calls = step.tool_calls if step.tool_calls is not None else []
                f.write(f"  Tool Calls: {len(tool_calls)}\n")

                # Handle both dict and object tool_calls
                for tc in tool_calls:
                    if isinstance(tc, dict):
                        name = tc.get("function", {}).get("name", "unknown")
                    else:
                        tc_dict = serialize_tool_call(tc)
                        name = tc_dict.get("function", {}).get("name", "unknown")
                    f.write(f"    - {name}\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("EXECUTOR SESSIONS SUMMARY\n")
            f.write("=" * 60 + "\n")

            for session_id, steps in self.executor_sessions.items():
                f.write(f"\n{session_id}: {len(steps)} steps\n")
                if steps:
                    query = steps[0].query if steps[0].query else "No query"
                    if len(query) > 100:
                        query = query[:100] + "..."
                    f.write(f"  Query: {query}\n")

    def log_step(
        self,
        description: str,
        raw_action: Dict[str, Any],
        result: str = "success",
        screenshot: Optional[np.ndarray] = None,
        reason: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> None:
        """
        Log a general step (for non-AutoDev agents).
        
        Args:
            description: Human-readable action description
            raw_action: Raw action dictionary (e.g., {"action_type": "click", "x": 100, "y": 200})
            result: Step result ("success", "retry", "fail")
            screenshot: Optional screenshot as numpy array
            reason: Optional reason for the action (from agent's reasoning)
            summary: Optional summary of the step (from agent's summary)
        """
        if not self.current_run_dir:
            raise ValueError("No active run. Call start_new_run first.")

        self.step_counter += 1
        timestamp = datetime.now().isoformat()

        # Sanitize description for filename
        safe_desc = self._sanitize_filename(description)
        screenshot_filename = f"step_{self.step_counter:03d}_{safe_desc}.png"
        screenshot_path = self.current_run_dir / "screenshots" / screenshot_filename

        # Save screenshot
        if screenshot is not None:
            cv2.imwrite(str(screenshot_path), screenshot)
        elif self.env_controller:
            # Try to capture via ADB
            self._capture_adb_screenshot(f"screenshots/{screenshot_filename}")

        # Create step record
        step_data = {
            "step_number": self.step_counter,
            "timestamp": timestamp,
            "description": description,
            "raw_action": raw_action,
            "screenshot_filename": f"screenshots/{screenshot_filename}",
            "result": result,
            "reason": reason,  # Agent's reasoning for the action
            "summary": summary,  # Agent's summary of the step
        }

        self.unified_steps.append(step_data)

        # Save updated steps
        self._save_unified_steps()

    def _capture_adb_screenshot(self, filename: str) -> bool:
        """
        Capture screenshot using ADB via environment controller.
        
        Args:
            filename: Filename to save screenshot as
            
        Returns:
            True if successful, False otherwise
        """
        if not self.env_controller or not self.current_run_dir:
            return False

        try:
            from android_env.proto import adb_pb2

            # Execute ADB screencap command
            response = self.env_controller.execute_adb_call(
                adb_pb2.AdbRequest(
                    generic=adb_pb2.AdbRequest.GenericRequest(
                        args=["exec-out", "screencap", "-p"]
                    )
                )
            )

            if response.status == adb_pb2.AdbResponse.Status.OK:
                # Handle both with and without screenshots/ prefix
                if filename.startswith("screenshots/"):
                    screenshot_path = self.current_run_dir / filename
                else:
                    screenshot_path = self.current_run_dir / "screenshots" / filename
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                with open(screenshot_path, "wb") as f:
                    f.write(response.generic.output)
                return True
        except Exception as e:
            # Silently fail - don't crash the logger
            print(f"Warning: Failed to capture ADB screenshot: {e}")
            return False

        return False

    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """Sanitize text for use in filenames."""
        # Remove special characters
        text = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with underscores
        text = re.sub(r'[\s]+', '_', text)
        # Remove multiple underscores
        text = re.sub(r'_+', '_', text)
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        return text.lower().strip('_')

    def _save_unified_steps(self) -> None:
        """Save unified steps to steps.json"""
        if not self.current_run_dir:
            return

        steps_path = self.current_run_dir / "steps.json"
        with open(steps_path, "w") as f:
            json.dump(self.unified_steps, f, indent=2)

    def _save_success_json(self) -> None:
        """Save success.json with task result metadata"""
        if not self.current_run_dir or not self.run_metadata:
            return

        # Calculate duration
        start_time = datetime.fromisoformat(self.run_metadata.start_time)
        end_time = datetime.fromisoformat(self.run_metadata.end_time) if self.run_metadata.end_time else datetime.now()
        duration_seconds = (end_time - start_time).total_seconds()

        success_data = {
            "success": self.run_metadata.success if self.run_metadata.success is not None else False,
            "reason": self.run_metadata.success_reason or "Unknown",
            "duration_seconds": round(duration_seconds, 2),
            "total_steps": len(self.unified_steps) if self.unified_steps else (
                self.run_metadata.total_planner_steps + self.run_metadata.total_executor_steps
            ),
            "task_name": self.run_metadata.task_name,
            "timestamp_start": self.run_metadata.start_time,
            "timestamp_end": self.run_metadata.end_time,
            "agent_name": self.run_metadata.agent_name,
            "final_status": self.run_metadata.final_status,
        }

        success_path = self.current_run_dir / "success.json"
        with open(success_path, "w") as f:
            json.dump(success_data, f, indent=2)

    def _create_timeline_md(self) -> None:
        """Create timeline.md in DroidRun-style format with thinking, code, and results"""
        if not self.current_run_dir or not self.run_metadata:
            return

        timeline_path = self.current_run_dir / "timeline.md"
        
        with open(timeline_path, "w") as f:
            # Header
            task_name = self.run_metadata.task_name or "Unknown Task"
            f.write(f"# {task_name}\n\n")
            
            # Plan Input
            f.write("## Plan Input\n\n")
            f.write("**Input:**\n\n")
            f.write(f"user:\n\n")
            f.write(f"Goal: {self.run_metadata.goal}\n\n")
            f.write("user: None\n\n")
            f.write("---\n\n")

            # If we have unified steps (general agent), use those
            if self.unified_steps:
                for step in self.unified_steps:
                    step_num = step.get("step_number", 0)
                    desc = step.get("description", "Unknown action")
                    raw_action = step.get("raw_action", {})
                    result = step.get("result", "unknown")
                    screenshot_file = step.get("screenshot_filename", "")
                    reason_text = step.get('reason', '')
                    summary_text = step.get('summary', '')
                    
                    f.write("## Task Thinking\n\n")
                    f.write(f"### Step {step_num}\n\n")
                    
                    # Thoughts (reasoning)
                    if reason_text:
                        f.write(f"**Thoughts:**\n\n{reason_text}\n\n")
                    elif desc:
                        f.write(f"**Thoughts:**\n\n{desc}\n\n")
                    
                    # Code (action)
                    f.write("**Code:**\n\n")
                    action_code = self._format_action_code(raw_action)
                    f.write(f"```\n{action_code}\n```\n\n")
                    
                    # Task Execution Result
                    f.write("## Task Execution Result\n\n")
                    if summary_text:
                        f.write(f"**Output:**\n\n{summary_text}\n\n")
                    else:
                        f.write(f"**Output:**\n\n{desc}\n\n")
                    
                    # Task End
                    result_emoji = "✅" if result == "success" else "⚠️" if result == "retry" else "❌"
                    f.write("## Task End\n\n")
                    f.write(f"**Success Reason:**\n\n{summary_text or desc or 'Action completed'}\n\n")
                    f.write(f"**{result_emoji} {result.capitalize()}**\n\n")
                    
                    # Screenshot
                    if screenshot_file:
                        screenshot_path = self.current_run_dir / screenshot_file
                        if screenshot_path.exists():
                            f.write(f"![Step {step_num}]({screenshot_file})\n\n")
                    
                    f.write("---\n\n")
            else:
                # AutoDev format: Combine planner thinking with executor results
                step_counter = 0
                executor_step_map = {}  # Map planner step number to executor result
                
                # Build executor step map - match executor sessions to planner steps
                executor_sessions_list = list(self.executor_sessions.items())
                for session_id, exec_steps in executor_sessions_list:
                    if exec_steps:
                        # Try to extract planner step number from session_id
                        # Format: "planner_step_N" or "exec_session_XXX"
                        match = re.search(r'planner_step_(\d+)', session_id)
                        if match:
                            planner_step_num = int(match.group(1))
                        else:
                            # Fallback: use order
                            planner_step_num = len(executor_step_map) + 1
                        
                        # Get the last executor step (completion result)
                        executor_step_map[planner_step_num] = exec_steps[-1]
                
                # Write planner steps with executor results
                for idx, step in enumerate(self.planner_steps):
                    step_counter += 1
                    planner_step_num = step.step_number
                    
                    f.write("## Task Thinking\n\n")
                    f.write(f"### Step {step_counter}\n\n")
                    
                    # Thoughts (planner's thinking)
                    f.write("**Thoughts:**\n\n")
                    thinking = step.thinking.strip() if step.thinking else ""
                    if thinking:
                        f.write(f"{thinking}\n\n")
                    else:
                        # Extract from tool calls if no thinking
                        if step.tool_calls:
                            for tc in step.tool_calls:
                                if isinstance(tc, dict):
                                    name = tc.get("function", {}).get("name", "unknown")
                                    args = tc.get("function", {}).get("arguments", {})
                                else:
                                    tc_dict = serialize_tool_call(tc)
                                    name = tc_dict.get("function", {}).get("name", "unknown")
                                    args = tc_dict.get("function", {}).get("arguments", {})
                                
                                if name == "update_todos":
                                    continue  # Skip todo updates in thoughts
                                
                                # Format intent from args
                                if isinstance(args, str):
                                    try:
                                        args = json.loads(args)
                                    except:
                                        pass
                                
                                intent = args.get("intent", "") if isinstance(args, dict) else ""
                                if intent:
                                    f.write(f"{intent}\n\n")
                    
                    # Code (action from tool calls)
                    f.write("**Code:**\n\n")
                    code_lines = []
                    for tc in step.tool_calls:
                        if isinstance(tc, dict):
                            name = tc.get("function", {}).get("name", "unknown")
                            args = tc.get("function", {}).get("arguments", {})
                        else:
                            tc_dict = serialize_tool_call(tc)
                            name = tc_dict.get("function", {}).get("name", "unknown")
                            args = tc_dict.get("function", {}).get("arguments", {})
                        
                        # Skip todo updates in code display
                        if name == "update_todos":
                            continue
                        
                        # Format code
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except:
                                pass
                        
                        code_str = self._format_tool_call_code(name, args)
                        if code_str:
                            code_lines.append(code_str)
                    
                    if code_lines:
                        f.write("```\n")
                        for code_line in code_lines:
                            f.write(f"{code_line}\n")
                        f.write("```\n\n")
                    else:
                        f.write("```\nNo action\n```\n\n")
                    
                    # Task Execution Result (from executor)
                    f.write("## Task Execution Result\n\n")
                    executor_result = executor_step_map.get(planner_step_num)
                    if executor_result:
                        # Get result from executor's tool_results or thinking
                        if executor_result.tool_results:
                            result_text = executor_result.tool_results[-1].get("result", "")
                            if isinstance(result_text, dict):
                                result_text = result_text.get("notes", result_text.get("status", ""))
                            if result_text:
                                f.write(f"**Output:**\n\n{result_text}\n\n")
                            else:
                                f.write(f"**Output:**\n\n{executor_result.thinking or 'Action executed'}\n\n")
                        else:
                            f.write(f"**Output:**\n\n{executor_result.thinking or 'Action executed'}\n\n")
                    else:
                        # Fallback to planner's tool call intent
                        for tc in step.tool_calls:
                            if isinstance(tc, dict):
                                name = tc.get("function", {}).get("name", "")
                                args = tc.get("function", {}).get("arguments", {})
                            else:
                                tc_dict = serialize_tool_call(tc)
                                name = tc_dict.get("function", {}).get("name", "")
                                args = tc_dict.get("function", {}).get("arguments", {})
                            
                            if name == "update_todos":
                                continue
                            
                            if isinstance(args, str):
                                try:
                                    args = json.loads(args)
                                except:
                                    pass
                            
                            intent = args.get("intent", "") if isinstance(args, dict) else ""
                            if intent:
                                f.write(f"**Output:**\n\n{intent}\n\n")
                                break
                    
                    # Task End
                    f.write("## Task End\n\n")
                    success_reason = "Action completed successfully"
                    step_status = "success"
                    if executor_result:
                        step_status = executor_result.status
                        if executor_result.tool_results:
                            result = executor_result.tool_results[-1].get("result", {})
                            if isinstance(result, dict):
                                success_reason = result.get("notes", result.get("status", success_reason))
                            elif isinstance(result, str) and result:
                                success_reason = result
                        if executor_result.error_message:
                            success_reason = executor_result.error_message
                            step_status = "failed"
                    
                    f.write(f"**Success Reason:**\n\n{success_reason}\n\n")
                    status_emoji = "✅" if step_status == "success" else "❌"
                    status_text = "Success" if step_status == "success" else "Failed"
                    f.write(f"**{status_emoji} {status_text}**\n\n")
                    
                    # Screenshot
                    if step.screenshot_path:
                        screenshot_path = self.current_run_dir / step.screenshot_path
                        if screenshot_path.exists():
                            f.write(f"![Step {step_counter}]({step.screenshot_path})\n\n")
                    
                    f.write("---\n\n")
                
                # Final task validation result
                f.write("## Final Task Validation\n\n")
                if self.run_metadata.success is not None:
                    if self.run_metadata.success:
                        f.write("**✅ Task Validation: PASSED**\n\n")
                        f.write(f"**Reason:** {self.run_metadata.success_reason or 'Task completed successfully'}\n\n")
                    else:
                        f.write("**❌ Task Validation: FAILED**\n\n")
                        f.write(f"**Reason:** {self.run_metadata.success_reason or 'Task validation failed'}\n\n")
                    if self.run_metadata.error_details:
                        f.write(f"**Error Details:** {self.run_metadata.error_details}\n\n")
                else:
                    f.write("**⚠️ Task Validation: Not Completed**\n\n")
                f.write("---\n\n")

    def _format_action(self, action: Dict[str, Any]) -> str:
        """Format action dictionary into human-readable string"""
        if not action:
            return "No action"
        
        action_type = action.get("action_type", "unknown")
        
        if action_type == "click":
            return f"click(x={action.get('x', '?')}, y={action.get('y', '?')})"
        elif action_type == "input_text":
            text = action.get("text", "")
            preview = text[:30] + "..." if len(text) > 30 else text
            return f"input_text('{preview}')"
        elif action_type == "swipe":
            return f"swipe({action.get('x0', '?')}, {action.get('y0', '?')} → {action.get('x1', '?')}, {action.get('y1', '?')})"
        elif action_type == "navigate_back":
            return "navigate_back()"
        elif action_type == "answer":
            return f"answer('{action.get('text', '')}')"
        else:
            return f"{action_type}({', '.join(f'{k}={v}' for k, v in action.items() if k != 'action_type')})"

    def _format_action_code(self, action: Dict[str, Any]) -> str:
        """Format action dictionary into code-style string for timeline"""
        if not action:
            return "No action"
        
        action_type = action.get("action_type", "unknown")
        
        if action_type == "click":
            if "index" in action:
                return f"click(index={action.get('index')})"
            else:
                return f"click(x={action.get('x', '?')}, y={action.get('y', '?')})"
        elif action_type == "input_text":
            text = action.get("text", "")
            if "index" in action:
                return f"type_text(text=\"{text}\", index={action.get('index')})"
            else:
                return f"type_text(text=\"{text}\")"
        elif action_type == "swipe":
            return f"swipe(x0={action.get('x0', '?')}, y0={action.get('y0', '?')}, x1={action.get('x1', '?')}, y1={action.get('y1', '?')})"
        elif action_type == "navigate_back":
            return "go_back()"
        elif action_type == "open_app":
            app_name = action.get("app_name", "")
            return f"open_app(text=\"{app_name}\")"
        elif action_type == "answer":
            return f"answer(text=\"{action.get('text', '')}\")"
        else:
            # Format as function call
            params = []
            for k, v in action.items():
                if k != "action_type":
                    if isinstance(v, str):
                        params.append(f"{k}=\"{v}\"")
                    else:
                        params.append(f"{k}={v}")
            return f"{action_type}({', '.join(params)})"

    def _format_tool_call_code(self, name: str, args: Any) -> str:
        """Format tool call into code-style string"""
        if not args:
            return f"{name}()"
        
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except:
                return f"{name}(text=\"{args}\")"
        
        if not isinstance(args, dict):
            return f"{name}({args})"
        
        # Format parameters
        params = []
        for k, v in args.items():
            if k == "intent":
                continue  # Skip intent in code display
            if isinstance(v, str):
                params.append(f"{k}=\"{v}\"")
            elif isinstance(v, (dict, list)):
                params.append(f"{k}={json.dumps(v)}")
            else:
                params.append(f"{k}={v}")
        
        if params:
            return f"{name}({', '.join(params)})"
        else:
            return f"{name}()"

    def get_run_data(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve all data for a run (current or specified).

        Args:
            run_id: Optional run ID to load historical data

        Returns:
            Dictionary containing all run data
        """
        if run_id:
            run_dir = self.base_log_dir / run_id
        else:
            run_dir = self.current_run_dir

        if not run_dir or not run_dir.exists():
            return {}

        data = {}

        # Load metadata
        metadata_path = run_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                data["metadata"] = json.load(f)

        # Load success.json
        success_path = run_dir / "success.json"
        if success_path.exists():
            with open(success_path, "r") as f:
                data["success"] = json.load(f)

        # Load steps.json (unified)
        steps_path = run_dir / "steps.json"
        if steps_path.exists():
            with open(steps_path, "r") as f:
                data["steps"] = json.load(f)

        # Load planner steps
        planner_path = run_dir / "planner_steps.json"
        if planner_path.exists():
            with open(planner_path, "r") as f:
                data["planner_steps"] = json.load(f)

        # Load executor sessions
        executor_path = run_dir / "executor_sessions.json"
        if executor_path.exists():
            with open(executor_path, "r") as f:
                data["executor_sessions"] = json.load(f)

        return data
