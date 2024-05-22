import streamlit as st
import replicate
from transformers import AutoTokenizer
import json
import re


def get_script(response):

    # Extract the content from the response
    content = response["content"]
    print("Content:\n", content)
    # Use regular expression to find the code block

    code_block = re.search(r"```python\s*(.*?)\s*```", content, re.DOTALL) or re.search(
        r"```python\s*(.*)", content, re.DOTALL
    )

    if code_block:
        code = code_block.group(1)

        # Write the code to a .py file
        with open("streamlit_app.py", "w") as file:
            file.write(code)

        print("Code extracted and written to streamlit_app.py")
    else:
        print("No code block found in the response.")


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


def analyze_query(query):
    """Analyze the user's query to understand the context and intent."""
    system_prompt = (
        "Analyze the following user query and provide a more detailed and contextually rich version of how the streamlit python code can be created in steps. "
        "Do not create code at this phase only create a plan of how the app will look like.  "
        "Keep as granted that streamlit is already installed \n\n"
    )

    full_prompt = system_prompt + query

    response = ""
    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "prompt": full_prompt,
            "temperature": 0.5,
            "top_p": 0.9,
        },
    ):
        response += str(event)

    return response.strip()


# Function for generating Snowflake Arctic response
def generate_arctic_response(prompt_str, temperature, top_p):
    # Check if the prompt exceeds the token limit

    system_prompt = (
        "You are an experienced python software engineer. "
        "Answer only by providing the code. "
        # "Answer only by providing the code no explanations, details, or other text. "
        "Do not explain what the app and code do. "
        "The app has to be created with streamlit library. "
        "The app has to be created with a def main(): function "
        "The code you produce should be able to run by itself and do not leave parts to be added later by user or other code parts. "
        "You should not try to open files that you are not sure if they exist in a path. "
        "When you create widgets you have to inlcude each time a different unique `key` for each one of them. "
        "Use the following pieces of context and provide only the python code: \n\n"
    )
    full_prompt = system_prompt + prompt_str
    print("The full prompt is: ", full_prompt)
    if get_num_tokens(prompt_str) > 2048:
        st.error("Conversation length too long. Please keep it under 3072 tokens.")
        st.button(
            "Clear chat history", on_click=clear_chat_history, key="clear_chat_history"
        )
        st.stop()

    # response = ""
    st.session_state.messages.append({"role": "assistant", "content": ""})
    for _, event in enumerate(
        replicate.stream(
            "snowflake/snowflake-arctic-instruct",
            input={
                "prompt": full_prompt,
                "prompt_template": r"{prompt}",
                "temperature": temperature,
                "top_p": top_p,
            },
        )
    ):
        st.session_state.messages[-1]["content"] += str(event)
        # response += str(event)
        # response_container.markdown(response)  # Update the response incrementally
        # return response
        yield str(event)
