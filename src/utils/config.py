import os
from dotenv import load_dotenv
import streamlit as st


def load_env_variables():
    load_dotenv()


def get_api_credentials(is_streamlit_active: bool = False):
    """Retrieve the OpenAI API key from either local env or Streamlit sidebar input.
    Ensures user-provided credentials are used for API access.
    """
    if is_streamlit_active:
        with st.sidebar:
            # User selects the API type (Azure or OpenAI) through a dropdown

            openai_api_type = st.selectbox(
                label="OpenAI API Type", options=["azure", "openai"], index=0
            )

            deployment_name = None
            api_base = None
            api_version = None
            openai_api_key = None
            # If Azure is selected, retrieve Azure-specific settings

            if openai_api_type == "azure":
                deployment_name = os.getenv("DEPLOYMENT_NAME") or st.text_input(
                    label="Azure Deployment Name"
                )
                api_base = os.getenv("OPENAI_API_BASE") or st.text_input(
                    label="OpenAI API Base URL"
                )
                api_version = os.getenv("OPENAI_API_VERSION") or st.selectbox(
                    label="OpenAI API Version",
                    options=["2023-07-01-preview"],
                )

            openai_api_key = os.getenv("OPENAI_API_KEY") or st.text_input(
                label="OpenAI API Key", type="password"
            )
            # Prompt for OpenAI API key if not already provided
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()
    else:
        openai_api_type = os.getenv("OPENAI_API_TYPE", "openai")
        deployment_name = os.getenv("DEPLOYMENT_NAME", "")
        api_base = os.getenv("OPENAI_API_BASE", "")
        api_version = os.getenv("OPENAI_API_VERSION", "2023-07-01-preview")
        openai_api_key = os.getenv("OPENAI_API_KEY", "")

    return openai_api_type, deployment_name, api_base, api_version, openai_api_key


if __name__ == "__main__":
    load_env_variables()
    print(get_api_credentials(False))
