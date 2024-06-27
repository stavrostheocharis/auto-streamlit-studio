import re
import tempfile
import os
import ast
import importlib
import sys
import streamlit as st
import time
import logging

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


def check_syntax(code):
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, str(e)


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
