import replicate
import streamlit as st
from src.utils.utils import get_num_tokens


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
