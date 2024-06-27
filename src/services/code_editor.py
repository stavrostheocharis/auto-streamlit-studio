from streamlit_ace import st_ace
import streamlit as st
import os
import time
from src.utils.code_management import check_syntax


def display_code_editor():
    st.sidebar.markdown("## Developer")
    with st.expander(label="Trust me, I'm a developer"):
        if (
            "temp_file_path" in st.session_state
            and st.session_state.temp_file_path
            and os.path.exists(st.session_state.temp_file_path)
        ):
            with open(st.session_state.temp_file_path, "r") as file:
                initial_code = file.read()
        else:
            initial_code = "# Your code will appear here."

        edited_code = st_ace(
            value=initial_code,
            language="python",
            theme="monokai",
            key="ace_editor",
            show_gutter=True,
            show_print_margin=True,
            wrap=True,
            auto_update=False,
        )

        if st.button("Save Code"):
            valid, error_message = check_syntax(edited_code)

            if valid:
                with open(st.session_state.temp_file_path, "w") as file:
                    file.write(edited_code)
                st.session_state.temp_file_content = edited_code
                # Add edited code as it was produced by assistant
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"```\n{edited_code}\n```"}
                )
                st.success("Code saved successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Syntax error in code: {error_message}")
