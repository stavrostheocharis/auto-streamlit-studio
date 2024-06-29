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
                    background-image: url("src/logo/logo.png");
                    background-repeat: no-repeat;
                    padding-top: 80px;
                    background-position: 20px 20px;
                }}
            </style>
            """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=3600)
def display_links(*links) -> None:
    """Displays provided links in the sidebar"""
    for link in links:
        if "name" in link and "url" in link:
            st.sidebar.markdown(
                f"<a style='display: block; text-align: left;' href={link['url']}>{link['name']}</a>",
                unsafe_allow_html=True,
            )


@st.cache_data(ttl=3600)
def add_icon(icon_url, redirect_url, width=100):
    st.markdown(
        f"""
        <a href="{redirect_url}" target="_blank">
            <img src="{icon_url}" style="width: {width}px; height: auto;">
        </a>
        """,
        unsafe_allow_html=True,
    )


def display_disclaimer():
    st.sidebar.write(
        """
        ##### ***Disclaimer***
        *This app is not production-ready as it executes code based on user input, which can potentially harm your system if incorrect code is executed. It is strongly recommended for local use only or to run it in an isolated environment.*
        """
    )


def display_contacts():
    st.sidebar.write(
        """
        ### **Contact**
        [![](https://img.shields.io/badge/GitHub-Follow-informational)](https://github.com/stavrostheocharis)
        [![](https://img.shields.io/badge/Linkedin-Connect-informational)](https://www.linkedin.com/in/stavros-theocharis-ai/)
        [![](https://img.shields.io/badge/Open-Issue-informational)](https://github.com/stavrostheocharis/auto-streamlit/issues)
        """
    )
    display_links(
        {
            "name": "Follow me on Medium",
            "url": "https://medium.com/@stavrostheocharis",
        }
    )
    st.sidebar.write(
        """
        ###### © Stavros Theocharis, 2024. All rights reserved.
        """
    )
