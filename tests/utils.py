import os
from unittest.mock import patch, MagicMock
from src.utils.code_management import (
    extract_code_from_answer,
    get_script,
    check_syntax,
    validate_code_safety,
)


def test_extract_code_from_answer():
    # Test with Python code block
    content = """Here is some code:
    ```python
    print("Hello, World!")
    ```
    """
    result = extract_code_from_answer(content)
    assert result.group(1) == 'print("Hello, World!")'

    # Test with non-Python code block
    content = """Here is some code:
    ```
    print("Hello, World!")
    ```
    """
    result = extract_code_from_answer(content)
    assert result.group(1) == 'print("Hello, World!")'

    # Test with no code block
    content = "Here is some text without code block."
    result = extract_code_from_answer(content)
    assert result is None


@patch("streamlit.session_state", new_callable=MagicMock)
def test_get_script(mock_session_state):
    response = {
        "content": """Here is some code:
        ```python
        print("Hello, World!")
        ```
        """
    }
    with patch(
        "tempfile.NamedTemporaryFile",
        lambda delete, suffix: open("temp_test_file.py", "w"),
    ):
        result = get_script(response)
        assert result is True
        assert os.path.exists("temp_test_file.py")
        with open("temp_test_file.py", "r") as file:
            content = file.read()
            assert content == 'print("Hello, World!")'
        os.remove("temp_test_file.py")

    response = {"content": "Here is some text without code block."}
    result = get_script(response)
    assert result is False


def test_check_syntax():
    valid_code = 'print("Hello, World!")'
    invalid_code = 'print("Hello, World!"'

    is_valid, error = check_syntax(valid_code)
    assert is_valid is True
    assert error == ""

    is_valid, error = check_syntax(invalid_code)
    assert is_valid is False
    assert "was never closed" in error


def test_validate_code_safety():
    safe_code = 'print("Hello, World!")'
    unsafe_code = "eval(\"print('Hello, World!')\")"

    is_safe, error = validate_code_safety(safe_code)
    assert is_safe is True
    assert error == ""

    is_safe, error = validate_code_safety(unsafe_code)
    assert is_safe is False
    assert "Disallowed function call detected: eval" in error
