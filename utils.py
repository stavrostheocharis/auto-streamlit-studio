import streamlit as st
import replicate
from transformers import AutoTokenizer
import re
import tempfile
import time
import os
import ast


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

    st.sidebar.button(
        "Clear chat history", on_click=clear_chat_history, key="clear_chat_history"
    )

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

    if "error_count" not in st.session_state:
        st.session_state.error_count = 0

    st.session_state.error_count += 1

    if st.session_state.error_count <= 3:
        st.error(error_message)

        # Display a spinner for a short duration
        with st.spinner("Attempting to resolve the error..."):
            time.sleep(2)

        # Add the error message as a user message
        st.session_state.messages.append({"role": "user", "content": error_message})

        # Rerun the app to process the new user message
        st.rerun()
    else:
        st.error("Failed to resolve the error after several attempts.")
        st.session_state.error_count = 0  # Reset the error count


def delete_temp_file():
    """Delete the temporary file and show a confirmation dialog."""
    if (
        "temp_file_path" in st.session_state
        and st.session_state.temp_file_path
        and os.path.exists(st.session_state.temp_file_path)
    ):
        delete_button = st.button("Delete app file", key="delete")
        if delete_button:
            delete_confirmation()


@st.experimental_dialog("Confirm Deletion")
def delete_confirmation():
    st.write("You are going to delete the created app file, are you sure?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, delete it"):
            if (
                "temp_file_path" in st.session_state
                and st.session_state.temp_file_path
                and os.path.exists(st.session_state.temp_file_path)
            ):
                os.remove(st.session_state.temp_file_path)
                st.session_state.temp_file_path = None
                st.success("Temporary file deleted successfully.")
            st.session_state.confirm_delete = False
            st.rerun()
    with col2:
        if st.button("No, keep it"):
            st.session_state.confirm_delete = False
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
