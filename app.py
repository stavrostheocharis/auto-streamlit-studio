import streamlit as st
import os

from src.utils.code_management import execute_user_code
from src.utils.session_handler import initialize_session
from src.services.sidebar import setup_sidebar

st.set_page_config(page_title="AutoStreamlit Studio", page_icon="🦾", layout="wide")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
initialize_session()


if "rerun" not in st.session_state.keys():
    st.session_state.rerun = False

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi., I'm your personal Streamlit assistant, a new intelligent assistant to help you create automatically streamlit apps! What do you want to build?",
        }
    ]


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
