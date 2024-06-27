import streamlit as st
from utils import generate_response, analyze_query, clear_chat_history

TEMPERATURE = 0.5
TOP_P = 0.9


def display_chat_messages():
    icons = {"assistant": "🤖", "user": "💼"}

    # Display the messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])


def abort_chat(error_message: str):
    """Display an error message requiring the chat to be cleared.
    Forces a rerun of the app."""
    assert error_message, "Error message must be provided."
    error_message = f":red[{error_message}]"
    if st.session_state.messages[-1]["role"] != "assistant":
        st.session_state.messages.append(
            {"role": "assistant", "content": error_message}
        )
    else:
        st.session_state.messages[-1]["content"] = error_message
    st.session_state.chat_aborted = True
    st.rerun()


def get_and_process_prompt():
    """Get the user prompt and process it"""
    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        user_prompt = st.session_state.messages[-1]["content"]
        # analyzed_query = analyze_query(user_prompt)
        analyzed_query = user_prompt
        # Display the assistant's response incrementally
        with st.chat_message("assistant", avatar="🤖"):
            response = generate_response(analyzed_query, TEMPERATURE, TOP_P)
            st.write_stream(response)

    if st.session_state.chat_aborted:
        # st.button("Reset chat", on_click=clear_chat_history, key="clear_chat_history")
        st.chat_input(disabled=True)

    elif prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()


def init_chat_history():
    """Create a st.session_state.messages list to store chat messages"""
    if "messages" not in st.session_state:
        clear_chat_history()


def chat():
    init_chat_history()
    display_chat_messages()
    get_and_process_prompt()
