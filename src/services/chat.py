import streamlit as st
import time
from src.services.prompts import generate_response
from src.utils.code_management import get_script


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
            st.rerun()


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
