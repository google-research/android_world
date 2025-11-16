"""Functions to create Android automation actions.

These functions are designed to be used as tool calls by an LLM to generate
properly formatted actions for various Android interactions.
"""

from typing import Optional

from android_world.env.json_action import JSONAction


def click(x: int, y: int) -> JSONAction:
    """Create a click action at the specified coordinates.

    Args:
        x: The x-coordinate of the click position on the screen.
        y: The y-coordinate of the click position on the screen.

    Example:
        >>> click(100, 200)
        # Performs a click at position (100, 200)
    """
    return JSONAction(action_type="click", x=x, y=y)


def double_tap(x: int, y: int) -> JSONAction:
    """Create a double-tap action at the specified coordinates.

    Args:
        x: The x-coordinate of the double-tap position on the screen.
        y: The y-coordinate of the double-tap position on the screen.

    Example:
        >>> double_tap(150, 300)
        # Performs a double-tap at position (150, 300)
    """
    return JSONAction(action_type="double_tap", x=x, y=y)


def long_press(x: int, y: int) -> JSONAction:
    """Create a long-press action at the specified coordinates.

    Args:
        x: The x-coordinate of the long-press position on the screen.
        y: The y-coordinate of the long-press position on the screen.

    Example:
        >>> long_press(200, 400)
        # Performs a long-press at position (200, 400)
    """
    return JSONAction(action_type="long_press", x=x, y=y)


def scroll(
    direction: str, x: Optional[int] = None, y: Optional[int] = None
) -> JSONAction:
    """Create a scroll action in the specified direction.

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

    return JSONAction(action_type="scroll", direction=direction, x=x, y=y)


def swipe(
    direction: str, x: Optional[int] = None, y: Optional[int] = None
) -> JSONAction:
    """Create a swipe action in the specified direction.

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

    return JSONAction(action_type="swipe", direction=direction, x=x, y=y)


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
    return JSONAction(
        action_type="input_text",
        text=text,
        x=x,
        y=y,
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


def keycode_action(
    keycode: str, x: Optional[int] = None, y: Optional[int] = None
) -> JSONAction:
    """Create a keycode action for complex UI interactions.

    Keycode actions are necessary for interacting with complex UI elements
    (like large textareas) that can't be accessed or controlled by simply
    tapping, ensuring precise control over navigation and selection.

    Args:
        keycode: The Android keycode to send. Must start with 'KEYCODE_'.
                Common examples: 'KEYCODE_DPAD_UP', 'KEYCODE_DPAD_DOWN',
                'KEYCODE_TAB', 'KEYCODE_ESCAPE', 'KEYCODE_DEL'.
        x: Optional x-coordinate for the action.
        y: Optional y-coordinate for the action.

    Raises:
        ValueError: If keycode doesn't start with 'KEYCODE_'.

    Example:
        >>> keycode_action('KEYCODE_TAB')
        # Sends a TAB key press

        >>> keycode_action('KEYCODE_DPAD_DOWN', x=100, y=200)
        # Sends a DPAD down key press at position (100, 200)
    """
    if not keycode.startswith("KEYCODE_"):
        raise ValueError(f"Keycode must start with 'KEYCODE_', got: {keycode}")

    # Since there's no specific action_type for keycode in the original class,
    # we'll need to determine the most appropriate action_type or extend the class
    # For now, using a generic action with keycode parameter
    return JSONAction(action_type="click", keycode=keycode, x=x, y=y)


# Convenience functions for common patterns


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


def swipe_left(x: Optional[int] = None, y: Optional[int] = None) -> JSONAction:
    """Convenience function for swiping left.

    Args:
        x: Optional x-coordinate for swipe origin.
        y: Optional y-coordinate for swipe origin.
    """
    return swipe("left", x, y)


def swipe_right(x: Optional[int] = None, y: Optional[int] = None) -> JSONAction:
    """Convenience function for swiping right.

    Args:
        x: Optional x-coordinate for swipe origin.
        y: Optional y-coordinate for swipe origin.
    """
    return swipe("right", x, y)


def scroll_up(x: Optional[int] = None, y: Optional[int] = None) -> JSONAction:
    """Convenience function for scrolling up.

    Args:
        x: Optional x-coordinate for scroll origin.
        y: Optional y-coordinate for scroll origin.
    """
    return scroll("up", x, y)


def scroll_down(x: Optional[int] = None, y: Optional[int] = None) -> JSONAction:
    """Convenience function for scrolling down.

    Args:
        x: Optional x-coordinate for scroll origin.
        y: Optional y-coordinate for scroll origin.
    """
    return scroll("down", x, y)


def done(success: bool):
    """Report the completion status of an action.

    This function serves as a callback or notification mechanism to indicate
    whether the originally initiated action completed successfully or failed.
    Use this when you are done, or have no way to proceed.

    Args:
        success: A boolean indicating the outcome of the action.
                 True if the action succeeded, False if it failed.

    """
