"""Reusable actions for web Page Objects."""
from pathlib import Path


def fill_input(element, value, clear=True):
    """Fill a text input and return the supplied page element."""
    if clear:
        element.clear()
    element.text = value
    return element


def login(username_input, password_input, submit_button, username, password):
    """Fill credentials and submit a standard login form."""
    fill_input(username_input, username)
    fill_input(password_input, password)
    submit_button.click()
    return submit_button


def upload_file(file_input, file_path):
    """Upload a local file through an ``input[type=file]`` page element."""
    path = Path(file_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Upload file was not found: {path}")

    file_input.text = str(path.resolve())
    return file_input


def assert_text(element, expected_text, contains=False):
    """Assert a page element's text and return its actual value."""
    actual_text = element.text
    matches = expected_text in actual_text if contains else actual_text == expected_text
    if not matches:
        comparison = "contain" if contains else "equal"
        raise AssertionError(
            f"Expected element text to {comparison} {expected_text!r}, got {actual_text!r}."
        )
    return actual_text