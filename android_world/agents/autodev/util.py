import inspect
from typing import Any, Callable, Dict, List

from litellm.utils import function_to_dict

from android_world.agents.autodev import executor_tools, planner_tools
from android_world.agents.autodev.llm import ToolCall


def get_all_planner_tools_dict() -> List[Dict[str, Any]]:
    """Convert all functions from planner_tools module to dictionary format."""
    return [
        function_to_dict(func)
        for name, func in inspect.getmembers(planner_tools, inspect.isfunction)
        if not name.startswith("_")
    ]


def get_all_executor_tools_dict() -> List[Dict[str, Any]]:
    """Convert all functions from executor_tools module to dictionary format."""
    return [
        function_to_dict(func)
        for name, func in inspect.getmembers(executor_tools, inspect.isfunction)
        if not name.startswith("_")
    ]


def get_executor_registry() -> Dict[str, Callable]:
    """
    Returns a dict mapping function names to the actual function objects
    from the given module. Skips private functions (starting with '_').
    """
    return {
        name: func
        for name, func in inspect.getmembers(executor_tools, inspect.isfunction)
        if not name.startswith("_")
    }


def tool_call_to_query(tool_call: ToolCall) -> str:
    """
    Convert a tool call from the planning LLM into a natural language prompt
    for the executor LLM to perform the concrete action.
    """
    function_name = tool_call["function"]["name"]
    arguments = tool_call["function"].get("arguments", {})

    # Parse arguments if they're a JSON string
    if isinstance(arguments, str):
        import json

        arguments = json.loads(arguments)

    # Map each tool to an appropriate executor prompt
    if function_name == "tap":
        intent = arguments.get("intent", "")
        return f"Locate and tap on the {intent} on the current screen. Analyze the screenshot to find the exact coordinates of this element and perform a tap gesture."

    elif function_name == "swipe":
        intent = arguments.get("intent", "")
        return f"Perform a swipe gesture to {intent}. Analyze the current screen and determine the appropriate start and end coordinates for this swipe action."

    elif function_name == "swipe_coords":
        start_x = arguments.get("start_x", 0)
        start_y = arguments.get("start_y", 0)
        end_x = arguments.get("end_x", 0)
        end_y = arguments.get("end_y", 0)
        intent = arguments.get("intent", "")
        return f"Perform a swipe gesture from coordinates ({start_x}, {start_y}) to ({end_x}, {end_y}). {intent}"

    elif function_name == "scroll":
        intent = arguments.get("intent", "")
        base_query = f"Perform a scroll gesture to {intent}. Analyze the current screen and determine the appropriate coordinates for this scroll action."
        return base_query

    elif function_name == "wait":
        seconds = arguments.get("seconds", 1)
        return f"Wait for {seconds} second{'s' if seconds != 1 else ''} before proceeding to the next action. No interaction required."

    elif function_name == "open_app":
        app_name = arguments.get("app_name", "")
        return f"Open the '{app_name}' application. Navigate to the home screen or app drawer if needed, locate the {app_name} app icon, and tap on it to launch the application."

    elif function_name == "go_back":
        return "Navigate back to the previous screen using the system back button or an appropriate back UI element visible on the screen."

    elif function_name == "clear_text":
        return "Clear all text from the currently focused input field. Select all text and delete it, or use the clear button if available."

    elif function_name == "type_text":
        text = arguments.get("text", "")
        intent = arguments.get("intent", "current field")
        return f"First, locate and tap on the {intent} to focus it. Then type the following text exactly: '{text}'"

    else:
        # Fallback for unknown tool types
        args_str = ", ".join([f"{k}={v}" for k, v in arguments.items()])
        return f"Execute {function_name} with parameters: {args_str}"
