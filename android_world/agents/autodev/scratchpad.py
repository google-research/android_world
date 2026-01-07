import json
from typing import Any, ClassVar, Dict, Optional


class Scratchpad:
    """Shared scratchpad storage for planner and executor to share data across sessions."""
    
    SCRATCHPAD_DESCRIPTION = """
    Use this tool to store and retrieve data in a shared scratchpad that persists across executor sessions.
    
    The scratchpad allows:
    - Storing extracted data (recipes, files, items) for later use
    - Tracking progress (items processed, duplicates found)
    - Sharing data between planner and executor
    
    Common use cases:
    - Extract recipe details and store for later creation in another app
    - Store list of items found while scrolling
    - Track duplicates found during scanning
    - Store file contents for merging or copying
    
    Keys follow the pattern PAD-1, PAD-2, PAD-3, etc. to avoid spelling mistakes.
    """
    
    CREATE_ITEM_TOOL: ClassVar[Dict[str, Any]] = {
        "name": "createItem",
        "description": "Store data in the shared scratchpad with a key (use PAD-1, PAD-2, etc. format) and title for identification.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Unique key following PAD-1, PAD-2, PAD-3 format (e.g., 'PAD-1', 'PAD-2'). Use sequential numbers to avoid spelling mistakes."
                },
                "title": {
                    "type": "string",
                    "description": "Human-readable title/description of what this data contains (e.g., 'Recipe Pasta Details', 'All Visible Items')"
                },
                "text": {
                    "type": "string",
                    "description": "The data content to store. Can be plain text or JSON string. For structured data, use JSON format."
                }
            },
            "required": ["key", "title", "text"]
        }
    }
    
    FETCH_ITEM_TOOL: ClassVar[Dict[str, Any]] = {
        "name": "fetchItem",
        "description": "Retrieve data from the shared scratchpad by key.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "The key of the data to retrieve (e.g., 'PAD-1', 'PAD-2')"
                }
            },
            "required": ["key"]
        }
    }
    
    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Initialize scratchpad with optional existing data."""
        self._data: Dict[str, Any] = data or {}
        self._next_pad_number = 1
    
    def create_item(self, key: str, title: str, text: str) -> Dict[str, Any]:
        """
        Store data in scratchpad.
        
        Args:
            key: Unique key (e.g., 'PAD-1', 'PAD-2')
            title: Human-readable title/description
            text: The data content (can be plain text or JSON string)
            
        Returns:
            Success status and the stored key
        """
        # Normalize key to uppercase
        normalized_key = key.upper()
        
        # Store with metadata
        self._data[normalized_key] = {
            "title": title,
            "text": text,
            "key": normalized_key
        }
        
        # Try to parse as JSON to validate, but store as-is
        try:
            json.loads(text)
            is_json = True
        except (json.JSONDecodeError, TypeError):
            is_json = False
        
        return {
            "success": True,
            "key": normalized_key,
            "title": title,
            "is_json": is_json
        }
    
    def fetch_item(self, key: str) -> Dict[str, Any]:
        """
        Read data from scratchpad.
        
        Args:
            key: The key of the data to retrieve (e.g., 'PAD-1')
            
        Returns:
            The stored data with title and text, or empty dict if key doesn't exist
        """
        normalized_key = key.upper()
        item = self._data.get(normalized_key)
        
        if item is None:
            return {
                "success": False,
                "error": f"Key '{normalized_key}' not found in scratchpad",
                "key": normalized_key
            }
        
        return {
            "success": True,
            "key": normalized_key,
            "title": item.get("title", ""),
            "text": item.get("text", "")
        }
    
    def get_all_keys(self) -> list[str]:
        """Get all scratchpad keys."""
        return sorted(list(self._data.keys()))
    
    def get_all(self) -> Dict[str, Any]:
        """Get all scratchpad data."""
        return self._data.copy()
    
    def get_system_reminder(self) -> str:
        """Get formatted scratchpad content for system instructions."""
        sys_instruction = "<system_reminder>"
        if not self._data:
            sys_instruction += """\n This is a reminder that your scratchpad is currently empty. DO NOT mention this to the user explicitly
            because they are already aware. If you need to store data for later use (e.g., extracted recipes, file contents, item lists),
            use createItem(key='PAD-1', title='[description]', text='[data]') to store it. If not, please feel free to ignore. 
            Again do not mention this message to the user.\n"""
        else:
            sys_instruction += """\n**SCRATCHPAD DATA AVAILABLE** - Use fetchItem(key) to retrieve stored data before processing items.\n
            Available scratchpad items:\n"""
            
            for key in sorted(self._data.keys()):
                item = self._data[key]
                title = item.get("title", "")
                sys_instruction += f"  - {key}: {title}\n"
            
            sys_instruction += "\nTo retrieve data, call fetchItem(key='PAD-X') where X is the number shown above.\n"
            sys_instruction += "Example: fetchItem(key='PAD-1') to get the first stored item.\n"
        
        sys_instruction += "\n</system_reminder>"
        return sys_instruction
    
    @classmethod
    def get_create_tool(cls) -> Dict[str, Any]:
        """Return the tool definition for creating items in scratchpad."""
        return cls.CREATE_ITEM_TOOL
    
    @classmethod
    def get_fetch_tool(cls) -> Dict[str, Any]:
        """Return the tool definition for fetching items from scratchpad."""
        return cls.FETCH_ITEM_TOOL
    
    def handle_create_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience method to handle raw tool arguments dict from the model.
        
        Example:
            tool_call = choice.message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            result = scratchpad.handle_create_args(args)
        """
        key = args.get("key", "")
        title = args.get("title", "")
        text = args.get("text", "")
        return self.create_item(key, title, text)
    
    def handle_fetch_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience method to handle raw tool arguments dict from the model.
        
        Example:
            tool_call = choice.message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            result = scratchpad.handle_fetch_args(args)
        """
        key = args.get("key", "")
        return self.fetch_item(key)
