import streamlit as st
import replicate
from transformers import AutoTokenizer
import re
import tempfile


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

        # Write the code to a .py file
        with open("streamlit_app.py", "w") as file:
            file.write(code)
        st.balloons()
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


def correct_code(query):
    """Analyze the user's code to correct it."""
    prompt = []
    system_prompt_content = (
        "You are a python code corrector. "
        "Answer only by providing the code. "
        "Do not explain what the app and code do. "
        "Analyze the following streamlit code part and provide a validated code that can run. "
        "Make sure that a def main(): part of function exists. "
        "Validate that the decorator  @st.experimental_fragment and not another decorator exists on top of the def main(): part \n\n"
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
        st.error(
            "Conversation length too long. Please keep it under 4096 tokens. Please clear memory."
        )
        st.sidebar.button(
            "Clear chat history", on_click=clear_chat_history, key="clear_chat_history"
        )
        st.stop()

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
