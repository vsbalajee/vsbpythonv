"""
Vsbvibe Main Application - Streamlined Entry Point
Refactored for modularity and maintainability
"""

import streamlit as st
import sys
import os

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