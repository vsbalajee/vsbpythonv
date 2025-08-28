import os
import json
import shutil
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from .utils import ensure_directory, save_json, load_json, log_activity

class ProjectManager:
    def __init__(self):
        self.current_project_path = None
        self.project_config = None
    
    def create_project_from_data(self, project_data: Dict[str, Any]) -> str:
        """Create a new project from form data"""
        project_name = project_data["project_name"]
        local_folder = project_data["local_folder"]
        
        # Sanitize project name for folder
        folder_name = project_name.lower().replace(" ", "-").replace("_", "-")
        folder_name = "".join(c for c in folder_name if c.isalnum() or c in "-")
        project_path = os.path.join(local_folder, folder_name)
        
        # Create directory structure
        self._create_directory_structure(project_path)
        
        # Save project configuration
        config_path = os.path.join(project_path, "_vsbvibe", "project.json")
        save_json(config_path, project_data)
        
        # Create initial files
        self._create_initial_files(project_path, project_data)
        
        # Log activity
        log_activity(project_path, "project_created", f"Project '{project_name}' created successfully")
        
        self.current_project_path = project_path
        self.project_config = project_data
        
        return project_path
    
    def create_project(self, name: str, company: str, ref_url: str, 
                      requirements: str, content_mode: str, base_folder: str) -> str:
        """Create a new Vsbvibe project with proper directory structure"""
        
        # Sanitize project name for folder
        folder_name = name.lower().replace(" ", "-").replace("_", "-")
        project_path = os.path.join(base_folder, folder_name)
        
        # Create directory structure
        self._create_directory_structure(project_path)
        
        # Create project configuration
        project_config = {
            "project_name": name,
            "company_name": company,
            "reference_url": ref_url,
            "requirements": requirements,
            "content_mode": content_mode,
            "local_folder": base_folder,
            "logo": "",
            "screenshots": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "status": "setup_complete"
        }
        
        # Save project config
        config_path = os.path.join(project_path, "_vsbvibe", "project.json")
        save_json(config_path, project_config)
        
        # Create initial files
        self._create_initial_files(project_path, project_config)
        
        # Log activity
        log_activity(project_path, "project_created", f"Project '{name}' created")
        
        self.current_project_path = project_path
        self.project_config = project_config
        
        return project_path
    
    def load_project(self, project_path: str) -> str:
        """Load an existing Vsbvibe project"""
        config_path = os.path.join(project_path, "_vsbvibe", "project.json")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError("No Vsbvibe project found in this directory")
        
        self.project_config = load_json(config_path)
        if not self.project_config:
            raise ValueError("Invalid project configuration file")
        
        self.current_project_path = project_path
        
        # Log activity
        log_activity(project_path, "project_loaded", f"Project loaded from {project_path}")
        
        return self.project_config.get("project_name", self.project_config.get("name", "Unknown"))
    
    def save_project_config(self, config: Dict[str, Any]) -> bool:
        """Save project configuration to _vsbvibe/project.json"""
        if not self.current_project_path:
            return False
        
        config["updated_at"] = datetime.now().isoformat()
        config_path = os.path.join(self.current_project_path, "_vsbvibe", "project.json")
        
        if save_json(config_path, config):
            self.project_config = config
            log_activity(self.current_project_path, "config_updated", "Project configuration updated")
            return True
        return False
    
    def load_project_config(self) -> Optional[Dict[str, Any]]:
        """Load project configuration from _vsbvibe/project.json"""
        if not self.current_project_path:
            return None
        
        config_path = os.path.join(self.current_project_path, "_vsbvibe", "project.json")
        config = load_json(config_path)
        
        if config:
            self.project_config = config
        
        return config
    
    def get_current_project_path(self) -> Optional[str]:
        return self.current_project_path
    
    def get_project_config(self) -> Optional[Dict[str, Any]]:
        return self.project_config
    
    def update_project_config(self, updates: Dict[str, Any]):
        """Update project configuration"""
        if self.project_config:
            self.project_config.update(updates)
            self.project_config["updated_at"] = datetime.now().isoformat()
            
            config_path = os.path.join(self.current_project_path, "_vsbvibe", "project.json")
            save_json(config_path, self.project_config)
            
            log_activity(self.current_project_path, "config_updated", f"Updated: {', '.join(updates.keys())}")
    
    def update_requirements(self, requirements: str, version_note: str = ""):
        """Update project requirements with versioning"""
        if not self.project_config:
            raise ValueError("No project loaded")
        
        # Store previous version
        versions_path = os.path.join(self.current_project_path, "_vsbvibe", "requirements_versions.json")
        versions = load_json(versions_path) or []
        
        # Add current version to history
        if self.project_config.get("requirements"):
            versions.append({
                "version": len(versions) + 1,
                "requirements": self.project_config.get("requirements", ""),
                "note": version_note,
                "timestamp": datetime.now().isoformat()
            })
            
            save_json(versions_path, versions)
        
        # Update current requirements
        self.update_project_config({"requirements": requirements})
        
        log_activity(
            self.current_project_path, 
            "requirements_updated", 
            f"Requirements updated. Note: {version_note}" if version_note else "Requirements updated"
        )
    
    def _create_directory_structure(self, project_path: str):
        """Create the standard Vsbvibe directory structure"""
        directories = [
            "_vsbvibe",
            "_vsbvibe/tests",
            "_vsbvibe/logs",
            "assets",
            "assets/screenshots",
            "site",
            "site/pages",
            "site/components", 
            "site/assets",
            "site/utils",
            "content"
        ]
        
        for directory in directories:
            ensure_directory(os.path.join(project_path, directory))
    
    def _create_initial_files(self, project_path: str, config: Dict[str, Any]):
        """Create initial project files"""
        vsbvibe_path = os.path.join(project_path, "_vsbvibe")
        
        # Create plan.json
        plan = {
            "ui_ux_plan": {
                "layout": "modern",
                "color_scheme": "professional",
                "navigation": "header",
                "components": ["hero", "features", "contact"]
            },
            "pages": [
                {"name": "home", "type": "landing", "priority": 1},
                {"name": "about", "type": "info", "priority": 2},
                {"name": "contact", "type": "form", "priority": 3}
            ],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        save_json(os.path.join(vsbvibe_path, "plan.json"), plan)
        
        # Create seo_defaults.json
        seo_defaults = {
            "title_template": f"{config.get('company_name', 'Company')} - {{page_title}}",
            "meta_description": f"Welcome to {config.get('company_name', 'our website')}",
            "keywords": ["website", "business", config.get('company_name', 'company').lower()],
            "og_image": "/assets/og-image.jpg",
            "favicon": "/assets/favicon.ico",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        save_json(os.path.join(vsbvibe_path, "seo_defaults.json"), seo_defaults)
        
        # Create content_store.json
        content_store = {
            "pages": {},
            "products": [],
            "global": {
                "company_name": config.get('company_name', 'Your Company'),
                "tagline": "Your success is our mission",
                "description": config.get('requirements', '')[:200] + "..." if len(config.get('requirements', '')) > 200 else config.get('requirements', '')
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        save_json(os.path.join(vsbvibe_path, "content_store.json"), content_store)
        
        # Create sample products.xlsx
        products_data = {
            "Product Name": ["Sample Product 1", "Sample Product 2"],
            "Description": ["A great product", "Another amazing product"],
            "Price": [99.99, 149.99],
            "Category": ["Category A", "Category B"]
        }
        
        df = pd.DataFrame(products_data)
        df.to_excel(os.path.join(project_path, "content", "products.xlsx"), index=False)
        
        # Create settings.json placeholder
        settings = {
            "openai_key": "",
            "claude_key": "",
            "gemini_key": "",
            "huggingface_key": "",
            "supabase_url": "",
            "supabase_key": "",
            "github_token": "",
            "netlify_token": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        save_json(os.path.join(vsbvibe_path, "settings.json"), settings)