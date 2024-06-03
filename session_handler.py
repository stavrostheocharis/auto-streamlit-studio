import uuid
import streamlit as st
from datetime import datetime, timedelta

SESSION_TIMEOUT = 30  # Timeout period in minutes


def check_session_expiry():
    if "last_activity" in st.session_state:
        now = datetime.now()
        last_activity = st.session_state.last_activity
        if now - last_activity > timedelta(minutes=SESSION_TIMEOUT):
            clear_session()
    st.session_state.last_activity = datetime.now()


def clear_session():
    st.session_state.clear()
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.last_activity = datetime.now()
