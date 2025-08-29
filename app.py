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
import os

def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Global error report download in sidebar
    excel_path = os.path.join("_vsbvibe", "errors", "error_report.xlsx")
    if os.path.exists(excel_path):
        with open(excel_path, "rb") as f:
            st.sidebar.download_button(
                "📥 Download Error Report (Excel)",
                data=f.read(),
                file_name="error_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download the latest error report"
            )
    else:
        st.sidebar.caption("Error report will appear here after first error or on Admin → Generate.")
    
    # Log page view
    log_page_view()
    
    # Handle routing and render appropriate interface
    handle_routing()

if __name__ == "__main__":
    main()