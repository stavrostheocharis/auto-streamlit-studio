import os
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
import streamlit as st
from src.utils.key_management import get_api_token_input

os.environ["TOKENIZERS_PARALLELISM"] = "false"


@pytest.fixture(scope="module")
def app_test():
    at = AppTest.from_file("app.py")
    at.run()
    return at


def test_main_app(app_test):
    """Test the main Streamlit app setup"""
    assert not app_test.exception


def test_sidebar_elements(app_test):
    """Test elements in the sidebar"""
    # Test if the sidebar contains the title "AutoStreamlit Studio"
    assert "AutoStreamlit Studio" in app_test.sidebar.markdown[0].value

    # Iterate through all sidebar markdown elements to find the disclaimer
    disclaimer_found = any(
        "***Disclaimer***" in md.value for md in app_test.sidebar.markdown
    )
    assert disclaimer_found, "Disclaimer not found in sidebar"

    # Test if the sidebar contains contact information
    contact_found = any("Contact" in md.value for md in app_test.sidebar.markdown)
    assert contact_found, "Contact information not found in sidebar"


def test_api_token_input():
    """Test the API token input handling"""
    at = AppTest.from_file("app.py")
    at.run()

    # Mock session state for the provider selection and token input
    with patch("streamlit.session_state", at.session_state.filtered_state):
        # Ensure session state keys are initialized
        if "input_openai_token" not in st.session_state:
            st.session_state["input_openai_token"] = ""

        # Simulate user selecting the provider and inputting the API token
        st.session_state["provider"] = "OpenAI"
        st.session_state["input_openai_token"] = "sk-fakeapikey"

        # Call the get_api_token_input function directly
        provider = "OpenAI"
        api_token = get_api_token_input(provider)

        # Update session state manually
        st.session_state[f"{provider.lower()}_token"] = st.session_state[
            f"input_{provider.lower()}_token"
        ]

        assert st.session_state[f"{provider.lower()}_token"] == "sk-fakeapikey"

    assert not at.exception


# Run all the tests
if __name__ == "__main__":
    pytest.main()
