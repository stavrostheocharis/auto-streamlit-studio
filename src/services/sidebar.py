import streamlit as st
import os
import toml

from src.utils.key_management import api_token_input
from src.utils.utils import (
    clear_chat_history,
    display_disclaimer,
    display_contacts,
    add_icon,
)
from audio_recorder_streamlit import audio_recorder

from src.services.versioning import display_version_control
from src.utils.templates import display_code_templates
from src.services.code_editor import display_code_editor
from src.services.chat import (
    generate_response_if_needed,
    display_chat_messages,
    written_chat,
    other_chat,
)
from src.services.voice import (
    transcribe_audio_file,
    process_voice_command,
    convert_bytes_to_mp3,
)


def display_main_sidebar_ui():
    st.logo(
        "src/images/streamlit-logo.png",
        link="https://github.com/stavrostheocharis/auto-streamlit",
    )
    with st.sidebar:
        st.title("AutoStreamlit Studio")
        info = toml.load("info.toml")
        tool_description = info["tool_description"]

        with st.expander(
            "About AutoStreamlit Studio",
        ):
            st.title(tool_description["title"])
            st.markdown(tool_description["description"])

        with st.expander("How to Use"):
            st.markdown(
                """
                1. Select your provider and enter the API key.
                2. Enter your requirements in the chat input box.
                3. View past conversations in the chat history.
                4. Use predefined templates to quickly create apps.
                5. Edit the generated script through chat or in developer mode.
                6. Save, load, or reset versions using version control.
                7. Use 'Clear chat history' to delete previous chats.
                """
            )

        provider, client, authed = api_token_input()

        return provider, client, authed


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

        if "last_audio_bytes" not in st.session_state:
            st.session_state["last_audio_bytes"] = None

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


def setup_sidebar():
    provider, client, authed = display_main_sidebar_ui()
    st.sidebar.divider()
    with st.sidebar:
        if authed:
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

        st.divider()
        display_disclaimer()
        st.divider()
        display_contacts()
