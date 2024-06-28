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


@st.cache_data(ttl=3600)
def add_logo():
    st.markdown(
        f"""
            <style>
                [data-testid="stSidebar"] {{
                    background-image: url(https://www.uphellas.gr/_next/static/media/logo.b4285350.svg);
                    background-repeat: no-repeat;
                    padding-top: 80px;
                    background-position: 20px 20px;
                }}
            </style>
            """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=3600)
def display_links(repo_link, other_link) -> None:
    """Displays a repository and other link"""
    col1, col2 = st.sidebar.columns(2)
    col1.markdown(
        f"<a style='display: block; text-align: center;' href={repo_link}>Source code</a>",
        unsafe_allow_html=True,
    )
    col2.markdown(
        f"<a style='display: block; text-align: center;' href={other_link}>App introduction</a>",
        unsafe_allow_html=True,
    )
