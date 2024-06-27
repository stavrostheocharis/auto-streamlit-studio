import streamlit as st
from transformers import AutoTokenizer
import logging

# Set up logging
logging.basicConfig(
    filename="auto_streamlit.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


@st.cache_data(show_spinner=False)
def get_tokenizer():
    """Get a tokenizer to make sure we're not sending too much text to the Model."""
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")


def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt."""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)


def clear_chat_history():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! Provide me your requirements to build you a streamlit app!",
        }
    ]
    st.session_state.chat_aborted = False
