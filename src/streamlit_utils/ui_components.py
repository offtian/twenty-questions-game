import streamlit as st


def setup_streamlit_page():
    """Configure Streamlit's page settings and initialize the session state for question count."""
    st.set_page_config(page_title="20 Questions with LLM", page_icon="🧠")
    st.title("🧠 Play 20 Questions with LLM")
    st.divider()


def initialize_question_count():
    """Initialize the question count in the session state if not already present"""
    if "question_count" not in st.session_state:
        st.session_state.question_count = 1


def get_temperature_setting():
    """Get the temperature setting from the user using a slider."""
    with st.sidebar:
        temperature = st.slider(
            "Set LLM Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1
        )
    return temperature
