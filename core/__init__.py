"""
Core module for Vsbvibe application
Contains routing, state management, and telemetry
"""

from .routing import handle_routing
from .state import initialize_session_state, get_session_state, update_session_state
from .telemetry import log_page_view, log_user_action

__all__ = [
    'handle_routing',
    'initialize_session_state', 
    'get_session_state',
    'update_session_state',
    'log_page_view',
    'log_user_action'
]