import streamlit as st
import os
import sys
import importlib
import time
from auto_change_identify import load_and_run_app, check_for_changes

st.set_page_config(page_title="Running-app", page_icon="🤖", layout="wide")
file_path = "streamlit_app.py"
if "last_mod_time" not in st.session_state:
    st.session_state.last_mod_time = None


def main():
    load_and_run_app(file_path)
    # Check for changes in streamlit_app.py file every few seconds
    while True:
        time.sleep(5)  # Delay to prevent rapid rechecking
        if check_for_changes(file_path):
            st.experimental_rerun()


if __name__ == "__main__":
    main()
