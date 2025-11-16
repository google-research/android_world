"""Simple LiteLLM wrapper for AutoDev agent."""

import base64
from io import BytesIO
from typing import Any, Dict, List, Optional, TypedDict, Union

import litellm
import numpy as np
from PIL import Image


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

    def __init__(self, model: str = "gpt-4", system_prompt: str = "") -> None:
        self.model = model
        self.messages: List[Dict[str, Any]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def chat(
        self,
        user_message: Optional[str],
        screenshot: Optional[np.ndarray] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ChatResponse:
        """Send a message and get response, optionally with tool calls."""
        # Prepare user message content
        content: Union[str, List[Dict[str, Any]], None] = user_message

        if screenshot is not None:
            # Convert screenshot to base64 for vision models
            image_data = self._encode_image(screenshot)
            content = [
                {"type": "text", "text": user_message},
                {"type": "image", "image": image_data},
            ]

        if content is not None:
            self.messages.append({"role": "user", "content": content})

        kwargs: Dict[str, Any] = {"model": self.model, "messages": self.messages}

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = litellm.completion(**kwargs)
        assistant_message = response.choices[0].message

        # Extract content and tool_calls
        content = assistant_message.content
        tool_calls = getattr(assistant_message, "tool_calls", None)

        # Add to message history
        self.messages.append(
            {
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls,
            }
        )

        # Return just the content and tool_calls
        return ChatResponse(content=content, tool_calls=tool_calls)

    def add_tool_result(self, tool_call_id: str, result: str) -> None:
        """Add tool execution result to conversation."""
        self.messages.append(
            {"role": "tool", "tool_call_id": tool_call_id, "content": result}
        )

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
