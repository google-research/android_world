import json
from typing import Any, ClassVar, Dict, List


class TodoList:
    # OpenAI tool schema
    TODO_LIST_DESCRIPTION = """
    Use this tool to create and manage a structured task list for your current task session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user.
    Without this, you will run into endless loops.

    ## When to Use This Tool
    Use this tool proactively in these scenarios:

    1. Complex multi-step tasks - When a task requires 3 or more distinct steps or actions
    2. Non-trivial and complex tasks - Tasks that require careful planning or multiple operations
    3. User explicitly requests todo list - When the user directly asks you to use the todo list
    4. User provides multiple tasks - When users provide a list of things to be done (numbered or comma-separated)
    5. After receiving new instructions - Immediately capture user requirements as todos
    6. When you start working on a task - Mark it as in_progress BEFORE beginning work. Ideally you should only have one todo as in_progress at a time
    7. After completing a task - Mark it as completed and add any new follow-up tasks discovered during implementation

    ## When NOT to Use This Tool

    Skip using this tool when:
    1. There is only a single, straightforward task
    2. The task is trivial and tracking it provides no organizational benefit
    3. The task can be completed in less than 3 trivial steps
    4. The task is purely conversational or informational

    NOTE that you should not use this tool if there is only one trivial task to do. In this case you are better off just doing the task directly.

    ## Examples of When to Use the Todo List

    User: I want to copy paste my data from app A into app B.

    *Creates todo list with the following items:*
    1. Open app A.
    2. Find the relevant data.
    3. Make a note of the data to copy and make a Todo list item for it.
    4. Open app B.
    5. Find relevant place to paste data.
    6. Copy data from Todo list.
    """
    TODO_TOOL: ClassVar[Dict[str, Any]] = {
        "name": "update_todos",
        "description": "Replace the current todo list with the provided list.",
        "parameters": {
            "type": "object",
            "properties": {
                "todos": {
                    "description": TODO_LIST_DESCRIPTION,
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "content": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "id": {
                                "type": "string",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                            },
                        },
                        "required": ["content", "status", "priority", "id"],
                    },
                },
            },
            "required": ["todos"],
        },
    }

    def __init__(self, todos: List[Dict[str, Any]] | None = None) -> None:
        """
        Initialize the todo list. Optionally seed with an existing list.
        """
        self._todos: List[Dict[str, Any]] = todos or []

    # ----- Core API -----

    def update(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Replace the current todo list with the provided list.

        This is meant to be called with the `todos` from the tool call:
            args = json.loads(tool_call.function.arguments)
            todo_list.update(args["todos"])
        """
        valid_priorities = {"high", "medium", "low"}
        valid_statuses = {"pending", "in_progress", "completed"}

        cleaned: List[Dict[str, Any]] = []

        for idx, todo in enumerate(todos):
            try:
                tid = str(todo["id"])
                content = str(todo["content"]).strip()
                priority = str(todo["priority"])
                status = str(todo["status"])
            except KeyError as e:
                raise ValueError(
                    f"Todo at index {idx} is missing required field: {e}"
                ) from e

            if not content:
                raise ValueError(f"Todo {tid} has empty content")

            if priority not in valid_priorities:
                raise ValueError(f"Todo {tid} has invalid priority: {priority}")

            if status not in valid_statuses:
                raise ValueError(f"Todo {tid} has invalid status: {status}")

            cleaned.append(
                {
                    "id": tid,
                    "content": content,
                    "priority": priority,
                    "status": status,
                }
            )

        # Commit the new list
        self._todos = cleaned

        # Return something nice for the LLM as the tool result
        return {
            "success": True,
            "count": len(self._todos),
            "todos": self._todos,
        }

    def pretty_print(self) -> str:
        """
        Return a formatted string representation of the todo list.
        """
        if self.is_empty():
            return "📋 Todo List: Empty"

        # Group todos by status
        pending = [t for t in self._todos if t["status"] == "pending"]
        in_progress = [t for t in self._todos if t["status"] == "in_progress"]
        completed = [t for t in self._todos if t["status"] == "completed"]

        lines = ["📋 Todo List", "=" * 50]

        # In Progress section
        if in_progress:
            lines.append("\n🔄 IN PROGRESS:")
            for todo in in_progress:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[
                    todo["priority"]
                ]
                lines.append(f"  {priority_icon} [{todo['id']}] {todo['content']}")

        # Pending section
        if pending:
            lines.append("\n⏳ PENDING:")
            for todo in pending:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[
                    todo["priority"]
                ]
                lines.append(f"  {priority_icon} [{todo['id']}] {todo['content']}")

        # Completed section
        if completed:
            lines.append("\n✅ COMPLETED:")
            for todo in completed:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[
                    todo["priority"]
                ]
                lines.append(f"  {priority_icon} [{todo['id']}] {todo['content']}")

        # Summary
        lines.append("\n" + "=" * 50)
        lines.append(
            f"Total: {len(self._todos)} | Pending: {len(pending)} | In Progress: {len(in_progress)} | Completed: {len(completed)}"
        )

        return "\n".join(lines)

    def read(self) -> List[Dict[str, Any]]:
        """
        Return the current todo list.
        """
        return self._todos

    def is_empty(self) -> bool:
        return len(self._todos) == 0

    def get_system_reminder(self) -> str:
        sys_instruction = "<system_reminder>"
        if self.is_empty():
            sys_instruction += """\n This is a reminder that your todo list is currently empty. DO NOT mention this to the user explicitly
            because they are already aware. If you are working on tasks that would benefit from a todo list please use
            the TodoWrite tool to create one. If not, please feel free to ignore. Again do not mention this message
            to the user.\n"""
        else:
            sys_instruction += """This is the current state of the todolist. Continue to work on it, and make sure everything gets done.
            Add to it and update it if necessary.\n
            """

            sys_instruction += json.dumps(self.read())

        sys_instruction += "\n</system_reminder>"
        return sys_instruction

    # ----- Tool helpers -----

    @classmethod
    def get_tool(cls) -> Dict[str, Any]:
        """
        Return the OpenAI tool definition for this todo list.
        """
        return cls.TODO_TOOL

    def handle_tool_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience method to handle raw tool arguments dict from the model.

        Example:
            tool_call = choice.message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            result = todo_list.handle_tool_args(args)
        """
        todos = args.get("todos", [])
        return self.update(todos)
