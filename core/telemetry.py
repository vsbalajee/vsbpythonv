"""
Telemetry and logging for Vsbvibe application
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

def log_page_view():
    """Log page view for analytics"""
    
    current_step = st.session_state.get("current_step", 1)
    project_path = st.session_state.get("project_path")
    
    if not project_path:
        return
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "page_view",
        "step": current_step,
        "session_id": st.session_state.get("session_id", "unknown")
    }
    
    _append_to_activity_log(project_path, log_entry)

def log_user_action(action: str, details: Dict[str, Any] = None):
    """Log user action"""
    
    project_path = st.session_state.get("project_path")
    
    if not project_path:
        return
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "user_action",
        "action": action,
        "details": details or {},
        "step": st.session_state.get("current_step", 1)
    }
    
    _append_to_activity_log(project_path, log_entry)

def log_generation_event(event_type: str, platform: str, files_created: int):
    """Log scaffold generation events"""
    
    project_path = st.session_state.get("project_path")
    
    if not project_path:
        return
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "generation",
        "type": event_type,
        "platform": platform,
        "files_created": files_created,
        "step": 3
    }
    
    _append_to_activity_log(project_path, log_entry)

def log_error(error_type: str, error_message: str, context: Dict[str, Any] = None):
    """Log application errors"""
    
    project_path = st.session_state.get("project_path")
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "error",
        "type": error_type,
        "message": error_message,
        "context": context or {},
        "step": st.session_state.get("current_step", 1)
    }
    
    if project_path:
        _append_to_activity_log(project_path, log_entry)
    else:
        # Log to console if no project path
        print(f"Error: {error_type} - {error_message}")

def get_activity_summary(project_path: str, hours: int = 24) -> Dict[str, Any]:
    """Get activity summary for the last N hours"""
    
    logs_path = os.path.join(project_path, "_vsbvibe", "logs", "activity.json")
    
    if not os.path.exists(logs_path):
        return {"total_events": 0, "events_by_type": {}, "recent_actions": []}
    
    try:
        with open(logs_path, 'r') as f:
            logs = json.load(f)
    except:
        return {"total_events": 0, "events_by_type": {}, "recent_actions": []}
    
    # Filter recent logs
    cutoff_time = datetime.now().timestamp() - (hours * 3600)
    recent_logs = []
    
    for log in logs:
        try:
            log_time = datetime.fromisoformat(log["timestamp"]).timestamp()
            if log_time >= cutoff_time:
                recent_logs.append(log)
        except:
            continue
    
    # Summarize
    events_by_type = {}
    for log in recent_logs:
        event_type = log.get("event", "unknown")
        events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
    
    return {
        "total_events": len(recent_logs),
        "events_by_type": events_by_type,
        "recent_actions": recent_logs[-10:]  # Last 10 actions
    }

def _append_to_activity_log(project_path: str, log_entry: Dict[str, Any]):
    """Append entry to activity log"""
    
    logs_path = os.path.join(project_path, "_vsbvibe", "logs", "activity.json")
    
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(logs_path), exist_ok=True)
    
    # Load existing logs
    logs = []
    if os.path.exists(logs_path):
        try:
            with open(logs_path, 'r') as f:
                logs = json.load(f)
        except:
            logs = []
    
    # Add new entry
    logs.append(log_entry)
    
    # Keep only last 1000 entries
    if len(logs) > 1000:
        logs = logs[-1000:]
    
    # Save logs
    try:
        with open(logs_path, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Error saving activity log: {e}")

def render_step1():
    """Render Step 1 interface"""
    from interfaces.step1 import render_step1_interface
    render_step1_interface()

def render_step2():
    """Render Step 2 interface"""
    from interfaces.step2 import render_step2_interface
    render_step2_interface()

def render_step3():
    """Render Step 3 interface"""
    from interfaces.step3 import render_step3_interface
    render_step3_interface()

def render_admin_interface():
    """Render Admin interface"""
    from modules.admin_interface import AdminInterface
    from modules.project_manager import ProjectManager
    
    project_manager = ProjectManager()
    admin = AdminInterface(project_manager)
    admin.render()