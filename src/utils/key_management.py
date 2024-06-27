import os
import streamlit as st
import openai
from replicate.client import Client
from time import sleep


def get_api_token_input(provider):
    token_name = f"{provider.upper()}_API_TOKEN"
    if token_name in st.secrets:
        api_token = st.secrets[token_name]
        print(f"{provider} API token found in secrets.")
    else:
        if f"{provider.lower()}_token" not in st.session_state:
            st.session_state[f"{provider.lower()}_token"] = ""

        api_token = st.text_input(
            f"Enter {provider} API token:",
            type="password",
            key=f"input_{provider.lower()}_token",
            value=st.session_state[f"{provider.lower()}_token"],
            on_change=update_token_state,
            args=(provider,),
        )

        if not validate_token_format(api_token, provider):
            st.warning(f"Please enter your {provider} API token.", icon="⚠️")
            st.markdown(
                f"**Don't have an API token?** Head over to [{provider}](https://{provider.lower()}.com) to sign up for one."
            )
    return api_token


def update_token_state(provider):
    st.session_state[f"{provider.lower()}_token"] = st.session_state[
        f"input_{provider.lower()}_token"
    ]
    st.session_state.auth["authed"] = False  # Reset auth status when token changes


def validate_token_format(token, provider):
    if provider == "OpenAI":
        return token.startswith("sk-") and len(token) == 51
    elif provider == "Replicate":
        return token.startswith("r8_") and len(token) == 40
    return False


def initialize_client(provider, token):
    if provider == "OpenAI":
        os.environ["OPENAI_API_TOKEN"] = token
        openai.api_key = token
        client = openai
    elif provider == "Replicate":
        os.environ["REPLICATE_API_TOKEN"] = token
        client = Client(api_token=token)
    return client


def validate_token_existence(provider, client):
    try:
        if provider == "OpenAI":
            client.models.list()  # A simple API call to validate the token
        elif provider == "Replicate":
            client.predictions.list()  # A simple API call to validate the token
        return True
    except Exception as e:
        st.error(f"Invalid {provider} API token.", icon="🚫")
        print(e)
        return False


def api_token_input():
    if "auth" not in st.session_state:
        st.session_state.auth = {"provider": None, "client": None, "authed": False}

    current_provider = st.sidebar.selectbox(
        "Choose provider", ["OpenAI", "Replicate"], index=0
    )

    # Reset session state if provider changes
    if st.session_state.auth["provider"] != current_provider:
        st.session_state.auth = {"provider": None, "client": None, "authed": False}
        st.session_state[f"{current_provider.lower()}_token"] = ""

    with st.expander("Add API token", expanded=True):
        api_token = get_api_token_input(current_provider)

        if api_token and validate_token_format(api_token, current_provider):
            if not st.session_state.auth["authed"]:
                client = initialize_client(current_provider, api_token)
                if validate_token_existence(current_provider, client):
                    st.session_state.auth["provider"] = current_provider
                    st.session_state.auth["client"] = client
                    st.session_state.auth["authed"] = True
                    st.session_state[f"{current_provider.lower()}_token"] = api_token
                    st.success(
                        f"{current_provider} API token validated successfully!",
                        icon="✅",
                    )
                    sleep(1)
                    st.rerun()
                else:
                    st.session_state.auth["client"] = None
            else:
                st.info(f"{current_provider} API token already validated.")
        else:
            st.session_state.auth["client"] = None

    return (
        st.session_state.auth["provider"],
        st.session_state.auth["client"],
        st.session_state.auth["authed"],
    )
