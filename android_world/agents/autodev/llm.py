"""Simple LiteLLM wrapper for AutoDev agent."""

import base64
import os
from io import BytesIO
from typing import Any, Dict, List, Optional, TypedDict, Union

import litellm
import numpy as np
from dotenv import load_dotenv
from PIL import Image

from .todo_list import TodoList

load_dotenv()


class ToolCall(TypedDict):
    """Type for tool call structure."""

    id: str
    type: str
    function: Dict[str, Any]  # Contains 'name' and 'arguments'


class ChatResponse(TypedDict):
    """Response from chat method containing content and tool calls."""

    content: Optional[str]
    tool_calls: Optional[List[ToolCall]]


class AutoDevLLM:
    """Simple LLM wrapper with conversation history and tool calls."""

    def __init__(
        self,
        model: str = "gpt-4",
        system_prompt: str = "",
        todo_list_enabled: bool = False,
    ) -> None:
        self.model = model
        self.messages: List[Dict[str, Any]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        self.todo_list_enabled = todo_list_enabled
        self.todo_list = TodoList()

    def chat(
        self,
        user_message: Optional[str],
        screenshot: np.ndarray,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ChatResponse:
        """Send a message and get response, optionally with tool calls."""
        # Prepare user message content
        tools_for_call = list(tools) if tools is not None else []

        parts: List[Dict[str, Any]] = []

        if user_message:  # only add if not None/empty
            parts.append({"type": "text", "text": user_message})
        image_data = self._encode_image(screenshot)
        parts.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_data}",
                    # you probably don't need 'format' here, the data URL covers it
                },
            }
        )
        if self.todo_list_enabled:
            parts.append({"type": "text", "text": self.todo_list.get_system_reminder()})
        self.messages.append({"role": "user", "content": parts})

        kwargs: Dict[str, Any] = {"model": self.model, "messages": self.messages}
        if self.todo_list_enabled:
            tools_for_call.append(TodoList.get_tool())
        if tools_for_call:
            wrapped_tools = []
            for t in tools_for_call:
                wrapped_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": t["name"],
                            "description": t.get("description", ""),
                            "parameters": t.get(
                                "parameters", {"type": "object", "properties": {}}
                            ),
                        },
                    }
                )
            tools_for_call = wrapped_tools  # replace original
            kwargs["tools"] = tools_for_call
            kwargs["tool_choice"] = "auto"

        response = litellm.completion(**kwargs)
        assistant_message = response.choices[0].message

        # Extract content and tool_calls
        content = assistant_message.content

        # Handle both legacy function_call and new tool_calls format
        tool_calls = getattr(assistant_message, "tool_calls", None)

        # Add to message history
        self.messages.append(
            {
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls,
            }
        )

        # Remove image blocks from message history after API call
        self._remove_image_blocks_from_history()

        # Return just the content and tool_calls
        return ChatResponse(content=content, tool_calls=tool_calls)

    def add_tool_result(self, tool_call_id: str, result: str) -> None:
        """Add tool execution result to conversation."""
        self.messages.append(
            {
                "role": "tool",
                "type": "function_call_output",
                "tool_call_id": tool_call_id,
                "content": result,
            }
        )

    def _remove_image_blocks_from_history(self) -> None:
        """Remove image blocks from message history to save memory."""
        for message in self.messages:
            if message.get("role") == "user" and isinstance(
                message.get("content"), list
            ):
                # Filter out image_url blocks, keep only text blocks
                message["content"] = [
                    part
                    for part in message["content"]
                    if part.get("type") != "image_url"
                ]

    def clear_history(self) -> None:
        """Clear conversation history but keep system prompt."""
        system_msg = None
        if self.messages and self.messages[0]["role"] == "system":
            system_msg = self.messages[0]
        self.messages = [system_msg] if system_msg else []

    def _encode_image(self, image: np.ndarray) -> str:
        """
        Encode numpy array image to base64 string for LLM API.

        Args:
            image: Image as numpy array

        Returns:
            Base64 encoded image string
        """
        # Convert numpy array to PIL Image
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        pil_image = Image.fromarray(image)

        # Convert to bytes
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        # Encode to base64
        return base64.b64encode(image_bytes).decode("utf-8")
