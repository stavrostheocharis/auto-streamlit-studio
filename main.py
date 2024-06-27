import streamlit as st
import os
import toml
from versioning import display_version_control
from utils import (
    get_script,
    generate_response,
    clear_chat_history,
    execute_user_code,
    display_code_templates,
)
from src.utils.key_management import api_token_input

from voice import transcribe_audio_file, process_voice_command, convert_bytes_to_mp3
import time
from code_editor import display_code_editor
from session_handler import initialize_session
from audio_recorder_streamlit import audio_recorder


# App title
st.set_page_config(page_title="AutoStreamlit Studio", page_icon="🦾", layout="wide")
info = toml.load("info.toml")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

initialize_session()


if "rerun" not in st.session_state.keys():
    st.session_state.rerun = False


def display_main_sidebar_ui():
    with st.sidebar:
        st.title("AutoStreamlit Studio")
        tool_description = info["tool_description"]

        with st.expander(
            "About AutoStreamlit Studio",
        ):
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

        provider, client, authed = api_token_input()

        return provider, client, authed


if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi., I'm your personal Streamlit assistant, a new intelligent assistant to help you create automatically streamlit apps! What do you want to build?",
        }
    ]


def generate_response_if_needed(provider, client):
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = generate_response(provider, client)
            full_response = st.write_stream(response)

        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
        created_file = get_script(st.session_state.messages[-1])
        if created_file:
            st.session_state.rerun = True
            st.balloons()
            time.sleep(2)
            st.rerun()


def handle_buttons(provider, client):

    if provider == "OpenAI":
        if "new_recording_processed" not in st.session_state:
            st.session_state.new_recording_processed = False

        audio_bytes = audio_recorder(
            "Click to record",
            # recording_color="#e8b62c",
            # energy_threshold=0.01,
            # neutral_color="#303030",
            icon_size="2x",
            auto_start=False,
            key="audio_rec",
        )

        # if "last_audio_bytes" in st.session_state:
        #     st.audio(st.session_state["last_audio_bytes"], format="audio/wav")

        if "last_audio_bytes" not in st.session_state:
            st.session_state["last_audio_bytes"] = None

        # if "last_transcription" in st.session_state:
        #     st.write("The last transcription was: ", st.session_state["last_transcription"])

        if audio_bytes and audio_bytes != st.session_state["last_audio_bytes"]:
            st.session_state["last_audio_bytes"] = audio_bytes
            audio = convert_bytes_to_mp3(audio_bytes)
            trans_script = transcribe_audio_file(audio, client).text
            st.session_state["last_transcription"] = trans_script
            st.session_state.new_recording_processed = False
            process_voice_command(trans_script)
            st.rerun()

        if not st.session_state.new_recording_processed:
            generate_response_if_needed(provider, client)
            st.session_state.new_recording_processed = True

    col1, col2 = st.columns(2)
    with col1:
        if len(st.session_state.messages) > 2:
            st.button(
                "Clear chat history",
                on_click=clear_chat_history,
                key="clear_chat_history",
                use_container_width=True,
            )
        else:
            st.button(
                "Clear chat history",
                key="clear_chat_history",
                disabled=True,
                use_container_width=True,
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
                    use_container_width=True,
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


def display_chat_messages():
    icons = {"assistant": "🤖", "user": "🧑‍💻"}

    # Display the messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])


def written_chat(provider, client):
    """This function will be triggered by the main chat part of the app"""
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.expander("Generating code...", expanded=True):
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(prompt)

            generate_response_if_needed(provider, client)


def other_chat(provider, client):
    """This function will be triggered by other chat parts like voice or template"""
    with st.expander("Generating code...", expanded=True):
        generate_response_if_needed(provider, client)


def setup_sidebar():
    provider, client, authed = display_main_sidebar_ui()
    st.sidebar.divider()
    if authed:
        with st.sidebar:
            with st.expander("Chat history"):
                display_chat_messages()
            written_chat(provider, client)
            other_chat(provider, client)
            handle_buttons(provider, client)
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
