import streamlit as st
import os
from chat import chat
from utils import get_script

# App title
st.set_page_config(page_title="Test", page_icon="🤖", layout="wide")


# st.title("UPLine AI")
def display_sidebar_ui():
    with st.sidebar:
        st.title("Test")

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


display_sidebar_ui()
with st.sidebar:
    chat()

get_script(st.session_state.messages[-1])

file_path = "streamlit_app.py"

if os.path.exists(file_path):
    from streamlit_app import main

    main()
    st.rerun()
else:
    print(f"The file {file_path} does not exist.")
