import streamlit as st


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
