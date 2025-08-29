"""
Step 1 Interface - Project Setup & Requirements
"""

import streamlit as st
import os
from datetime import datetime
from modules.project_manager import ProjectManager
from core.state import save_form_data, get_form_data, set_project_state
from core.telemetry import log_user_action

def render_step1_interface():
    """Render Step 1 - Project Setup & Requirements"""
    
    st.header("🚀 Step 1: Project Setup & Requirements")
    st.write("Set up your project basics and define your requirements.")
    
    # Progress indicator
    progress_cols = st.columns(10)
    for i in range(10):
        with progress_cols[i]:
            if i == 0:
                st.markdown("🔵")  # Current step
            else:
                st.markdown("⚪")  # Future steps
    
    st.markdown("---")
    
    # Load existing form data
    form_data = get_form_data(1)
    
    # Project setup form
    with st.form("project_setup"):
        st.subheader("Project Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Project Name *", 
                value=form_data.get("project_name", ""),
                placeholder="My Awesome Website"
            )
            
            company_name = st.text_input(
                "Company/Brand Name *",
                value=form_data.get("company_name", ""),
                placeholder="Your Company Name"
            )
            
            local_folder = st.text_input(
                "Local Folder Path *",
                value=form_data.get("local_folder", os.path.expanduser("~/vsbvibe-projects")),
                help="Where to save your project files"
            )
        
        with col2:
            reference_url = st.text_input(
                "Reference URL (Optional)",
                value=form_data.get("reference_url", ""),
                placeholder="https://example.com"
            )
            
            content_mode = st.selectbox(
                "Content Mode *",
                ["AI Generated", "User Provided", "Hybrid"],
                index=["AI Generated", "User Provided", "Hybrid"].index(
                    form_data.get("content_mode", "AI Generated")
                )
            )
        
        # File uploads
        st.subheader("Assets (Optional)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            logo_file = st.file_uploader(
                "Logo Upload",
                type=["png", "jpg", "jpeg", "svg"],
                help="Upload your company logo"
            )
        
        with col2:
            screenshot_files = st.file_uploader(
                "Screenshots (5-10 images)",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                help="Upload reference screenshots for inspiration"
            )
        
        # Requirements
        st.subheader("Requirements")
        requirements = st.text_area(
            "Project Requirements *",
            value=form_data.get("requirements", ""),
            height=200,
            placeholder="""Describe your website requirements in detail:

• What type of website do you need? (e-commerce, portfolio, blog, etc.)
• Who is your target audience?
• What features do you want? (contact forms, product catalog, blog, etc.)
• What is your business about?
• Any specific design preferences?
• Integration requirements? (payment, CRM, analytics, etc.)

Example: "I need an e-commerce website for selling handmade jewelry. Target audience is women aged 25-45. Need product catalog, shopping cart, customer reviews, blog section, and contact form. Modern, elegant design with focus on product photography."
"""
        )
        
        # Form submission
        submitted = st.form_submit_button("Create Project", type="primary")
        
        if submitted:
            # Validate required fields
            if not project_name or not company_name or not requirements or not local_folder:
                st.error("Please fill in all required fields marked with *")
            else:
                # Process form submission
                success = _process_project_creation(
                    project_name, company_name, reference_url, requirements,
                    content_mode, local_folder, logo_file, screenshot_files
                )
                
                if success:
                    st.success("✅ Project created successfully!")
                    st.session_state.current_step = 2
                    log_user_action("project_created", {"project_name": project_name})
                    st.rerun()

def _process_project_creation(project_name: str, company_name: str, reference_url: str,
                            requirements: str, content_mode: str, local_folder: str,
                            logo_file, screenshot_files) -> bool:
    """Process project creation"""
    
    try:
        # Create project manager
        project_manager = ProjectManager()
        
        # Prepare project data
        project_data = {
            "project_name": project_name,
            "company_name": company_name,
            "reference_url": reference_url,
            "requirements": requirements,
            "content_mode": content_mode,
            "local_folder": local_folder,
            "logo": "",
            "screenshots": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "status": "step1_complete"
        }
        
        # Create project
        project_path = project_manager.create_project_from_data(project_data)
        
        # Handle file uploads
        if logo_file:
            logo_path = _save_uploaded_file(logo_file, project_path, "logo")
            project_data["logo"] = logo_path
        
        if screenshot_files:
            screenshot_paths = []
            for i, screenshot in enumerate(screenshot_files):
                screenshot_path = _save_uploaded_file(screenshot, project_path, f"screenshot_{i+1}")
                screenshot_paths.append(screenshot_path)
            project_data["screenshots"] = screenshot_paths
        
        # Update project config with file paths
        project_manager.save_project_config(project_data)
        
        # Save form data
        save_form_data(1, project_data)
        
        # Set project state
        set_project_state(project_path, project_data)
        
        return True
        
    except Exception as e:
        st.error(f"Error creating project: {str(e)}")
        return False

def _save_uploaded_file(uploaded_file, project_path: str, prefix: str) -> str:
    """Save uploaded file to project assets"""
    
    assets_path = os.path.join(project_path, "assets")
    if prefix == "logo":
        save_path = os.path.join(assets_path, f"logo_{uploaded_file.name}")
    else:
        screenshots_path = os.path.join(assets_path, "screenshots")
        os.makedirs(screenshots_path, exist_ok=True)
        save_path = os.path.join(screenshots_path, uploaded_file.name)
    
    # Save file
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Return relative path
    return os.path.relpath(save_path, project_path)