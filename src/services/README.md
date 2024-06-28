
# Core Functions
## Authentication and Token Management
- `api_token_input`: Manages API token input and validation for OpenAI and Replicate providers.

## Prompt and Response Handling
- `summary_text`: Generates summaries based on user input.
- `initialise_system_prompt`: Initializes the system prompt for OpenAI and Replicate.
- `setup_openai_prompt`: Sets up the prompt for OpenAI.
- `setup_replicate_prompt`: Sets up the prompt for Replicate.
- `generate_response`: Generates responses based on the provider (OpenAI or Replicate).

## Code Management
- `extract_code_from_answer`: Extracts code from the assistant's response.
- `get_script`: Retrieves the script from the response and saves it as a file.
- `execute_user_code`: Executes the generated user code.
- `check_syntax`: Checks the syntax of the provided code.
- `validate_code_safety`: Validates the safety of the code.

## Utility Functions
- `get_tokenizer`: Retrieves the tokenizer for text processing.
- `get_num_tokens`: Counts the number of tokens in a given prompt.
- `clear_chat_history`: Clears the chat history in the session state.
- `summarize_messages`: Summarizes the chat messages.
- `handle_message_overflow`: Manages overflow of messages by summarizing them.

## Template Management
- `display_code_templates`: Displays a list of available templates for the user to choose from.

## Voice Commands
- `transcribe_audio_file`: Transcribes audio files to text.
- `process_voice_command`: Processes the voice command to generate responses.
- `convert_bytes_to_mp3`: Converts audio bytes to MP3 format.