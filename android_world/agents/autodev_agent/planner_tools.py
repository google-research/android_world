def tap(intent: str):
    """
    Declare an intent to tap a specific UI element on the current screen.

    This is a semantic instruction only — no coordinates should be provided.
    The executor will analyze the screenshot and determine the correct pixel
    location to perform the tap.

    Examples of `intent`:
      - "login button"
      - "search icon"
      - "cart tab"
      - "menu hamburger"
      - "the blue continue button at the bottom"

    Parameters:
        intent (str): A short natural-language description of the element
                      the agent should tap.
    """
    pass


def swipe(intent: str):
    """
    Declare an intent to perform a swipe gesture based on semantic direction
    or purpose.

    The executor will translate the high-level intent into a concrete swipe
    vector using the screenshot.

    Examples of `intent`:
      - "scroll down"
      - "scroll up to reveal hidden content"
      - "swipe left to switch tab"
      - "swipe right to view next item"

    Parameters:
        intent (str): A natural-language description of the direction or
                      purpose of the swipe.
    """
    pass


def wait(seconds: int):
    """
    Declare an intent to wait for a specified duration before performing any
    further actions.

    This is useful when the UI is transitioning, animations are occurring,
    or network responses require time.

    Parameters:
        seconds (int): Number of seconds the agent should pause.
    """
    pass


def open_app(app_name: str):
    """
    Declare an intent to open an installed application on the device.

    The executor is responsible for locating the app icon on the home screen,
    app drawer, or search interface, and performing the necessary taps.

    Examples:
      - "YouTube"
      - "Gmail"
      - "Settings"

    Parameters:
        app_name (str): The exact name or closest recognizable name of the app.
    """
    pass


def go_back():
    """
    Declare an intent to navigate back to the previous screen.

    The executor will decide whether to press the system back button or
    another UI-specific back element, depending on the visible screen.
    """
    pass


def clear_text():
    """
    Declare an intent to clear the text in the currently focused input field.

    The executor will determine how to clear the text (e.g., selecting all and
    deleting, tapping the clear icon, or issuing repeated delete commands).
    """
    pass


def type_text(text: str, intent: str):
    """
    Declare an intent to type a specific string into a specific semantic field.

    The planner should describe *what* to type and *where*, and the executor
    determines the correct UI element and performs typing actions.

    Examples:
        text="hello", intent="search bar"
        text="john@example.com", intent="email field"

    Parameters:
        text (str): The exact text to be entered.
        intent (str): A natural-language description of the input field
                      (e.g., "username box", "search bar", "comment field").
    """
    pass


def answer(text: str):
    """
    Provide a natural-language answer or final statement to the user or system.

    This is not a UI action — it represents verbal or textual reasoning output
    from the agent (e.g., answering a question in the Android World task).

    The executor does not process this; instead, the agent returns it as the
    final answer for the environment to evaluate.

    Parameters:
        text (str): The answer the agent wants to output.
    """
    pass


def finish_task(success: bool):
    """
    Declare that the agent considers the task complete and wishes to terminate.

    If success=True, the agent believes it has achieved the required goal.
    If success=False, the agent is unable to complete the task.

    This will signal the environment to end the episode.

    Parameters:
        success (bool): Whether the agent believes the task was completed.
    """
    pass
