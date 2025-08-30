"""
Error handling and reporting system
"""

import json
import os
import traceback
import hashlib
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Callable
from pathlib import Path
from functools import wraps

class ErrorReporter:
    """Centralized error reporting and Excel generation"""
    
    def __init__(self):
        self.errors_dir = Path("_vsbvibe/errors")
        self.errors_dir.mkdir(parents=True, exist_ok=True)
        
        self.suggestions_dir = self.errors_dir / "suggestions"
        self.suggestions_dir.mkdir(exist_ok=True)
    
    def capture_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """Capture and process error with full context"""
        
        if context is None:
            context = {}
        
        # Extract error details
        error_name = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # Parse traceback for file/line info
        tb_lines = error_traceback.split('\n')
        file_info = self._extract_file_info(tb_lines)
        
        # Generate error ID
        error_id = self._generate_error_id(error_name, file_info.get('filename', ''), 
                                         file_info.get('line_number', 0), error_message)
        
        # Get project context
        project_context = self._get_project_context()
        
        # Root cause analysis
        root_causes, other_causes = self._analyze_root_causes(error_name, error_message, error_traceback)
        
        # Create error record
        error_record = {
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "error_name": error_name,
            "error_details": error_message,
            "root_causes": root_causes,
            "other_possible_causes": other_causes,
            "files_to_correct": file_info.get('filename', 'unknown'),
            "line_number": file_info.get('line_number', 0),
            "suggested_fix": self._generate_suggested_fix(error_name, error_message),
            "module": context.get('module', file_info.get('module', 'unknown')),
            "platform_target": project_context.get('platform_target', 'unknown'),
            "site_mode": project_context.get('site_mode', 'unknown'),
            "plan_version": project_context.get('plan_version', 'unknown'),
            "requirements_version": project_context.get('requirements_version', 'unknown'),
            "status": "new",
            "traceback": error_traceback,
            "context": context
        }
        
        # Log to errors.log
        from .telemetry import log_error
        log_error(error_record)
        
        # Update Excel report
        self._update_excel_report(error_record)
        
        # Generate AI suggestion if possible
        self._generate_ai_suggestion(error_id, error_record)
        
        return error_id
    
    def _extract_file_info(self, tb_lines: List[str]) -> Dict[str, Any]:
        """Extract file and line information from traceback"""
        
        file_info = {
            "filename": "unknown",
            "line_number": 0,
            "module": "unknown"
        }
        
        for line in tb_lines:
            if 'File "' in line and 'line ' in line:
                try:
                    # Parse: File "/path/file.py", line 123, in function_name
                    parts = line.strip().split('"')
                    if len(parts) >= 2:
                        filepath = parts[1]
                        filename = os.path.basename(filepath)
                        file_info["filename"] = filename
                        
                        # Extract module from path
                        if 'site/' in filepath:
                            module_path = filepath.split('site/')[-1]
                            file_info["module"] = module_path.replace('/', '.').replace('.py', '')
                        
                        # Extract line number
                        line_part = line.split('line ')[-1].split(',')[0]
                        file_info["line_number"] = int(line_part)
                        break
                except:
                    continue
        
        return file_info
    
    def _generate_error_id(self, error_name: str, filename: str, line_number: int, message: str) -> str:
        """Generate unique error ID"""
        
        content = f"{error_name}:{filename}:{line_number}:{message[:120]}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _get_project_context(self) -> Dict[str, Any]:
        """Get current project context"""
        
        context = {}
        
        # Load project config
        project_path = Path("_vsbvibe/project.json")
        if project_path.exists():
            try:
                with open(project_path, 'r') as f:
                    project_config = json.load(f)
                    context.update(project_config)
            except:
                pass
        
        # Load plan
        plan_path = Path("_vsbvibe/plan.json")
        if plan_path.exists():
            try:
                with open(plan_path, 'r') as f:
                    plan = json.load(f)
                    context["platform_target"] = plan.get("platform_target", "unknown")
                    context["site_mode"] = plan.get("site_mode", "unknown")
                    context["plan_version"] = plan.get("updated_at", "unknown")
            except:
                pass
        
        # Load requirements version
        req_versions_path = Path("_vsbvibe/requirements_versions.json")
        if req_versions_path.exists():
            try:
                with open(req_versions_path, 'r') as f:
                    versions = json.load(f)
                    context["requirements_version"] = len(versions)
            except:
                context["requirements_version"] = 1
        
        return context
    
    def _analyze_root_causes(self, error_name: str, message: str, traceback: str) -> tuple:
        """Analyze error for root causes and suggestions"""
        
        root_causes = []
        other_causes = []
        
        if error_name == "ImportError":
            root_causes.append("Missing module or incorrect import path")
            other_causes.extend([
                "Module not installed",
                "Circular import dependency",
                "Incorrect relative import syntax"
            ])
        
        elif error_name == "AttributeError":
            root_causes.append("Object does not have the requested attribute")
            other_causes.extend([
                "Typo in attribute name",
                "Object is None",
                "Wrong object type",
                "Module not fully loaded"
            ])
        
        elif error_name == "KeyError":
            root_causes.append("Dictionary key does not exist")
            other_causes.extend([
                "Typo in key name",
                "Data structure changed",
                "Missing default value handling",
                "Case sensitivity issue"
            ])
        
        elif error_name == "FileNotFoundError":
            root_causes.append("File or directory does not exist")
            other_causes.extend([
                "Incorrect file path",
                "File not created yet",
                "Permission issues",
                "Working directory mismatch"
            ])
        
        elif error_name == "TypeError":
            root_causes.append("Incorrect data type or function signature")
            other_causes.extend([
                "Wrong number of arguments",
                "Incompatible data types",
                "None value where object expected",
                "API signature changed"
            ])
        
        else:
            root_causes.append("General application error")
            other_causes.extend([
                "Logic error in code",
                "Unexpected data format",
                "External dependency issue",
                "Configuration problem"
            ])
        
        return root_causes, other_causes
    
    def _generate_suggested_fix(self, error_name: str, message: str) -> str:
        """Generate suggested fix for common errors"""
        
        suggestions = {
            "ImportError": "Check import path and ensure module exists",
            "AttributeError": "Verify object type and attribute spelling",
            "KeyError": "Add key existence check or default value",
            "FileNotFoundError": "Verify file path and ensure file exists",
            "TypeError": "Check function arguments and data types"
        }
        
        return suggestions.get(error_name, "Review error details and traceback for specific fix")
    
    def _update_excel_report(self, error_record: Dict[str, Any]):
        """Update Excel error report with de-duplication"""
        
        excel_path = self.errors_dir / "error_report.xlsx"
        
        # Load existing data
        if excel_path.exists():
            try:
                df = pd.read_excel(excel_path)
            except:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
        
        error_id = error_record["error_id"]
        
        # Check for existing error
        if not df.empty and error_id in df["error_id"].values:
            # Update existing record
            idx = df[df["error_id"] == error_id].index[0]
            df.loc[idx, "last_seen"] = error_record["timestamp"]
            df.loc[idx, "count"] = df.loc[idx, "count"] + 1
        else:
            # Add new record
            new_row = {
                "error_id": error_record["error_id"],
                "timestamp": error_record["timestamp"],
                "first_seen": error_record["timestamp"],
                "last_seen": error_record["timestamp"],
                "count": 1,
                "error_name": error_record["error_name"],
                "error_details": error_record["error_details"],
                "root_causes": "; ".join(error_record["root_causes"]),
                "other_possible_causes": "; ".join(error_record["other_possible_causes"]),
                "files_to_correct": error_record["files_to_correct"],
                "line_number": error_record["line_number"],
                "suggested_fix": error_record["suggested_fix"],
                "module": error_record["module"],
                "platform_target": error_record["platform_target"],
                "site_mode": error_record["site_mode"],
                "plan_version": error_record["plan_version"],
                "requirements_version": error_record["requirements_version"],
                "status": error_record["status"]
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Save Excel file
        try:
            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"Error saving Excel report: {e}")
    
    def _generate_ai_suggestion(self, error_id: str, error_record: Dict[str, Any]):
        """Generate AI-powered fix suggestion"""
        
        # Check if AI keys are available
        settings_path = Path("_vsbvibe/settings.json")
        if not settings_path.exists():
            return
        
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            # For now, create a placeholder patch file
            # In production, this would call OpenAI/Claude API
            patch_content = f"""# AI Suggestion for Error {error_id}

## Error Details
- **Type**: {error_record['error_name']}
- **Message**: {error_record['error_details']}
- **File**: {error_record['files_to_correct']}
- **Line**: {error_record['line_number']}

## Suggested Fix
{error_record['suggested_fix']}

## Root Causes
{'; '.join(error_record['root_causes'])}

## Alternative Solutions
{'; '.join(error_record['other_possible_causes'])}

## Code Patch
```python
# TODO: AI-generated patch would go here
# This requires API integration with OpenAI/Claude
```
"""
            
            patch_path = self.suggestions_dir / f"{error_id}.patch"
            with open(patch_path, 'w') as f:
                f.write(patch_content)
                
        except Exception as e:
            print(f"Error generating AI suggestion: {e}")

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

# Global error reporter instance
error_reporter = ErrorReporter()

def safe_page(func: Callable) -> Callable:
    """Decorator for safe page rendering with error capture"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            from .telemetry import log_event
            log_event("page_render_start", {"page": func.__name__})
            result = func(*args, **kwargs)
            log_event("page_render_success", {"page": func.__name__})
            return result
        except Exception as e:
            context = {
                "module": "page",
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            }
            
            error_id = error_reporter.capture_error(e, context)
            
            # Show user-friendly error in Streamlit
            try:
                import streamlit as st
                st.error(f"Page Error: {type(e).__name__}")
                st.write(f"Error ID: {error_id}")
                st.write("This error has been logged for review.")
                
                with st.expander("Technical Details"):
                    st.code(str(e))
            except:
                print(f"Page error in {func.__name__}: {e}")
            
            return None
    
    return wrapper

def safe_component(func: Callable) -> Callable:
    """Decorator for safe component rendering with error capture"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            context = {
                "module": "component",
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            }
            
            error_id = error_reporter.capture_error(e, context)
            
            # Show fallback component
            try:
                import streamlit as st
                st.warning(f"Component Error: {func.__name__}")
                st.caption(f"Error ID: {error_id}")
            except:
                print(f"Component error in {func.__name__}: {e}")
            
            return None
    
    return wrapper