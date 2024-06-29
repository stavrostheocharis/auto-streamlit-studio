import time
import os
import streamlit as st
from src.utils.code_management import get_script


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
        st.toast("Version was saved successfully!", icon="✅️")
    else:
        st.toast("No code available to save.", icon="🚨")


def delete_temp_file():
    """Delete the temporary file and show a confirmation dialog."""
    if (
        "temp_file_path" in st.session_state
        and st.session_state.temp_file_path
        and os.path.exists(st.session_state.temp_file_path)
    ):
        delete_button = st.button("Reset app", key="delete", use_container_width=True)
        if delete_button:
            delete_confirmation()


@st.experimental_dialog("Confirm Deletion")
def delete_confirmation():
    st.write(
        "You are going to delete all the created versions of the app, are you sure?"
    )
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Yes, delete them", key="validate_delete", use_container_width=True
        ):
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
                    time.sleep(1)
                    st.success("The app has been reseted successfully.")
                    time.sleep(2)
                st.rerun()

    with col2:
        if st.button("No, keep them", key="cancel_delete", use_container_width=True):
            st.session_state.confirm_delete = False
            st.rerun()


def display_version_control():
    st.sidebar.markdown("## Version Control")
    with st.expander(label="Open version options"):
        col1, col2 = st.columns([2, 4])
        with col1:
            st.button("Save Version", on_click=save_version, use_container_width=True)
            delete_temp_file()
        with col2:
            if "versions" in st.session_state and st.session_state.versions:
                version = st.selectbox(
                    "Select a version", range(len(st.session_state.versions))
                )
                if st.button("Load Version", use_container_width=True):
                    selected_version_code = st.session_state.versions[version]
                    with open(st.session_state.temp_file_path, "w") as file:
                        file.write(selected_version_code)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": selected_version_code}
                    )
                    created_file = get_script(st.session_state.messages[-1])
                    st.toast(f"Loaded app version ''{version}''.", icon="ℹ️")
                    if created_file:
                        st.session_state.rerun = True
                        st.rerun()
