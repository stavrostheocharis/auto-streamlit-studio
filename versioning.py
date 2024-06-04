import json
import time
import re
import tempfile
import os
import streamlit as st
from utils import get_script


def save_version():
    if "versions" not in st.session_state:
        st.session_state.versions = []

    if (
        "temp_file_path" in st.session_state
        and st.session_state.temp_file_path
        and os.path.exists(st.session_state.temp_file_path)
    ):
        with open(st.session_state.temp_file_path, "r") as file:
            current_code = file.read()
        st.session_state.versions.append(current_code)
        st.sidebar.success("Version saved successfully!")
    else:
        st.sidebar.error("No code available to save.")


def delete_temp_file():
    """Delete the temporary file and show a confirmation dialog."""
    if (
        "temp_file_path" in st.session_state
        and st.session_state.temp_file_path
        and os.path.exists(st.session_state.temp_file_path)
    ):
        delete_button = st.button("Reset app", key="delete")
        if delete_button:
            delete_confirmation()


@st.experimental_dialog("Confirm Deletion")
def delete_confirmation():
    st.write(
        "You are going to delete all the created versions of the app, are you sure?"
    )
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, delete them", key="validate_delete"):
            if (
                "temp_file_path" in st.session_state
                and st.session_state.temp_file_path
                and os.path.exists(st.session_state.temp_file_path)
            ):
                os.remove(st.session_state.temp_file_path)
                st.session_state.temp_file_path = None
                st.session_state.confirm_delete = False

                if "versions" in st.session_state and st.session_state.versions:
                    st.session_state.versions = []
                    st.success("All versions cleared successfully!")
                    st.success("The app has been reseted successfully.")
                    time.sleep(2)
                st.rerun()

    with col2:
        if st.button("No, keep them", key="cancel_delete"):
            st.session_state.confirm_delete = False
            st.rerun()


def display_version_control():
    st.sidebar.markdown("## Version Control")
    # version_box = st.checkbox("Open version opts", key="vers")
    # if version_box:
    with st.expander(label="Open version options"):

        col1, col2 = st.columns([2, 4])

        with col1:
            st.button("Save Version", on_click=save_version)
            delete_temp_file()
        with col2:
            if "versions" in st.session_state and st.session_state.versions:
                version = st.selectbox(
                    "Select a version", range(len(st.session_state.versions))
                )
                if st.button("Load Version"):
                    selected_version_code = st.session_state.versions[version]
                    with open(st.session_state.temp_file_path, "w") as file:
                        file.write(selected_version_code)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": selected_version_code}
                    )

                    created_file = get_script(st.session_state.messages[-1])
                    if created_file:
                        st.session_state.rerun = True
                        st.rerun()
