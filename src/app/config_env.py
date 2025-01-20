import os

import streamlit as st
from dotenv import load_dotenv


def config_env() -> str | None:
    """Loads the api key from the .env file."""
    load_dotenv()
    api_key = os.getenv("API_KEY")

    if api_key is None:
        st.info("Please configure your API key in the project.")
        st.stop()
    return api_key
