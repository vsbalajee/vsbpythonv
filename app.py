"""
Vsbvibe Main Application - Streamlined Entry Point
Refactored for modularity and maintainability
"""

import streamlit as st
import sys
import os

# --- Secrets bootstrap (OpenAI & others) ---
import os
import streamlit as st

if "openai_api_key" in st.secrets and st.secrets.get("openai_api_key"):
    os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]

# Set default OpenAI model (always GPT-5 Mini unless overridden)
DEFAULT_OPENAI_MODEL = st.secrets.get("openai_model", "gpt-5-mini")

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from core.routing import handle_routing
from core.state import initialize_session_state
from core.telemetry import log_page_view

def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Log page view
    log_page_view()
    
    # Handle routing and render appropriate interface
    handle_routing()

if __name__ == "__main__":
    main()