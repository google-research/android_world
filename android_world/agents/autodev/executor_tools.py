"""Functions to create Android automation actions.

These functions are designed to be used as tool calls by an LLM to generate
properly formatted actions for various Android interactions.
"""

from typing import Optional

from android_world.env.json_action import JSONAction

# Global scale factor for coordinate scaling
SCALE = 0.4


def click(x: int, y: int) -> JSONAction:
    """Create a click action at the specified coordinates.

    Args:
        x: The x-coordinate of the click position on the screen.
        y: The y-coordinate of the click position on the screen.

    Example:
        >>> click(100, 200)
        # Performs a click at position (100, 200)
    """
    return JSONAction(action_type="click", x=int(int(x) / SCALE), y=int(int(y) / SCALE))


def double_tap(x: int, y: int) -> JSONAction:
    """Create a double-tap action at the specified coordinates.
    You may use this to perform a zoom in gesture on a map or an image.

    Args:
        x: The x-coordinate of the double-tap position on the screen.
        y: The y-coordinate of the double-tap position on the screen.

    Example:
        >>> double_tap(150, 300)
        # Performs a double-tap at position (150, 300)
    """
    return JSONAction(
        action_type="double_tap", x=int(int(x) / SCALE), y=int(int(y) / SCALE)
    )


def long_press(x: int, y: int) -> JSONAction:
    """Create a long-press action at the specified coordinates.

    Args:
        x: The x-coordinate of the long-press position on the screen.
        y: The y-coordinate of the long-press position on the screen.

    Example:
        >>> long_press(200, 400)
        # Performs a long-press at position (200, 400)
    """
    return JSONAction(
        action_type="long_press", x=int(int(x) / SCALE), y=int(int(y) / SCALE)
    )


def scroll(
    direction: str, x: Optional[int] = None, y: Optional[int] = None
) -> JSONAction:
    """Create a scroll action in the specified direction.
    In order to scroll a tiny bit, use swipe in the inverse direction instead.
    Args:
        direction: The scroll direction. Must be one of: 'up', 'down', 'left', 'right'.
        x: Optional x-coordinate for the scroll origin. If not provided, scrolls from center.
        y: Optional y-coordinate for the scroll origin. If not provided, scrolls from center.





    Raises:
        ValueError: If direction is not one of the valid scroll directions.

    Example:
        >>> scroll('down')
        # Scrolls down from center of screen

        >>> scroll('up', x=300, y=500)
        # Scrolls up from position (300, 500)
    """
    valid_directions = ("up", "down", "left", "right")
    if direction not in valid_directions:
        raise ValueError(
            f"Direction must be one of {valid_directions}, got: {direction}"
        )

    scaled_x = int(int(x) / SCALE) if x is not None else None
    scaled_y = int(int(y) / SCALE) if y is not None else None
    return JSONAction(action_type="scroll", direction=direction, x=scaled_x, y=scaled_y)


def swipe(
    direction: str, x: Optional[int] = None, y: Optional[int] = None
    ) -> JSONAction:
    """Create a swipe action in the specified direction.
    You may scroll tiny amounts by using swipe instead.
    For example, to scroll down, swipe the screen up from the upper half of the screen.
    Args:
        direction: The swipe direction. Must be one of: 'up', 'down', 'left', 'right'.
        x: Optional x-coordinate for the swipe origin. If not provided, swipes from center.
        y: Optional y-coordinate for the swipe origin. If not provided, swipes from center.

    Raises:
        ValueError: If direction is not one of the valid swipe directions.

    Example:
        >>> swipe('left')
        # Swipes left from center of screen

        >>> swipe('right', x=100, y=200)
        # Swipes right from position (100, 200)
    """
    valid_directions = ("up", "down", "left", "right")
    if direction not in valid_directions:
        raise ValueError(
            f"Direction must be one of {valid_directions}, got: {direction}"
        )
    
    scaled_x = int(int(x) / SCALE) if x is not None else None
    scaled_y = int(int(y) / SCALE) if y is not None else None
    return JSONAction(action_type="swipe", direction=direction, x=scaled_x, y=scaled_y)


def swipe_coords(
    start_x: int, start_y: int, end_x: int, end_y: int
) -> JSONAction:
    """Create a swipe action with explicit start and end coordinates.
    
    This gives precise control over the swipe path. The coordinates are in logical
    screen space and will be scaled appropriately.
    
    Args:
        start_x: X coordinate where the swipe starts
        start_y: Y coordinate where the swipe starts
        end_x: X coordinate where the swipe ends
        end_y: Y coordinate where the swipe ends
    
    Example:
        >>> swipe_coords(100, 1200, 800, 1200)
        # Swipes horizontally from (100, 1200) to (800, 1200)
    """
    scaled_start_x = int(int(start_x) / SCALE)
    scaled_start_y = int(int(start_y) / SCALE)
    scaled_end_x = int(int(end_x) / SCALE)
    scaled_end_y = int(int(end_y) / SCALE)
    
    action = JSONAction(
        action_type="swipe", 
        x=scaled_start_x,
        y=scaled_start_y,
    )
    action.end_x = scaled_end_x
    action.end_y = scaled_end_y
    return action


def input_text(
    text: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    clear_text: bool = False,
) -> JSONAction:
    """Create an input text action to type text into a field.

    Args:
        text: The text string to input.
        x: Optional x-coordinate of the text field to click before typing.
        y: Optional y-coordinate of the text field to click before typing.
        clear_text: Whether to clear existing text in the field before typing.
                   Defaults to False.

    Example:
        >>> input_text("Hello World")
        # Types "Hello World" into the currently focused field

        >>> input_text("user@example.com", x=200, y=300, clear_text=True)
        # Clicks at (200, 300), clears the field, then types the email
    """
    scaled_x = int(int(x) / SCALE) if x is not None else None
    scaled_y = int(int(y) / SCALE) if y is not None else None
    return JSONAction(
        action_type="input_text",
        text=text,
        x=scaled_x,
        y=scaled_y,
        clear_text=clear_text if clear_text else None,
    )


def keyboard_enter() -> JSONAction:
    """Create a keyboard enter/return key press action.

    Example:
        >>> keyboard_enter()
        # Presses the enter key
    """
    return JSONAction(action_type="keyboard_enter")


def navigate_back() -> JSONAction:
    """Create a navigate back action (Android back button).

    Example:
        >>> navigate_back()
        # Presses the Android back button
    """
    return JSONAction(action_type="navigate_back")


def navigate_home() -> JSONAction:
    """Create a navigate home action (Android home button).

    Example:
        >>> navigate_home()
        # Presses the Android home button to go to home screen
    """
    return JSONAction(action_type="navigate_home")


def open_app(app_name: str) -> JSONAction:
    """Create an open app action to launch a specific application.

    Args:
        app_name: The name of the application to open (case-insensitive).

    Example:
        >>> open_app("Settings")
        # Opens the Settings app

        >>> open_app("Google Chrome")
        # Opens Google Chrome browser
    """
    return JSONAction(action_type="open_app", app_name=app_name)


def wait() -> JSONAction:
    """Create a wait action to pause execution.

    This is useful for waiting for UI elements to load or animations to complete.

    Example:
        >>> wait()
        # Pauses execution temporarily
    """
    return JSONAction(action_type="wait")


def tap(x: int, y: int) -> JSONAction:
    """Alias for click() - create a tap action at the specified coordinates.

    Args:
        x: The x-coordinate of the tap position.
        y: The y-coordinate of the tap position.

    Example:
        >>> tap(250, 500)
        # Taps at position (250, 500)
    """
    return click(x, y)


def type_text(text: str, clear_first: bool = False) -> JSONAction:
    """Simplified text input without coordinates.

    Use this when the text field is already focused or selected.

    Args:
        text: The text to type.
        clear_first: Whether to clear existing text before typing.

    Example:
        >>> type_text("Hello")
        # Types "Hello" into the currently focused field
    """
    return input_text(text, clear_text=clear_first)


def swipe_up(x: Optional[int] = None, y: Optional[int] = None) -> JSONAction:
    """Convenience function for swiping up.

    Args:
        x: Optional x-coordinate for swipe origin.
        y: Optional y-coordinate for swipe origin.
    """
    return swipe("up", x, y)


def swipe_down(x: Optional[int] = None, y: Optional[int] = None) -> JSONAction:
    """Convenience function for swiping down.

    Args:
        x: Optional x-coordinate for swipe origin.
        y: Optional y-coordinate for swipe origin.
    """
    return swipe("down", x, y)


def extracted_data(data: str):
    """
    This function is a callback to return extracted data.
    If you have been tasked with extracting data from a screen, you may use this function to return that data.
    Please send the data in a structured format that can be effectively used.
    """


def report(notes: str):
    """Reports what it has achieved of current conversation objectives.

    This function serves as a callback or notification mechanism to indicate
    the overall status and summary of the performed actions on the originally stated goal.

    It will help the planner in setting future objectives, and tracking the status
    of the goals.

    Use this when you have achieved what you set out to achieve or don't have a way to proceed.

    Args:
        notes: Succint notes on everything that was done and observed in this flow.

    """
