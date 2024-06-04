import streamlit as st
import os
import sys
import toml
from versioning import display_version_control
from utils import (
    get_script,
    generate_arctic_response,
    clear_chat_history,
    delete_temp_file,
    execute_user_code,
    display_code_templates,
)
import time
import uuid
from code_editor import display_code_editor
from session_handler import initialize_session

# App title
st.set_page_config(page_title="Auto-streamlit", page_icon="🤖", layout="wide")
info = toml.load("info.toml")


initialize_session()


if "rerun" not in st.session_state.keys():
    st.session_state.rerun = False


def api_token_input():
    if "REPLICATE_API_TOKEN" in st.secrets:
        print("Replicate API token found in secrets.")
    else:
        replicate_api = st.text_input("Enter Replicate API token:", type="password")
        if not (replicate_api.startswith("r8_") and len(replicate_api) == 40):
            st.warning("Please enter your Replicate API token.", icon="⚠️")
            st.markdown(
                "**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one."
            )
        os.environ["REPLICATE_API_TOKEN"] = replicate_api


def display_main_sidebar_ui():
    with st.sidebar:
        st.title("Auto-streamlit")
        tool_description = info["tool_description"]

        with st.expander("About Auto-Streamlit"):
            st.title(tool_description["title"])
            st.markdown(tool_description["description"])

        with st.expander("How to Use"):
            st.markdown(
                """
                1. Enter your requirements in the chat input box.
                2. The assistant will generate a Streamlit script based on your input.
                3. You can download, edit, or run the generated script.
                4. Use the 'Clear chat history' button to delete the memory of previous chats.
                5. Use the 'Delete app file' button to delete the current created app.
            """
            )

        api_token_input()


if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi., I'm your personal Streamlit assistant, a new intelligent assistant to help you create automatically streamlit apps! What do you want to build?",
        }
    ]


def generate_response_if_needed():
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = generate_arctic_response()
            full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
        created_file = get_script(st.session_state.messages[-1])
        if created_file:
            st.session_state.rerun = True
            st.balloons()
            time.sleep(2)
            st.rerun()


def handle_buttons():
    col1, col2 = st.columns(2)
    with col1:
        if len(st.session_state.messages) > 2:
            st.button(
                "Clear chat history",
                on_click=clear_chat_history,
                key="clear_chat_history",
            )
        else:
            st.button(
                "Clear chat history",
                key="clear_chat_history",
                disabled=True,
            )
    with col2:
        if (
            "temp_file_path" in st.session_state
            and st.session_state.temp_file_path
            and os.path.exists(st.session_state.temp_file_path)
        ):
            with open(st.session_state.temp_file_path, "r") as file:
                btn = st.download_button(
                    label="Download file",
                    data=file.read(),
                    file_name="streamlit_app.py",
                    mime="text/x-python",
                )
        else:
            st.download_button(
                label="Download file",
                data="",
                file_name="streamlit_app.py",
                mime="text/x-python",
                disabled=True,
            )
    # delete_temp_file()


def setup_sidebar():
    display_main_sidebar_ui()
    with st.sidebar:
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(prompt)

        generate_response_if_needed()
        handle_buttons()
        st.divider()

        display_code_templates()
        # Ensure the dropdown resets after selection
        if st.session_state.get("selected_template"):
            st.session_state.selected_template = ""

        display_version_control()

        display_code_editor()


setup_sidebar()


if (
    "temp_file_path" in st.session_state
    and st.session_state.temp_file_path
    and os.path.exists(st.session_state.temp_file_path)
):
    file_path = st.session_state.temp_file_path

    execute_user_code(file_path)

else:
    print("No temporary file path found in session state.")
