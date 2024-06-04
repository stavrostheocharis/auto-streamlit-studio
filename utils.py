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

# Set up logging
logging.basicConfig(
    filename="auto_streamlit.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


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
    # st.rerun()  # Ensure the chat history is cleared
    st.session_state.chat_aborted = False


def summary_text(query):
    prompt = []
    system_prompt_content = (
        "You are a summarizer. " "Make the summary of the given text.  \n\n"
    )
    # system_prompt = "<|im_start|>system\n" + system_prompt_content + "<|im_end|>"
    system_prompt = (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        + system_prompt_content
        + "<|eot_id|>"
    )
    prompt.append(system_prompt)

    # query_prompt = "<|im_start|>user\n" + query + "<|im_end|>"
    query_prompt = "<|start_header_id|>user<|end_header_id|>\n\n" + query + "<|eot_id|>"
    prompt.append(query_prompt)

    # prompt.append("<|im_start|>assistant")
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


system_prompt = (
    "You are an experienced python software engineer. "
    "Answer only by providing the code. "
    "Do not explain what the app and code do. "
    "The app has to be created with streamlit library. "
    "The app has to be created with a def main(): function "
    # "In the previous like of the the main() function you have always to include the decorator: @st.experimental_fragment"
    "The code you produce should be able to run by itself and do not leave parts to be added later by user or other code parts. "
    "You should not try to open files that you are not sure if they exist in a path. "
    "When you create widgets you have to inlcude each time a different unique `key` for each one of them. "
    "Use the following pieces of context and provide only the python code: \n\n"
)

system_prompt = (
    "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
    + system_prompt
    + "<|eot_id|>"
)
# system_prompt = "<|im_start|>system\n" + system_prompt + "<|im_end|>"


def generate_arctic_response():
    prompt = [system_prompt]
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            # prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
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
            # prompt.append(
            #     "<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>"
            # )
    # prompt.append("<|im_start|>assistant")
    prompt.append("<|start_header_id|>assistant<|end_header_id|>")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    if get_num_tokens(prompt_str) >= 4096:
        handle_message_overflow()

        # st.error(
        #     "Conversation length too long. Please keep it under 4096 tokens. Please clear memory."
        # )
        # st.sidebar.button(
        #     "Clear chat history", on_click=clear_chat_history, key="clear_chat_history"
        # )
        # st.stop()

    # st.sidebar.button(
    #     "Clear chat history", on_click=clear_chat_history, key="clear_chat_history"
    # )

    for event in replicate.stream(
        "meta/meta-llama-3-70b-instruct",
        input={
            "prompt": prompt_str,
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


def summarize_messages(messages):
    # Concatenate all previous messages
    summary = ""
    for message in messages:
        if message["role"] == "user":
            summary += f"User: {message['content']}\n"
        else:
            summary += f"Assistant: {message['content']}\n"
    # Use LLM to summarize the concatenated messages
    return summary_text(summary)


def handle_message_overflow():
    # Summarize the previous messages using the LLM
    summary = summary_text(summarize_messages(st.session_state.messages[:-2]))

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
            submitted = st.form_submit_button("Submit")
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
