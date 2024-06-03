import streamlit as st
import os
import sys
import toml
import importlib
from utils import (
    get_script,
    generate_arctic_response,
    clear_chat_history,
    handle_import_error,
    delete_temp_file,
)
import time
import uuid
from code_editor import display_code_editor
from session_handler import check_session_expiry

# App title
st.set_page_config(page_title="Auto-streamlit", page_icon="🤖", layout="wide")
info = toml.load("info.toml")

# Initialize session ID and check expiry
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
check_session_expiry()


if "rerun" not in st.session_state.keys():
    st.session_state.rerun = False

if "retry_count" not in st.session_state:
    st.session_state.retry_count = 0


def display_main_sidebar_ui():
    with st.sidebar:
        st.title("Auto-streamlit")
        tool_description = info["tool_description"]
        with st.expander("About Auto-Streamlit"):
            st.title(tool_description["title"])
            st.markdown(tool_description["description"])

        if "REPLICATE_API_TOKEN" in st.secrets:
            print("Replicate API token found in secrets.")
            replicate_api = st.secrets["REPLICATE_API_TOKEN"]
        else:
            replicate_api = st.text_input("Enter Replicate API token:", type="password")
            if not (replicate_api.startswith("r8_") and len(replicate_api) == 40):
                st.warning("Please enter your Replicate API token.", icon="⚠️")
                st.markdown(
                    "**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one."
                )

        os.environ["REPLICATE_API_TOKEN"] = replicate_api


if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi., I'm your personal Streamlit assistant, a new intelligent assistant to help you create automatically streamlit apps! What do you want to build?",
        }
    ]

display_main_sidebar_ui()
with st.sidebar:
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="⛷️"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = generate_arctic_response()
            full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)

        created_file = get_script(st.session_state.messages[-1])
        if created_file:
            st.session_state.rerun = True
            st.balloons()  # Show balloons here
            time.sleep(2)  # Add a delay of 2 seconds
            st.rerun()

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
    delete_temp_file()
    developer_box = st.checkbox("Trust me, I'm a developer", key="dev")

    if developer_box:
        display_code_editor()

if (
    "temp_file_path" in st.session_state
    and st.session_state.temp_file_path
    and os.path.exists(st.session_state.temp_file_path)
):
    file_path = st.session_state.temp_file_path
    if os.path.exists(file_path):
        try:
            # Import the module dynamically from the temporary file
            module_name = os.path.basename(file_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            streamlit_app = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = streamlit_app
            spec.loader.exec_module(streamlit_app)

            streamlit_app.main()

            if st.session_state.rerun:
                st.session_state.rerun = False
                st.balloons()  # Show balloons here
                time.sleep(2)  # Add a delay of 2 seconds
                st.rerun()
        except Exception as e:
            handle_import_error(e)
    else:
        print(f"The file {file_path} does not exist.")
else:
    print("No temporary file path found in session state.")
