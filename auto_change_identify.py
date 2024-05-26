import os
import streamlit as st
import sys
import importlib


def check_for_changes(file_path):
    try:
        current_mod_time = os.path.getmtime(file_path)
        if st.session_state.last_mod_time is None:
            st.session_state.last_mod_time = current_mod_time
            return False
        if current_mod_time != st.session_state.last_mod_time:
            st.session_state.last_mod_time = current_mod_time
            return True
        return False
    except FileNotFoundError:
        return False


def load_and_run_app(file_path):
    if os.path.exists(file_path):
        try:
            if "streamlit_app" in sys.modules:
                streamlit_app = importlib.reload(sys.modules["streamlit_app"])
            else:
                streamlit_app = importlib.import_module("streamlit_app")
            streamlit_app.main()
        except ImportError as e:
            st.error(f"Error importing streamlit_app: {e}")
    else:
        st.error(f"The file {file_path} does not exist.")
