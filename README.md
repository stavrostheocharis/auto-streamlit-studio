# AutoStreamlit Studio

## Introduction

Welcome to AutoStreamlit Studio, your intelligent assistant designed to effortlessly create Streamlit applications. With AutoStreamlit Studio, simply provide your requirements through a prompt, and the tool takes care of the rest. It automatically generates, customizes, and runs a Streamlit app tailored to your specifications. Whether you need data visualization, interactive dashboards, or any other Streamlit functionality, AutoStreamlit Studio simplifies the process, turning your ideas into functional apps in no time. This innovative tool is designed to save time and enhance productivity for both developers and non-developers alike.

## Features

- **Automatic App Generation**: Provide your requirements, and AutoStreamlit Studio generates a complete Streamlit app for you.
- **Customizable Templates**: Choose from a variety of templates to kickstart your app development.
- **Interactive Widgets**: Add interactive elements like charts, tables, and forms effortlessly.
- **Voice Commands**: Use voice commands to interact with the tool and generate apps.
- **Code Editor**: Edit the generated code directly within the app for further customization.
- **Version Control**: Manage different versions of your app to track changes and improvements.
- **File Operations**: Easily download, upload, and run Streamlit app files.

## How to Use
1. **Enter Your Requirements**: Use the chat input box to specify your app requirements.
2. **Generate the Script**: AutoStreamlit Studio will generate a Streamlit script based on your input.
3. **Edit and Run**: You can download, edit, or run the generated script directly within the app.
4. **Manage Chat History**: Use the 'Clear chat history' button to delete the memory of previous chats.
5. **Delete App File**: Use the 'Delete app file' button to remove the current created app.

## Sidebar UI
The sidebar of AutoStreamlit Studio provides various functionalities to manage your app development process:
- **About AutoStreamlit Studio**: Learn more about the tool and its capabilities.
- **How to Use**: Detailed instructions on how to interact with the tool.
- **API Token Management**: Securely manage your API tokens for OpenAI and Replicate providers.
- **Chat History**: View the history of your interactions with the assistant.
- **Template Selection**: Choose from a variety of pre-defined templates to start your app.
- **Version Control**: Manage different versions of your app to keep track of changes.
- **Code Editor**: Edit the generated code directly within the app.

## Core Functions
### Authentication and Token Management
- `api_token_input`: Manages API token input and validation for OpenAI and Replicate providers.

### Prompt and Response Handling
- `summary_text`: Generates summaries based on user input.
- `initialise_system_prompt`: Initializes the system prompt for OpenAI and Replicate.
- `setup_openai_prompt`: Sets up the prompt for OpenAI.
- `setup_replicate_prompt`: Sets up the prompt for Replicate.
- `generate_response`: Generates responses based on the provider (OpenAI or Replicate).

### Code Management
- `extract_code_from_answer`: Extracts code from the assistant's response.
- `get_script`: Retrieves the script from the response and saves it as a file.
- `execute_user_code`: Executes the generated user code.
- `check_syntax`: Checks the syntax of the provided code.
- `validate_code_safety`: Validates the safety of the code.

### Utility Functions
- `get_tokenizer`: Retrieves the tokenizer for text processing.
- `get_num_tokens`: Counts the number of tokens in a given prompt.
- `clear_chat_history`: Clears the chat history in the session state.
- `summarize_messages`: Summarizes the chat messages.
- `handle_message_overflow`: Manages overflow of messages by summarizing them.

### Template Management
- `display_code_templates`: Displays a list of available templates for the user to choose from.

### Voice Commands
- `transcribe_audio_file`: Transcribes audio files to text.
- `process_voice_command`: Processes the voice command to generate responses.
- `convert_bytes_to_mp3`: Converts audio bytes to MP3 format.

## Getting Started
To get started with AutoStreamlit Studio, follow these steps:
1. **Set Up the Environment**: Ensure you have the necessary API tokens for OpenAI or Replicate.
2. **Run the App**: Execute the main script to start the AutoStreamlit Studio.
3. **Interact with the Assistant**: Use the chat input to specify your app requirements and watch as your app is generated in real-time.
4. **Customize and Extend**: Use the built-in code editor to make any custom changes to your app.

## Conclusion
AutoStreamlit Studio is designed to revolutionize the way you create Streamlit applications. With its intelligent assistant, customizable templates, and interactive features, you can quickly turn your ideas into functional apps, saving time and boosting productivity. Whether you are a developer looking to streamline your workflow or a non-developer needing to create powerful data-driven apps, AutoStreamlit Studio is your go-to solution.