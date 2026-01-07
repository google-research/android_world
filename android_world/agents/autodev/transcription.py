"""Screen transcription utility using Haiku for pre-transcribing screens."""

import base64
from io import BytesIO
from typing import Optional

import litellm
import numpy as np
from PIL import Image


def transcribe_screen(screenshot: np.ndarray, model: str = "gemini/gemini-3-pro-preview") -> Optional[str]:
    """Transcribe text content from a screenshot using Haiku.
    
    Args:
        screenshot: Screenshot as numpy array
        model: Model to use for transcription (default: Haiku)
    
    Returns:
        Transcribed text content, or None if transcription fails
    """
    try:
        # Convert numpy array to PIL Image
        if screenshot.dtype != np.uint8:
            screenshot = (screenshot * 255).astype(np.uint8)
        
        pil_image = Image.fromarray(screenshot)
        
        # Convert to base64
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        
        # Create messages for transcription
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcribe all text visible on this screen. Include all UI elements, labels, buttons, text fields, and any other readable content and mention them as icons , buttons, text fields, etc. Be thorough and complete."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }
        ]
        
        # Call Haiku for transcription
        response = litellm.completion(
            model=model,
            messages=messages,
            max_tokens=2000,
        )
        
        transcription = response.choices[0].message.content
        return transcription.strip() if transcription else None
        
    except Exception as e:
        print(f"⚠️  Transcription error: {e}")
        return None

