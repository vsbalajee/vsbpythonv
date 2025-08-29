"""
Session state management for Vsbvibe application
"""

import streamlit as st
from typing import Dict, Any, Optional

def initialize_session_state():
    """Initialize session state variables"""
    
    # Core application state
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    
    if "project_loaded" not in st.session_state:
        st.session_state.project_loaded = False
    
    if "project_path" not in st.session_state:
        st.session_state.project_path = None
    
    if "project_config" not in st.session_state:
        st.session_state.project_config = None
    
    # Form state
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    
    # UI state
    if "show_help" not in st.session_state:
        st.session_state.show_help = False
    
    if "admin_tab" not in st.session_state:
        st.session_state.admin_tab = "Requirements"
    
    # Generation state
    if "generation_status" not in st.session_state:
        st.session_state.generation_status = "ready"
    
    if "last_generated" not in st.session_state:
        st.session_state.last_generated = None

def get_session_state(key: str, default: Any = None) -> Any:
    """Get session state value safely"""
    return st.session_state.get(key, default)

def update_session_state(updates: Dict[str, Any]):
    """Update multiple session state values"""
    for key, value in updates.items():
        st.session_state[key] = value

def clear_session_state():
    """Clear all session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def get_project_state() -> Dict[str, Any]:
    """Get current project state"""
    return {
        "loaded": st.session_state.get("project_loaded", False),
        "path": st.session_state.get("project_path"),
        "config": st.session_state.get("project_config"),
        "current_step": st.session_state.get("current_step", 1)
    }

def set_project_state(project_path: str, project_config: Dict[str, Any]):
    """Set project state"""
    st.session_state.project_loaded = True
    st.session_state.project_path = project_path
    st.session_state.project_config = project_config

def reset_project_state():
    """Reset project state"""
    st.session_state.project_loaded = False
    st.session_state.project_path = None
    st.session_state.project_config = None
    st.session_state.current_step = 1

def get_form_data(step: int) -> Dict[str, Any]:
    """Get form data for specific step"""
    return st.session_state.form_data.get(f"step_{step}", {})

def save_form_data(step: int, data: Dict[str, Any]):
    """Save form data for specific step"""
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    
    st.session_state.form_data[f"step_{step}"] = data

def get_generation_status() -> str:
    """Get current generation status"""
    return st.session_state.get("generation_status", "ready")

def set_generation_status(status: str):
    """Set generation status"""
    st.session_state.generation_status = status