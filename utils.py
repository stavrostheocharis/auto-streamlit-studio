import streamlit as st
import replicate
from transformers import AutoTokenizer
import re
import tempfile
import time
import os
import ast
import logging
import importlib
import sys
from openai import OpenAI
from replicate.client import Client


# Set up logging
logging.basicConfig(
    filename="auto_streamlit.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def api_token_input():
    provider = st.sidebar.selectbox(
        "Choose provider", ["OpenAI", "Replicate"], placeholder="OpenAI"
    )
    client = None
    authed = False
    if provider == "OpenAI":
        if "OPENAI_API_TOKEN" in st.secrets:
            openai_api_key = st.secrets["OPENAI_API_TOKEN"]
            print("OpenAI API token found in secrets.")
        else:
            openai_api_key = st.text_input("Enter OpenAI API token:", type="password")
            if not (openai_api_key.startswith("sk-") and len(replicate_api) == 51):
                st.warning("Please enter your OpenAI API token.", icon="⚠️")
                st.markdown(
                    "**Don't have an API token?** Head over to [OpenAI](https://openai.com/index/openai-api/) to sign up for one."
                )
            else:
                os.environ["OPENAI_API_TOKEN"] = openai_api_key
                client = OpenAI(api_key=os.environ["OPENAI_API_TOKEN"])
                authed = True
    else:
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
            else:
                os.environ["REPLICATE_API_TOKEN"] = replicate_api
                client = Client(api_token=os.environ["REPLICATE_API_TOKEN"])
                authed = True

    return provider, client, authed


def extract_code_from_answer(content):
    # Use regular expression to find the code block

    code_block = re.search(r"```python\s*(.*?)\s*```", content, re.DOTALL) or re.search(
        r"```python\s*(.*)", content, re.DOTALL
    )
    if code_block:
        return code_block
    else:
        code_block = re.search(r"```\s*(.*?)\s*```", content, re.DOTALL) or re.search(
            r"```\s*(.*)", content, re.DOTALL
        )
    return code_block


def get_script(response):
    code_block = extract_code_from_answer(response["content"])
    if code_block:
        code = code_block.group(1)

        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        with open(temp_file.name, "w") as file:
            file.write(code)

        # Save the temporary file path in session state
        st.session_state.temp_file_path = temp_file.name

        print("Code extracted and written to streamlit_app.py")
        return True
    else:
        print("No code block found in the response.")
        return False


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


def summary_text(query, provider, client):

    prompt = []
    system_prompt_content = (
        "You are a summarizer. " "Make the summary of the given text \n\n"
    )

    if provider == "OpenAI":
        system_prompt = {"role": "system", "content": system_prompt_content}
        prompt.append(system_prompt)
        query_prompt = {"role": "user", "content": query}
        prompt.append(query_prompt)
        prompt.append({"role": "assistant", "content": ""})
        response = client.chat.completions.create(model="gpt-4o", messages=prompt)

        return response.choices[0].message.content
    else:
        system_prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            + system_prompt_content
            + "<|eot_id|>"
        )
        prompt.append(system_prompt)
        query_prompt = (
            "<|start_header_id|>user<|end_header_id|>\n\n" + query + "<|eot_id|>"
        )
        prompt.append(query_prompt)
        prompt.append("<|start_header_id|>assistant<|end_header_id|>\n\n")
        prompt.append("")
        prompt_str = "\n".join(prompt)
        response = ""

        for event in replicate.stream(
            "meta/meta-llama-3-70b-instruct",
            input={
                "prompt": prompt_str,
                "prompt_template": r"{prompt}",
                "temperature": 0.2,
                "top_p": 0.9,
            },
        ):
            response += str(event)

        return response.strip()


@st.cache_data
def initialise_system_prompt(provider):

    system_prompt = (
        "You are an experienced python software engineer. "
        "Answer only by providing the code. "
        "Do not explain what the app and code do. "
        "The app has to be created with streamlit library. "
        "The app has to be created with a def main(): function "
        "Never use set_page_config() in your code "
        "The code you produce should be able to run by itself and do not leave parts to be added later by user or other code parts. "
        "You should not try to open files that you are not sure if they exist in a path. "
        "When you create widgets you have to inlcude each time a different unique `key` for each one of them. "
        "Use the following pieces of context and provide only the python code: \n\n"
    )

    if provider == "OpenAI":
        return {"role": "system", "content": system_prompt}

    else:
        return (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            + system_prompt
            + "<|eot_id|>"
        )


def setup_openai_prompt(client):
    system_prompt = initialise_system_prompt("OpenAI")
    prompt = [system_prompt]
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append({"role": "user", "content": dict_message["content"]})
        else:
            prompt.append({"role": "assistant", "content": dict_message["content"]})

    prompt.append({"role": "assistant", "content": ""})
    prompt_str = "\n".join(item["content"] for item in prompt)

    if get_num_tokens(prompt_str) >= 4096:
        handle_message_overflow("OpenAI", client)

    return prompt


def setup_replicate_prompt(client):
    system_prompt = initialise_system_prompt("Replicate")
    prompt = [system_prompt]
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append(
                "<|start_header_id|>user<|end_header_id|>\n\n"
                + dict_message["content"]
                + "<|eot_id|>"
            )
        else:
            prompt.append(
                "<|start_header_id|>assistant<|end_header_id|>\n\n"
                + dict_message["content"]
                + "<|eot_id|>"
            )
    prompt.append("<|start_header_id|>assistant<|end_header_id|>")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    if get_num_tokens(prompt_str) >= 4096:
        handle_message_overflow("Replicate", client)

    return prompt_str


def generate_response(provider, client):

    if provider == "OpenAI":
        prompt = setup_openai_prompt(client)
        response = client.chat.completions.create(model="gpt-4o", messages=prompt)
        yield response.choices[0].message.content
    else:
        prompt = setup_replicate_prompt(client)
        for event in client.stream(
            "meta/meta-llama-3-70b-instruct",
            input={
                "prompt": prompt,
                "prompt_template": r"{prompt}",
                "temperature": 0.2,
                "top_p": 0.9,
            },
        ):
            yield str(event)


def handle_import_error(e):
    """Handle ImportError and attempt to regenerate response."""
    error_message = f"Error importing streamlit_app: {e}"
    logging.error(error_message)
    st.error(error_message)
    resolve_error = st.button("Resolve error", key="resolve_error")
    if resolve_error:
        # Display a spinner for a short duration
        with st.spinner("Attempting to resolve the error..."):
            time.sleep(2)
            # Add the error message as a user message
            st.session_state.messages.append({"role": "user", "content": error_message})
            # Rerun the app to process the new user message
            st.rerun()


def check_syntax(code):
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, str(e)


def summarize_messages(messages, provider, client):
    # Concatenate all previous messages
    summary = ""
    for message in messages:
        if message["role"] == "user":
            summary += f"User: {message['content']}\n"
        else:
            summary += f"Assistant: {message['content']}\n"
    # Use LLM to summarize the concatenated messages
    return summary_text(summary, provider, client)


def handle_message_overflow(provider, client):
    # Summarize the previous messages using the LLM
    summary = summarize_messages(st.session_state.messages[:-2], provider, client)

    # Keep the last two messages
    last_two_messages = st.session_state.messages[-2:]

    # Update the session state messages with the summary and last two messages
    st.session_state.messages = [
        {"role": "assistant", "content": summary},
        *last_two_messages,
    ]


def execute_user_code(file_path):
    if os.path.exists(file_path):
        try:
            module_name = os.path.basename(file_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            streamlit_app = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = streamlit_app
            spec.loader.exec_module(streamlit_app)

            if hasattr(streamlit_app, "main"):
                streamlit_app.main()
            else:
                st.error("The script does not contain a main() function.")

            if st.session_state.rerun:
                st.session_state.rerun = False
                st.balloons()
                time.sleep(2)
                st.rerun()
        except Exception as e:
            handle_import_error(e)
    else:
        st.error("The script file does not exist.")


def validate_code_safety(code):
    safe_builtins = {"print", "range", "len"}
    node = ast.parse(code)
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name) or n.func.id not in safe_builtins:
                return False, f"Disallowed function call detected: {n.func.id}"
    return True, ""


def display_code_templates():
    templates = [
        {
            "name": "Basic App",
            "description": "Create a basic demo app with a title and some small inputs.",
        },
        {
            "name": "DataFrame Example",
            "description": "Create an app demonstrating capabilities with dataframes.",
        },
        {
            "name": "Interactive Widgets",
            "description": "Create an app with various interactive widgets.",
        },
        {
            "name": "File Uploader",
            "description": "Create an app to upload and display a file.",
        },
        {
            "name": "Line Chart Example",
            "description": "Create an app displaying a line chart and some small analysis.",
        },
        {
            "name": "Image Display",
            "description": "Create an app to display an image and small modifications.",
        },
        {
            "name": "Plotly Chart Example",
            "description": "Create an app displaying different capabilities of Plotly",
        },
        {
            "name": "MNIST dataset",
            "description": "Create an app visualising the MNIST dataset and training a model, showcasing basic results",
        },
        {
            "name": "Explainable AI",
            "description": "Create an app visualising explainable AI with Lime in a small dataset with a small trained model.",
        },
        {
            "name": "SQL Query Example",
            "description": "Create an app to run a SQL query.",
        },
    ]

    template_names = [template["name"] for template in templates]

    st.sidebar.markdown("## App Templates")
    with st.expander(label="Open template selection list"):
        # Initialize selected_template in session state
        if "selected_template" not in st.session_state:
            st.session_state.selected_template = ""

        with st.form("template_form"):
            selected_template_name = st.selectbox(
                label="",
                options=[""] + template_names,
                index=0,
            )
            submitted = st.form_submit_button("Submit", use_container_width=True)
            if submitted and selected_template_name:
                selected_template = next(
                    template
                    for template in templates
                    if template["name"] == selected_template_name
                )
                st.session_state.messages.append(
                    {"role": "user", "content": selected_template["description"]}
                )
                st.session_state.selected_template = selected_template_name
                st.rerun()
