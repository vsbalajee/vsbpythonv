"""
Telemetry and logging system for Streamlit site
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

def log_event(event: str, meta: Dict[str, Any] = None):
    """Log application event to JSONL format"""
    
    if meta is None:
        meta = {}
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "meta": meta,
        "session_id": _get_session_id()
    }
    
    _append_to_log("app.log", log_entry)

def log_error(meta: Dict[str, Any]):
    """Log error event to errors.log"""
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "error",
        "meta": meta,
        "session_id": _get_session_id()
    }
    
    _append_to_log("errors.log", log_entry)

def get_activity_summary(hours: int = 24) -> Dict[str, Any]:
    """Get activity summary for the last N hours"""
    
    logs_dir = Path("_vsbvibe/logs")
    app_log_path = logs_dir / "app.log"
    
    if not app_log_path.exists():
        return {"total_events": 0, "events_by_type": {}, "recent_events": []}
    
    cutoff_time = datetime.now().timestamp() - (hours * 3600)
    recent_events = []
    events_by_type = {}
    
    try:
        with open(app_log_path, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    log_time = datetime.fromisoformat(log_entry["timestamp"]).timestamp()
                    
                    if log_time >= cutoff_time:
                        recent_events.append(log_entry)
                        event_type = log_entry.get("event", "unknown")
                        events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
                        
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception:
        pass
    
    return {
        "total_events": len(recent_events),
        "events_by_type": events_by_type,
        "recent_events": recent_events[-50:]  # Last 50 events
    }

def _get_session_id() -> str:
    """Get or create session ID"""
    try:
        import streamlit as st
        if "session_id" not in st.session_state:
            st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        return st.session_state.session_id
    except:
        return "unknown"

def _append_to_log(log_filename: str, log_entry: Dict[str, Any]):
    """Append log entry to JSONL file"""
    
    logs_dir = Path("_vsbvibe/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_path = logs_dir / log_filename
    
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Error writing to log {log_filename}: {e}")

def _ensure_log_files():
    """Ensure log files exist"""
    logs_dir = Path("_vsbvibe/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    for log_file in ["app.log", "errors.log"]:
        log_path = logs_dir / log_file
        if not log_path.exists():
            log_path.touch()

# Initialize log files
_ensure_log_files()