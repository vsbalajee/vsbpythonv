import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    os.makedirs(path, exist_ok=True)

def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Load JSON file safely"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {file_path}: {e}")
    return None

def save_json(file_path: str, data: Dict[str, Any]) -> bool:
    """Save data to JSON file safely"""
    try:
        ensure_directory(os.path.dirname(file_path))
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")
        return False

def create_backup(source_path: str, backup_path: str) -> bool:
    """Create backup of file or directory"""
    try:
        if os.path.isfile(source_path):
            ensure_directory(os.path.dirname(backup_path))
            shutil.copy2(source_path, backup_path)
        elif os.path.isdir(source_path):
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(source_path, backup_path)
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def get_file_diff(old_content: str, new_content: str) -> Dict[str, Any]:
    """Generate simple file difference summary"""
    old_lines = old_content.splitlines() if old_content else []
    new_lines = new_content.splitlines() if new_content else []
    
    return {
        "lines_added": len(new_lines) - len(old_lines),
        "lines_changed": sum(1 for i, line in enumerate(new_lines) 
                           if i < len(old_lines) and line != old_lines[i]),
        "total_lines": len(new_lines)
    }

def log_activity(project_path: str, action: str, details: str):
    """Log activity to project logs"""
    if not project_path:
        return
        
    logs_path = os.path.join(project_path, "_vsbvibe", "logs", "activity.json")
    
    # Load existing logs
    logs = load_json(logs_path) or []
    
    # Add new log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    }
    
    logs.append(log_entry)
    
    # Keep only last 100 entries
    if len(logs) > 100:
        logs = logs[-100:]
    
    # Save logs
    save_json(logs_path, logs)

def create_file_diff_summary(files_created: list, files_updated: list, operation: str = "generate") -> dict:
    """Create a summary of file changes"""
    return {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "files_created": files_created,
        "files_updated": files_updated,
        "total_files": len(files_created) + len(files_updated),
        "summary": f"{operation.title()} operation: {len(files_created)} files created, {len(files_updated)} files updated"
    }

def validate_project_structure(project_path: str) -> Dict[str, bool]:
    """Validate project has proper Vsbvibe structure"""
    required_paths = [
        "_vsbvibe/project.json",
        "_vsbvibe/plan.json", 
        "_vsbvibe/seo_defaults.json",
        "_vsbvibe/content_store.json",
        "content/products.xlsx"
    ]
    
    results = {}
    for path in required_paths:
        full_path = os.path.join(project_path, path)
        results[path] = os.path.exists(full_path)
    
    return results