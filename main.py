import streamlit as st
import os
from utils import get_script, generate_arctic_response

# App title
st.set_page_config(page_title="Auto-streamlit", page_icon="🤖", layout="wide")

if "rerun" not in st.session_state.keys():
    st.session_state.rerun = False


def display_sidebar_ui():
    with st.sidebar:
        st.title("Auto-streamlit")

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

display_sidebar_ui()
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
            st.rerun()


file_path = "streamlit_app.py"

print(st.session_state.messages, " st.session_state.messages")
if os.path.exists(file_path):
    from streamlit_app import main

    main()

    # print(st.session_state.messages)
    if st.session_state.rerun:
        st.session_state.rerun = False
        st.rerun()
else:
    print(f"The file {file_path} does not exist.")
