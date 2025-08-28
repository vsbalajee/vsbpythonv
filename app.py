import streamlit as st
import os
import json
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from project_manager import ProjectManager
from admin_interface import AdminInterface
from test_runner import TestRunner
from utils import ensure_directory, load_json, save_json
from scaffold_generator import (
    generate_main_app, generate_page, generate_components, 
    generate_tokens, generate_style_injector, generate_seo_utilities
)

st.set_page_config(
    page_title="Vsbvibe Website Builder", 
    page_icon="🚀", 
    layout="wide"
)

# Initialize session state
if 'project_manager' not in st.session_state:
    st.session_state.project_manager = ProjectManager()
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'step' not in st.session_state:
    st.session_state.step = 1

def main():
    st.title("🚀 Vsbvibe Website Builder")
    st.markdown("*Local-first website builder platform*")
    
    # Sidebar for navigation
    with st.sidebar:
        show_sidebar()
    
    # Main content area
    if st.session_state.current_project:
        show_admin_interface()
    else:
        show_step1_wizard()

def show_sidebar():
    st.header("Navigation")
    
    # Help Panel
    with st.expander("📖 VSBVibe User Flow", expanded=False):
        st.markdown("""
        **VSBVibe Website Builder Flow:**
        1. **Setup**: Enter project details, requirements, content mode
        2. **Plan**: AI generates UI/UX plan and page structure  
        3. **Content**: Manage products, pages, and media assets
        4. **Design**: Customize themes, layouts, and components
        5. **Generate**: Create Streamlit or static HTML website
        6. **Test**: Validate structure, content, SEO, performance
        7. **Deploy**: Publish to Streamlit Cloud or export files
        8. **Manage**: Update content, track changes, version control
        9. **Monitor**: Analytics, logs, and maintenance tools
        10. **Scale**: Add features, integrate APIs, optimize performance
        """)
    
    # Project status
    if st.session_state.current_project:
        st.success(f"📁 Project: {st.session_state.current_project}")
        if st.button("🔄 Change Project"):
            st.session_state.current_project = None
            st.session_state.step = 1
            st.rerun()
        
        # Show current step
        st.info(f"Step: {st.session_state.step}/7")
    else:
        st.info("No project loaded")

def show_step1_wizard():
    st.header("Step 1: Project Setup & Requirements")
    st.markdown("Set up your new website project with basic information and requirements.")
    
    with st.form("project_setup_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Basic Information")
            project_name = st.text_input(
                "Project Name *", 
                placeholder="my-awesome-website",
                help="This will be used as the folder name and site identifier"
            )
            
            company_name = st.text_input(
                "Company/Brand Name *", 
                placeholder="My Company Inc.",
                help="Your business or brand name for the website"
            )
            
            reference_url = st.text_input(
                "Reference URL (optional)", 
                placeholder="https://example.com",
                help="An existing website to use as inspiration or reference"
            )
            
            local_folder = st.text_input(
                "Local Folder Path *", 
                value=os.getcwd(),
                help="Where to create your project files"
            )
        
        with col2:
            st.subheader("Content & Assets")
            
            # Logo upload
            logo_file = st.file_uploader(
                "Logo (optional)", 
                type=['png', 'jpg', 'jpeg', 'svg'],
                help="Upload your company logo"
            )
            
            # Screenshots upload
            screenshot_files = st.file_uploader(
                "Reference Screenshots (optional)", 
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Upload 5-10 screenshots of websites you like"
            )
            
            if screenshot_files:
                st.info(f"📸 {len(screenshot_files)} screenshot(s) uploaded")
        
        # Content mode selector
        st.subheader("Content Generation Mode")
        content_mode = st.selectbox(
            "How do you want to create content?",
            ["User Provided", "AI Generated", "Hybrid"],
            help="Choose how website content will be created"
        )
        
        # Content mode descriptions
        mode_descriptions = {
            "User Provided": "You'll manually enter all content, text, and descriptions",
            "AI Generated": "AI will generate content based on your requirements and company info",
            "Hybrid": "Combination of AI-generated content that you can edit and customize"
        }
        st.info(f"💡 {mode_descriptions[content_mode]}")
        
        # Requirements section
        st.subheader("Project Requirements")
        requirements = st.text_area(
            "Describe your website requirements *",
            placeholder="""Example requirements:
- Modern e-commerce website for selling handmade jewelry
- Need product catalog with categories and search
- Customer reviews and testimonials section
- Contact form and about us page
- Mobile-responsive design
- Integration with payment processing
- Blog section for marketing content""",
            height=200,
            help="Be as detailed as possible about what you want your website to include"
        )
        
        # Form submission
        submitted = st.form_submit_button("🚀 Create Project", type="primary")
        
        if submitted:
            # Validation
            errors = []
            if not project_name.strip():
                errors.append("Project Name is required")
            if not company_name.strip():
                errors.append("Company/Brand Name is required")
            if not requirements.strip():
                errors.append("Requirements are required")
            if not local_folder.strip():
                errors.append("Local Folder Path is required")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    # Create project
                    project_data = {
                        "project_name": project_name.strip(),
                        "company_name": company_name.strip(),
                        "reference_url": reference_url.strip() if reference_url.strip() else "",
                        "content_mode": content_mode,
                        "requirements": requirements.strip(),
                        "local_folder": local_folder.strip(),
                        "logo": "",
                        "screenshots": [],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "version": "1.0.0",
                        "status": "setup_complete"
                    }
                    
                    # Handle file uploads
                    if logo_file:
                        project_data["logo"] = f"assets/{logo_file.name}"
                    
                    if screenshot_files:
                        project_data["screenshots"] = [f"assets/screenshots/{f.name}" for f in screenshot_files]
                    
                    # Create project using project manager
                    project_path = st.session_state.project_manager.create_project_from_data(project_data)
                    
                    # Save uploaded files
                    if logo_file or screenshot_files:
                        assets_path = os.path.join(project_path, "assets")
                        ensure_directory(assets_path)
                        
                        if logo_file:
                            with open(os.path.join(assets_path, logo_file.name), "wb") as f:
                                f.write(logo_file.getbuffer())
                        
                        if screenshot_files:
                            screenshots_path = os.path.join(assets_path, "screenshots")
                            ensure_directory(screenshots_path)
                            for screenshot in screenshot_files:
                                with open(os.path.join(screenshots_path, screenshot.name), "wb") as f:
                                    f.write(screenshot.getbuffer())
                    
                    st.session_state.current_project = project_name.strip()
                    st.session_state.step = 2
                    st.success(f"✅ Project '{project_name}' created successfully!")
                    st.success(f"📁 Project files saved to: {project_path}")
                    st.balloons()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error creating project: {str(e)}")
    
    # Load existing project option
    st.markdown("---")
    st.subheader("Or Load Existing Project")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        existing_folder = st.text_input("Existing Project Folder Path")
    with col2:
        st.write("")  # Spacing
        if st.button("📂 Load Project"):
            if existing_folder:
                try:
                    project_name = st.session_state.project_manager.load_project(existing_folder)
                    st.session_state.current_project = project_name
                    st.success(f"✅ Loaded project: {project_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error loading project: {str(e)}")
            else:
                st.error("Please enter a folder path")

def show_admin_interface():
    st.header(f"🛠️ Admin Dashboard - {st.session_state.current_project}")
    
    # Progress indicator
    progress_steps = ["Setup", "Plan", "Content", "Design", "Generate", "Test", "Deploy"]
    current_step = st.session_state.step
    
    cols = st.columns(len(progress_steps))
    for i, step_name in enumerate(progress_steps):
        with cols[i]:
            if i + 1 < current_step:
                st.success(f"✅ {step_name}")
            elif i + 1 == current_step:
                st.info(f"🔄 {step_name}")
            else:
                st.write(f"⏳ {step_name}")
    
    # Admin interface tabs
    admin_tabs = st.tabs([
        "Requirements", "Models & Keys", "Pages", "Design", 
        "Products", "Data", "Generate", "Publish", "Tests", "Jobs & Logs"
    ])
    
    with admin_tabs[0]:
        show_requirements_panel()
    
    with admin_tabs[1]:
        show_models_keys_panel()
    
    with admin_tabs[2]:
        show_pages_panel()
    
    with admin_tabs[3]:
        show_design_panel()
    
    with admin_tabs[4]:
        st.info("Products management will be available in Step 3")
    
    with admin_tabs[5]:
        st.info("Data management will be available in Step 4")
    
    with admin_tabs[6]:
        show_generate_panel()
    
    with admin_tabs[7]:
        st.info("Publishing will be available in Step 6")
    
    with admin_tabs[8]:
        show_tests_panel()
    
    with admin_tabs[9]:
        show_logs_panel()

def show_requirements_panel():
    st.subheader("📋 Requirements Management")
    
    project_config = st.session_state.project_manager.get_project_config()
    if not project_config:
        st.error("No project configuration found")
        return
    
    # Current requirements display
    st.write("**Current Requirements:**")
    current_requirements = project_config.get("requirements", "")
    st.text_area("", value=current_requirements, height=150, disabled=True, key="current_req_display")
    
    # Requirements editing
    with st.expander("✏️ Edit Requirements", expanded=False):
        with st.form("update_requirements"):
            new_requirements = st.text_area(
                "Updated Requirements", 
                value=current_requirements,
                height=200,
                help="Modify your project requirements"
            )
            
            version_note = st.text_input(
                "Version Note (optional)", 
                placeholder="What changed in this update?"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Requirements", type="primary"):
                    if new_requirements.strip():
                        try:
                            # Update requirements with versioning
                            st.session_state.project_manager.update_requirements(
                                new_requirements.strip(), 
                                version_note.strip()
                            )
                            st.success("✅ Requirements updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error updating requirements: {str(e)}")
                    else:
                        st.error("Requirements cannot be empty")
            
            with col2:
                if st.form_submit_button("🔄 Reset to Original"):
                    st.rerun()
    
    # Requirements history
    versions_path = os.path.join(
        st.session_state.project_manager.get_current_project_path(),
        "_vsbvibe", "requirements_versions.json"
    )
    
    if os.path.exists(versions_path):
        with st.expander("📚 Requirements History", expanded=False):
            versions = load_json(versions_path)
            if versions:
                for version in reversed(versions[-5:]):  # Show last 5 versions
                    st.write(f"**Version {version.get('version', 'Unknown')}** - {version.get('timestamp', '')[:19]}")
                    if version.get('note'):
                        st.write(f"*{version.get('note')}*")
                    with st.expander(f"View Version {version.get('version', 'Unknown')}", expanded=False):
                        st.text_area("", value=version.get('requirements', ''), height=100, disabled=True, key=f"version_{version.get('version')}")
            else:
                st.info("No version history available")

def show_models_keys_panel():
    st.subheader("🔑 AI Models & API Keys")
    st.info("Configure your API keys for AI content generation and database integration")
    
    # Load current settings
    settings_path = os.path.join(
        st.session_state.project_manager.get_current_project_path(), 
        "_vsbvibe", "settings.json"
    )
    
    settings = load_json(settings_path) or {}
    
    with st.form("api_keys_form"):
        st.write("**🤖 AI Content Generation**")
        col1, col2 = st.columns(2)
        
        with col1:
            openai_key = st.text_input(
                "OpenAI API Key", 
                value=settings.get("openai_key", ""), 
                type="password",
                help="For GPT-based content generation"
            )
            
            claude_key = st.text_input(
                "Anthropic Claude API Key", 
                value=settings.get("claude_key", ""), 
                type="password",
                help="Alternative AI model for content generation"
            )
        
        with col2:
            gemini_key = st.text_input(
                "Google Gemini API Key", 
                value=settings.get("gemini_key", ""), 
                type="password",
                help="Google's AI model for content generation"
            )
            
            huggingface_key = st.text_input(
                "HuggingFace API Key", 
                value=settings.get("huggingface_key", ""), 
                type="password",
                help="For open-source AI models"
            )
        
        st.write("**🗄️ Database & Storage**")
        col3, col4 = st.columns(2)
        
        with col3:
            supabase_url = st.text_input(
                "Supabase Project URL", 
                value=settings.get("supabase_url", ""),
                help="Your Supabase project URL"
            )
            
            supabase_key = st.text_input(
                "Supabase Anon Key", 
                value=settings.get("supabase_key", ""), 
                type="password",
                help="Supabase anonymous key"
            )
        
        with col4:
            github_token = st.text_input(
                "GitHub Personal Access Token", 
                value=settings.get("github_token", ""), 
                type="password",
                help="For version control and deployment"
            )
            
            netlify_token = st.text_input(
                "Netlify Access Token", 
                value=settings.get("netlify_token", ""), 
                type="password",
                help="For static site deployment"
            )
        
        # Save settings
        if st.form_submit_button("💾 Save API Keys", type="primary"):
            new_settings = {
                "openai_key": openai_key,
                "claude_key": claude_key,
                "gemini_key": gemini_key,
                "huggingface_key": huggingface_key,
                "supabase_url": supabase_url,
                "supabase_key": supabase_key,
                "github_token": github_token,
                "netlify_token": netlify_token,
                "updated_at": datetime.now().isoformat()
            }
            
            if save_json(settings_path, new_settings):
                st.success("✅ API keys saved successfully!")
                # Don't show the actual keys in success message for security
                key_count = sum(1 for v in new_settings.values() if v and v != new_settings["updated_at"])
                st.info(f"🔐 {key_count} API keys configured")
            else:
                st.error("❌ Error saving API keys")
    
    # API key status
    st.write("**🔍 Configuration Status**")
    status_data = []
    
    key_services = {
        "OpenAI": settings.get("openai_key", ""),
        "Claude": settings.get("claude_key", ""),
        "Gemini": settings.get("gemini_key", ""),
        "HuggingFace": settings.get("huggingface_key", ""),
        "Supabase": settings.get("supabase_url", "") and settings.get("supabase_key", ""),
        "GitHub": settings.get("github_token", ""),
        "Netlify": settings.get("netlify_token", "")
    }
    
    for service, configured in key_services.items():
        status_data.append({
            "Service": service,
            "Status": "✅ Configured" if configured else "❌ Not Set",
            "Required": "Yes" if service in ["OpenAI", "Supabase"] else "Optional"
        })
    
    st.dataframe(pd.DataFrame(status_data), use_container_width=True, hide_index=True)

def show_pages_panel():
    st.subheader("📄 Pages Management")
    
    project_path = st.session_state.project_manager.get_current_project_path()
    plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
    
    if not os.path.exists(plan_path):
        st.warning("No plan found. Please complete Step 2 first.")
        return
    
    plan = load_json(plan_path)
    if not plan:
        st.error("Invalid plan file")
        return
    
    pages = plan.get("pages", [])
    
    if pages:
        st.write("**Planned Pages:**")
        
        for page in pages:
            with st.expander(f"{page.get('name', 'Unknown')} ({page.get('slug', '/')})", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Type:** {page.get('type', 'Unknown')}")
                    st.write(f"**Priority:** {page.get('priority', 0)}")
                    st.write(f"**Template:** {page.get('template', 'default')}")
                
                with col2:
                    sections = page.get('sections', [])
                    if sections:
                        st.write("**Sections:**")
                        for section in sections:
                            st.write(f"• {section.get('name', 'Unknown')} ({section.get('type', 'generic')})")
                    else:
                        st.write("No sections defined")
                
                # Show if file exists
                site_path = os.path.join(project_path, "site")
                if os.path.exists(site_path):
                    page_file = f"{page.get('priority', 0):02d}_{page.get('name', 'Unknown').replace(' ', '_')}.py"
                    page_path = os.path.join(site_path, "pages", page_file)
                    
                    if os.path.exists(page_path):
                        st.success("✅ Page file generated")
                        if st.button(f"View {page.get('name', 'Unknown')} Code", key=f"view_{page.get('name', 'Unknown')}"):
                            with open(page_path, 'r') as f:
                                st.code(f.read(), language='python')
                    else:
                        st.info("⏳ Page file not generated yet")
    else:
        st.info("No pages defined in plan")

def show_design_panel():
    st.subheader("🎨 Design Settings")
    
    project_path = st.session_state.project_manager.get_current_project_path()
    plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
    tokens_path = os.path.join(project_path, "site", "styles", "tokens.json")
    
    # Show current brand tokens from plan
    if os.path.exists(plan_path):
        plan = load_json(plan_path)
        if plan and plan.get("brand_tokens"):
            st.write("**Brand Tokens from Plan:**")
            
            brand_tokens = plan["brand_tokens"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Primary Color:** {brand_tokens.get('primary_color', '#007bff')}")
                st.write(f"**Secondary Color:** {brand_tokens.get('secondary_color', '#6c757d')}")
                st.write(f"**Accent Color:** {brand_tokens.get('accent_color', '#28a745')}")
            
            with col2:
                st.write(f"**Font Family:** {brand_tokens.get('font_family', 'Inter, sans-serif')}")
                st.write(f"**Font Weight:** {brand_tokens.get('font_weight', '400')}")
                st.write(f"**Border Radius:** {brand_tokens.get('border_radius', '8px')}")
            
            # Show color swatches
            st.write("**Color Preview:**")
            color_html = f"""
            <div style="display: flex; gap: 10px; margin: 10px 0;">
                <div style="width: 50px; height: 50px; background-color: {brand_tokens.get('primary_color', '#007bff')}; border-radius: 4px; border: 1px solid #ddd;"></div>
                <div style="width: 50px; height: 50px; background-color: {brand_tokens.get('secondary_color', '#6c757d')}; border-radius: 4px; border: 1px solid #ddd;"></div>
                <div style="width: 50px; height: 50px; background-color: {brand_tokens.get('accent_color', '#28a745')}; border-radius: 4px; border: 1px solid #ddd;"></div>
            </div>
            """
            st.markdown(color_html, unsafe_allow_html=True)
    
    # Show generated tokens file status
    if os.path.exists(tokens_path):
        st.success("✅ Design tokens file generated")
        
        tokens = load_json(tokens_path)
        if tokens:
            with st.expander("View Generated Tokens", expanded=False):
                st.json(tokens)
        
        if st.button("🔄 Regenerate Styles"):
            st.info("Style regeneration will be implemented")
    else:
        st.info("⏳ Design tokens not generated yet")
    
    # UI/UX Plan Summary
    if os.path.exists(plan_path):
        plan = load_json(plan_path)
        if plan and plan.get("ui_ux_plan"):
            st.write("**UI/UX Plan:**")
            ui_plan = plan["ui_ux_plan"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Layout:** {ui_plan.get('layout', 'modern')}")
                st.write(f"**Navigation:** {ui_plan.get('navigation', 'header')}")
            
            with col2:
                st.write(f"**Color Scheme:** {ui_plan.get('color_scheme', 'professional')}")
                components = ui_plan.get('components', [])
                st.write(f"**Components:** {', '.join(components) if components else 'None'}")

def show_generate_panel():
    st.subheader("🚀 Site Generation")
    
    # Step 0 - Preflight Check
    project_path = st.session_state.project_manager.get_current_project_path()
    preflight_path = os.path.join(project_path, "_vsbvibe", "logs", "preflight.log")
    
    if not os.path.exists(preflight_path):
        st.error("❌ Preflight validation not passed. Run the validation prompt again before scaffold generation.")
        return
    
    try:
        with open(preflight_path, 'r') as f:
            preflight_content = f.read()
        if "OK" not in preflight_content:
            st.error("❌ Preflight validation not passed. Run the validation prompt again before scaffold generation.")
            return
    except Exception as e:
        st.error(f"❌ Error reading preflight log: {str(e)}")
        return
    
    st.success("✅ Preflight validation passed")
    
    plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
    
    # Load plan to determine platform and mode
    plan = load_json(plan_path)
    if not plan:
        st.error("❌ No valid plan found")
        return
    
    platform_target = plan.get("platform_target", "")
    site_mode = plan.get("site_mode", "")
    
    # Show platform and mode info
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Platform:** {platform_target}")
    with col2:
        st.info(f"**Site Mode:** {site_mode}")
    
    # Check if scaffold exists for current platform
    output_path = os.path.join(project_path, "output", plan.get("project_name", "project"), platform_target)
    scaffold_exists = os.path.exists(output_path)
    
    # Check if plan exists
    if not os.path.exists(plan_path):
        st.error("❌ No plan found. Please complete Step 2 first.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Generation Options:**")
        generate_components = st.checkbox("Generate Components", value=True)
        generate_seo = st.checkbox("Generate SEO Utilities", value=True)
        generate_styles = st.checkbox("Generate Styling System", value=True)
        
    with col2:
        st.write("**Scaffold Status:**")
        if scaffold_exists:
            st.success(f"✅ {platform_target} scaffold exists")
            st.info("Use 'Regenerate' to update existing files")
        else:
            st.info(f"⏳ No {platform_target} scaffold generated yet")
    
    # Generation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"🏗️ Generate {platform_target.title()} Scaffold", type="primary", disabled=scaffold_exists):
            if generate_platform_scaffold(project_path, platform_target, site_mode, generate_components, generate_seo, generate_styles):
                st.success(f"✅ {platform_target} scaffold generated successfully!")
                st.session_state.step = max(st.session_state.step, 3)
                st.rerun()
            else:
                st.error(f"❌ Error generating {platform_target} scaffold")
    
    with col2:
        if st.button("🔄 Regenerate", disabled=not scaffold_exists):
            if generate_platform_scaffold(project_path, platform_target, site_mode, generate_components, generate_seo, generate_styles, regenerate=True):
                st.success(f"✅ {platform_target} scaffold regenerated successfully!")
                st.rerun()
            else:
                st.error(f"❌ Error regenerating {platform_target} scaffold")
    
    with col3:
        if st.button("📋 View Diff Summary"):
            diff_path = os.path.join(project_path, "_vsbvibe", "diff_summary.json")
            if os.path.exists(diff_path):
                diff_data = load_json(diff_path)
                if diff_data:
                    st.json(diff_data)
                else:
                    st.info("No diff data available")
            else:
                st.info("No diff summary found")
    
    # Show generated files
    if scaffold_exists:
        st.write(f"**Generated {platform_target} Files:**")
        
        # List key files based on platform
        if platform_target == "streamlit_site":
            key_files = [
                f"output/{plan.get('project_name', 'project')}/streamlit_site/app.py",
                f"output/{plan.get('project_name', 'project')}/streamlit_site/pages/00_Home.py",
                f"output/{plan.get('project_name', 'project')}/streamlit_site/components/nav.py",
                f"output/{plan.get('project_name', 'project')}/streamlit_site/styles/tokens.json"
            ]
        elif platform_target == "htmljs":
            key_files = [
                f"output/{plan.get('project_name', 'project')}/htmljs/index.html",
                f"output/{plan.get('project_name', 'project')}/htmljs/css/main.css",
                f"output/{plan.get('project_name', 'project')}/htmljs/js/main.js"
            ]
        else:
            key_files = [
                f"output/{plan.get('project_name', 'project')}/reactvite/reactvite_plan.json",
                f"output/{plan.get('project_name', 'project')}/reactvite/README_handoff.md"
            ]
        
        for file_path in key_files:
            full_path = os.path.join(project_path, file_path)
            if os.path.exists(full_path):
                st.success(f"✅ {file_path.split('/')[-1]}")
            else:
                st.error(f"❌ {file_path.split('/')[-1]}")
    
    # Cleanup notice
    cleanup_path = os.path.join(project_path, "_vsbvibe", "cleanup_list.txt")
    if os.path.exists(cleanup_path):
        with st.expander("🧹 Cleanup Required", expanded=False):
            st.warning("Files from other platforms detected. Manual cleanup recommended.")
            with open(cleanup_path, 'r') as f:
                cleanup_files = f.read()
            st.text_area("Files to remove:", cleanup_files, height=100, disabled=True)
    
    # Preview instructions
    preview_path = os.path.join(project_path, "_vsbvibe", "preview.json")
    if os.path.exists(preview_path):
        st.write("**Preview Instructions:**")
        preview_data = load_json(preview_path)
        if preview_data:
            st.info(f"📁 Navigate to: {preview_data.get('directory', 'site/')}")
            st.info(f"🚀 Run: {preview_data.get('command', 'See README')}")
            st.info(f"🌐 URL: {preview_data.get('url', 'http://localhost:8501')}")

def generate_platform_scaffold(project_path: str, platform_target: str, site_mode: str, components: bool = True, seo: bool = True, styles: bool = True, regenerate: bool = False) -> bool:
    """Generate platform-specific scaffold from plan"""
    try:
        # Load plan and project config
        plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
        project_config_path = os.path.join(project_path, "_vsbvibe", "project.json")
        seo_defaults_path = os.path.join(project_path, "_vsbvibe", "seo_defaults.json")
        
        plan = load_json(plan_path)
        project_config = load_json(project_config_path)
        seo_defaults = load_json(seo_defaults_path)
        
        if not all([plan, project_config, seo_defaults]):
            return False
        
        # Create output directory structure
        project_name = project_config.get("project_name", "project")
        output_base = os.path.join(project_path, "output", project_name)
        platform_path = os.path.join(output_base, platform_target)
        
        # Check for cleanup (other platform files)
        cleanup_files = []
        for other_platform in ["htmljs", "streamlit_site", "reactvite"]:
            if other_platform != platform_target:
                other_path = os.path.join(output_base, other_platform)
                if os.path.exists(other_path):
                    cleanup_files.append(f"output/{project_name}/{other_platform}/")
        
        if cleanup_files:
            cleanup_path = os.path.join(project_path, "_vsbvibe", "cleanup_list.txt")
            with open(cleanup_path, 'w') as f:
                f.write("\n".join(cleanup_files))
        
        # Track generated files for diff
        generated_files = []
        
        # Branch by platform_target
        if platform_target == "htmljs":
            generated_files = generate_htmljs_scaffold(platform_path, plan, project_config, seo_defaults, site_mode, components, seo, styles)
        elif platform_target == "streamlit_site":
            generated_files = generate_streamlit_scaffold(platform_path, plan, project_config, seo_defaults, site_mode, components, seo, styles)
        elif platform_target == "reactvite":
            generated_files = generate_reactvite_handoff(platform_path, plan, project_config, seo_defaults, site_mode)
        else:
            return False
        
        # Generate preview instructions
        preview_data = generate_preview_instructions(platform_target, project_name)
        preview_path = os.path.join(project_path, "_vsbvibe", "preview.json")
        save_json(preview_path, preview_data)
        
        # Generate diff summary
        diff_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": "regenerate" if regenerate else "generate",
            "platform_target": platform_target,
            "site_mode": site_mode,
            "files_created": generated_files,
            "files_updated": [],
            "total_files": len(generated_files)
        }
        diff_path = os.path.join(project_path, "_vsbvibe", "diff_summary.json")
        save_json(diff_path, diff_data)
        
        # Log scaffold generation
        log_path = os.path.join(project_path, "_vsbvibe", "logs", "scaffold.log")
        ensure_directory(os.path.dirname(log_path))
        with open(log_path, 'a') as f:
            f.write(f"{datetime.now().isoformat()}: Generated {platform_target} scaffold with {len(generated_files)} files\n")
        
        return True
        
    except Exception as e:
        print(f"Error generating {platform_target} scaffold: {e}")
        return False

def generate_htmljs_scaffold(platform_path: str, plan: Dict[str, Any], project_config: Dict[str, Any], seo_defaults: Dict[str, Any], site_mode: str, components: bool, seo: bool, styles: bool) -> List[str]:
    """Generate HTML/JS static website scaffold"""
    generated_files = []
    
    # Create directory structure
    directories = ["css", "js", "assets", "public"]
    for directory in directories:
        ensure_directory(os.path.join(platform_path, directory))
    
    # Generate index.html (Home page)
    index_content = generate_html_page("Home", plan, project_config, seo_defaults)
    index_path = os.path.join(platform_path, "index.html")
    with open(index_path, 'w') as f:
        f.write(index_content)
    generated_files.append("index.html")
    
    # Generate other pages from plan
    pages = plan.get("pages", [])
    for page in pages:
        if page.get("slug") != "/":  # Skip home page
            page_name = page.get("name", "page").lower().replace(" ", "")
            page_content = generate_html_page(page.get("name", "Page"), plan, project_config, seo_defaults, page)
            page_path = os.path.join(platform_path, f"{page_name}.html")
            with open(page_path, 'w') as f:
                f.write(page_content)
            generated_files.append(f"{page_name}.html")
    
    # Generate ecommerce pages if needed
    if site_mode == "ecommerce" and plan.get("entities", {}).get("products", False):
        # Shop page (PLP)
        shop_content = generate_html_shop_page(plan, project_config, seo_defaults)
        shop_path = os.path.join(platform_path, "shop.html")
        with open(shop_path, 'w') as f:
            f.write(shop_content)
        generated_files.append("shop.html")
        
        # Product page (PDP)
        product_content = generate_html_product_page(plan, project_config, seo_defaults)
        product_path = os.path.join(platform_path, "product.html")
        with open(product_path, 'w') as f:
            f.write(product_content)
        generated_files.append("product.html")
        
        # Search page
        search_content = generate_html_search_page(plan, project_config, seo_defaults)
        search_path = os.path.join(platform_path, "search.html")
        with open(search_path, 'w') as f:
            f.write(search_content)
        generated_files.append("search.html")
    
    # Generate CSS
    if styles:
        css_content = generate_html_css(plan)
        css_path = os.path.join(platform_path, "css", "main.css")
        with open(css_path, 'w') as f:
            f.write(css_content)
        generated_files.append("css/main.css")
    
    # Generate JavaScript
    js_content = generate_html_js(plan, site_mode)
    js_path = os.path.join(platform_path, "js", "main.js")
    with open(js_path, 'w') as f:
        f.write(js_content)
    generated_files.append("js/main.js")
    
    # Generate SEO exports
    if seo:
        # Sitemap
        sitemap_content = generate_html_sitemap(plan, project_config)
        sitemap_path = os.path.join(platform_path, "public", "sitemap.xml")
        with open(sitemap_path, 'w') as f:
            f.write(sitemap_content)
        generated_files.append("public/sitemap.xml")
        
        # Robots.txt
        robots_content = generate_html_robots(project_config)
        robots_path = os.path.join(platform_path, "public", "robots.txt")
        with open(robots_path, 'w') as f:
            f.write(robots_content)
        generated_files.append("public/robots.txt")
    
    return generated_files

def generate_streamlit_scaffold(platform_path: str, plan: Dict[str, Any], project_config: Dict[str, Any], seo_defaults: Dict[str, Any], site_mode: str, components: bool, seo: bool, styles: bool) -> List[str]:
    """Generate Streamlit website scaffold"""
    generated_files = []
    
    # Create directory structure
    directories = ["pages", "components", "styles", "seo", "utils", "assets", "_public"]
    for directory in directories:
        ensure_directory(os.path.join(platform_path, directory))
    
    # Generate main app.py
    app_content = generate_main_app(plan, project_config)
    app_path = os.path.join(platform_path, "app.py")
    with open(app_path, 'w') as f:
        f.write(app_content)
    generated_files.append("app.py")
    
    # Generate pages
    pages = plan.get("pages", [])
    for page in pages:
        page_content = generate_page(page, plan, project_config)
        page_filename = f"{page.get('priority', 0):02d}_{page.get('name', 'Unknown').replace(' ', '_')}.py"
        page_path = os.path.join(platform_path, "pages", page_filename)
        
        with open(page_path, 'w') as f:
            f.write(page_content)
        generated_files.append(f"pages/{page_filename}")
    
    # Generate ecommerce pages if needed
    if site_mode == "ecommerce" and plan.get("entities", {}).get("products", False):
        # Shop page (PLP)
        shop_content = generate_streamlit_shop_page(plan, project_config)
        shop_path = os.path.join(platform_path, "pages", "10_Shop.py")
        with open(shop_path, 'w') as f:
            f.write(shop_content)
        generated_files.append("pages/10_Shop.py")
        
        # Product page (PDP)
        product_content = generate_streamlit_product_page(plan, project_config)
        product_path = os.path.join(platform_path, "pages", "20_Product.py")
        with open(product_path, 'w') as f:
            f.write(product_content)
        generated_files.append("pages/20_Product.py")
        
        # Search page
        search_content = generate_streamlit_search_page(plan, project_config)
        search_path = os.path.join(platform_path, "pages", "30_Search.py")
        with open(search_path, 'w') as f:
            f.write(search_content)
        generated_files.append("pages/30_Search.py")
    
    # Generate components
    if components:
        component_files = generate_components(plan, project_config)
        for filename, content in component_files.items():
            comp_path = os.path.join(platform_path, "components", filename)
            with open(comp_path, 'w') as f:
                f.write(content)
            generated_files.append(f"components/{filename}")
    
    # Generate styles
    if styles:
        tokens_content = generate_tokens(plan)
        tokens_path = os.path.join(platform_path, "styles", "tokens.json")
        save_json(tokens_path, tokens_content)
        generated_files.append("styles/tokens.json")
        
        inject_content = generate_style_injector(plan)
        inject_path = os.path.join(platform_path, "styles", "inject.py")
        with open(inject_path, 'w') as f:
            f.write(inject_content)
        generated_files.append("styles/inject.py")
    
    # Generate SEO utilities
    if seo:
        seo_files = generate_seo_utilities(seo_defaults, project_config)
        for filename, content in seo_files.items():
            seo_path = os.path.join(platform_path, "seo", filename)
            with open(seo_path, 'w') as f:
                f.write(content)
            generated_files.append(f"seo/{filename}")
        
        # Export sitemap and robots
        sitemap_content = generate_streamlit_sitemap(plan, project_config)
        sitemap_path = os.path.join(platform_path, "_public", "sitemap.xml")
        with open(sitemap_path, 'w') as f:
            f.write(sitemap_content)
        generated_files.append("_public/sitemap.xml")
        
        robots_content = generate_streamlit_robots(project_config)
        robots_path = os.path.join(platform_path, "_public", "robots.txt")
        with open(robots_path, 'w') as f:
            f.write(robots_content)
        generated_files.append("_public/robots.txt")
    
    return generated_files

def generate_reactvite_handoff(platform_path: str, plan: Dict[str, Any], project_config: Dict[str, Any], seo_defaults: Dict[str, Any], site_mode: str) -> List[str]:
    """Generate React/Vite handoff documentation (no code)"""
    generated_files = []
    
    ensure_directory(platform_path)
    
    # Generate handoff plan
    handoff_plan = {
        "platform": "reactvite",
        "site_mode": site_mode,
        "project_name": project_config.get("project_name", "project"),
        "company_name": project_config.get("company_name", "Company"),
        "routes": [],
        "components": [],
        "data_flow": {
            "database": "supabase",
            "auth": "supabase_auth",
            "storage": "supabase_storage"
        },
        "seo_requirements": seo_defaults,
        "brand_tokens": plan.get("brand_tokens", {}),
        "pages": plan.get("pages", []),
        "navigation": plan.get("navigation", {}),
        "generated_at": datetime.now().isoformat()
    }
    
    # Extract routes from pages
    for page in plan.get("pages", []):
        handoff_plan["routes"].append({
            "path": page.get("slug", "/"),
            "component": f"{page.get('name', 'Page').replace(' ', '')}Page",
            "sections": page.get("sections", [])
        })
    
    # Define required components
    handoff_plan["components"] = [
        "Header", "Footer", "Hero", "ProductCard", "ContactForm", 
        "SearchBar", "Breadcrumbs", "Newsletter", "Testimonials"
    ]
    
    plan_path = os.path.join(platform_path, "reactvite_plan.json")
    save_json(plan_path, handoff_plan)
    generated_files.append("reactvite_plan.json")
    
    # Generate README handoff
    readme_content = f"""# {project_config.get('project_name', 'Project')} - React/Vite Implementation Guide

## Project Overview
- **Company:** {project_config.get('company_name', 'Company')}
- **Site Mode:** {site_mode}
- **Platform:** React + Vite + TypeScript

## Implementation Requirements

### 1. Setup
```bash
npm create vite@latest {project_config.get('project_name', 'project')} --template react-ts
cd {project_config.get('project_name', 'project')}
npm install
```

### 2. Required Dependencies
```bash
npm install @supabase/supabase-js
npm install react-router-dom
npm install @headlessui/react
npm install tailwindcss
```

### 3. Pages to Implement
{chr(10).join([f"- {page.get('name', 'Page')} ({page.get('slug', '/')})" for page in plan.get('pages', [])])}

### 4. Components Required
{chr(10).join([f"- {comp}" for comp in handoff_plan["components"]])}

### 5. Brand Tokens
- Primary Color: {plan.get('brand_tokens', {}).get('primary_color', '#007bff')}
- Font Family: {plan.get('brand_tokens', {}).get('font_family', 'Inter, sans-serif')}
- Border Radius: {plan.get('brand_tokens', {}).get('border_radius', '8px')}

### 6. SEO Requirements
- JSON-LD Schema: Organization, Product, Breadcrumbs
- Meta tags for all pages
- Sitemap.xml generation
- Robots.txt configuration

### 7. Data Integration
- Supabase for database
- Authentication with Supabase Auth
- File storage with Supabase Storage

## Next Steps
1. Review the reactvite_plan.json for detailed specifications
2. Set up the development environment
3. Implement pages and components according to the plan
4. Integrate with Supabase for data and authentication
5. Implement SEO utilities and meta tag management

## Notes
This is a handoff document. No React/Vite code is generated by VSBVibe.
Use this plan as a blueprint for your React implementation.
"""
    
    readme_path = os.path.join(platform_path, "README_handoff.md")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    generated_files.append("README_handoff.md")
    
    return generated_files

def generate_preview_instructions(platform_target: str, project_name: str) -> Dict[str, Any]:
    """Generate platform-specific preview instructions"""
    if platform_target == "streamlit_site":
        return {
            "platform": platform_target,
            "directory": f"output/{project_name}/streamlit_site/",
            "command": "streamlit run app.py",
            "url": "http://localhost:8501",
            "notes": "Navigate to the streamlit_site directory and run the command",
            "generated_at": datetime.now().isoformat()
        }
    elif platform_target == "htmljs":
        return {
            "platform": platform_target,
            "directory": f"output/{project_name}/htmljs/",
            "command": "python -m http.server 8000",
            "url": "http://localhost:8000",
            "notes": "Navigate to the htmljs directory and serve static files",
            "generated_at": datetime.now().isoformat()
        }
    else:  # reactvite
        return {
            "platform": platform_target,
            "directory": f"output/{project_name}/reactvite/",
            "command": "See README_handoff.md",
            "url": "Implementation required",
            "notes": "This is a handoff - no code generated. Follow README_handoff.md",
            "generated_at": datetime.now().isoformat()
        }

# HTML Generation Functions
def generate_html_page(title: str, plan: Dict[str, Any], project_config: Dict[str, Any], seo_defaults: Dict[str, Any], page_data: Dict[str, Any] = None) -> str:
    """Generate HTML page content"""
    brand_tokens = plan.get("brand_tokens", {})
    company_name = project_config.get("company_name", "Company")
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {company_name}</title>
    <meta name="description" content="Welcome to {company_name}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/main.css">
    
    <!-- JSON-LD Schema -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "{company_name}",
        "url": "https://example.com"
    }}
    </script>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="nav-brand">{company_name}</div>
            <ul class="nav-links">
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main">
        <section class="hero">
            <div class="container">
                <h1>{title}</h1>
                <p>Welcome to our {title.lower()} page</p>
                <button class="btn btn-primary">Get Started</button>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {company_name}. All rights reserved.</p>
        </div>
    </footer>
    
    <script src="js/main.js"></script>
</body>
</html>"""

def generate_html_shop_page(plan: Dict[str, Any], project_config: Dict[str, Any], seo_defaults: Dict[str, Any]) -> str:
    """Generate HTML shop page"""
    company_name = project_config.get("company_name", "Company")
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shop - {company_name}</title>
    <meta name="description" content="Browse our products at {company_name}">
    <link rel="stylesheet" href="css/main.css">
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="nav-brand">{company_name}</div>
            <ul class="nav-links">
                <li><a href="index.html">Home</a></li>
                <li><a href="shop.html" class="active">Shop</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main">
        <section class="shop-header">
            <div class="container">
                <h1>Our Products</h1>
                <div class="shop-filters">
                    <input type="search" placeholder="Search products..." class="search-input">
                    <select class="filter-select">
                        <option>All Categories</option>
                        <option>Category 1</option>
                        <option>Category 2</option>
                    </select>
                </div>
            </div>
        </section>
        
        <section class="products-grid">
            <div class="container">
                <div class="grid">
                    <!-- Products will be loaded here -->
                    <div class="product-card">
                        <img src="https://via.placeholder.com/300x200" alt="Product" loading="lazy">
                        <h3>Sample Product</h3>
                        <p class="price">$99.99</p>
                        <button class="btn btn-primary">View Details</button>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {company_name}. All rights reserved.</p>
        </div>
    </footer>
    
    <script src="js/main.js"></script>
</body>
</html>"""

def generate_html_product_page(plan: Dict[str, Any], project_config: Dict[str, Any], seo_defaults: Dict[str, Any]) -> str:
    """Generate HTML product detail page"""
    company_name = project_config.get("company_name", "Company")
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Details - {company_name}</title>
    <meta name="description" content="Product details at {company_name}">
    <link rel="stylesheet" href="css/main.css">
    
    <!-- Product JSON-LD -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Sample Product",
        "description": "A great product",
        "offers": {{
            "@type": "Offer",
            "price": "99.99",
            "priceCurrency": "USD"
        }}
    }}
    </script>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="nav-brand">{company_name}</div>
            <ul class="nav-links">
                <li><a href="index.html">Home</a></li>
                <li><a href="shop.html">Shop</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main">
        <section class="product-detail">
            <div class="container">
                <div class="product-layout">
                    <div class="product-images">
                        <img src="https://via.placeholder.com/500x400" alt="Product" loading="lazy">
                    </div>
                    <div class="product-info">
                        <h1>Sample Product</h1>
                        <p class="price">$99.99</p>
                        <p class="description">This is a detailed product description.</p>
                        <button class="btn btn-primary btn-large">Add to Cart</button>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {company_name}. All rights reserved.</p>
        </div>
    </footer>
    
    <script src="js/main.js"></script>
</body>
</html>"""

def generate_html_search_page(plan: Dict[str, Any], project_config: Dict[str, Any], seo_defaults: Dict[str, Any]) -> str:
    """Generate HTML search page"""
    company_name = project_config.get("company_name", "Company")
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search - {company_name}</title>
    <meta name="description" content="Search products at {company_name}">
    <link rel="stylesheet" href="css/main.css">
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="nav-brand">{company_name}</div>
            <ul class="nav-links">
                <li><a href="index.html">Home</a></li>
                <li><a href="shop.html">Shop</a></li>
                <li><a href="search.html" class="active">Search</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main class="main">
        <section class="search-section">
            <div class="container">
                <h1>Search Products</h1>
                <div class="search-form">
                    <input type="search" placeholder="What are you looking for?" class="search-input-large">
                    <button class="btn btn-primary">Search</button>
                </div>
                <div id="search-results" class="search-results">
                    <!-- Search results will appear here -->
                </div>
            </div>
        </section>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {company_name}. All rights reserved.</p>
        </div>
    </footer>
    
    <script src="js/main.js"></script>
</body>
</html>"""

def generate_html_css(plan: Dict[str, Any]) -> str:
    """Generate main CSS file for HTML/JS scaffold"""
    brand_tokens = plan.get("brand_tokens", {})
    primary_color = brand_tokens.get("primary_color", "#007bff")
    font_family = brand_tokens.get("font_family", "Inter, sans-serif")
    
    return f"""/* Main CSS for HTML/JS Scaffold */

/* Reset and Base Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: {font_family};
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}}

/* Header and Navigation */
.header {{
    background: #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}}

.nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
}}

.nav-brand {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {primary_color};
    text-decoration: none;
}}

.nav-links {{
    display: flex;
    list-style: none;
    gap: 2rem;
}}

.nav-links a {{
    text-decoration: none;
    color: #333;
    font-weight: 500;
    transition: color 0.2s;
}}

.nav-links a:hover,
.nav-links a.active {{
    color: {primary_color};
}}

/* Main Content */
.main {{
    min-height: calc(100vh - 200px);
}}

/* Hero Section */
.hero {{
    background: linear-gradient(135deg, {primary_color}15, {primary_color}05);
    padding: 4rem 0;
    text-align: center;
}}

.hero h1 {{
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #333;
}}

.hero p {{
    font-size: 1.25rem;
    margin-bottom: 2rem;
    color: #666;
}}

/* Buttons */
.btn {{
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 1rem;
}}

.btn-primary {{
    background: {primary_color};
    color: white;
}}

.btn-primary:hover {{
    background: {primary_color}dd;
    transform: translateY(-1px);
}}

.btn-large {{
    padding: 1rem 2rem;
    font-size: 1.125rem;
}}

/* Grid Layouts */
.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}}

/* Product Cards */
.product-card {{
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: transform 0.2s;
}}

.product-card:hover {{
    transform: translateY(-4px);
}}

.product-card img {{
    width: 100%;
    height: 200px;
    object-fit: cover;
}}

.product-card h3 {{
    padding: 1rem;
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
}}

.product-card .price {{
    padding: 0 1rem;
    font-size: 1.5rem;
    font-weight: 600;
    color: {primary_color};
    margin-bottom: 1rem;
}}

.product-card .btn {{
    margin: 0 1rem 1rem;
    width: calc(100% - 2rem);
}}

/* Forms */
.search-input,
.search-input-large {{
    padding: 0.75rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 1rem;
    width: 100%;
    max-width: 400px;
}}

.search-input-large {{
    font-size: 1.125rem;
    padding: 1rem;
}}

.filter-select {{
    padding: 0.75rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 1rem;
    background: white;
}}

/* Shop Specific */
.shop-header {{
    padding: 2rem 0;
    background: #f8f9fa;
}}

.shop-filters {{
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}}

.products-grid {{
    padding: 2rem 0;
}}

/* Product Detail */
.product-detail {{
    padding: 2rem 0;
}}

.product-layout {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: start;
}}

.product-images img {{
    width: 100%;
    border-radius: 12px;
}}

.product-info h1 {{
    font-size: 2rem;
    margin-bottom: 1rem;
}}

.product-info .price {{
    font-size: 2rem;
    font-weight: 600;
    color: {primary_color};
    margin-bottom: 1rem;
}}

.product-info .description {{
    font-size: 1.125rem;
    line-height: 1.6;
    margin-bottom: 2rem;
    color: #666;
}}

/* Search */
.search-section {{
    padding: 2rem 0;
}}

.search-form {{
    display: flex;
    gap: 1rem;
    margin: 2rem 0;
    flex-wrap: wrap;
}}

.search-results {{
    margin-top: 2rem;
}}

/* Footer */
.footer {{
    background: #333;
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 4rem;
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .nav {{
        flex-direction: column;
        gap: 1rem;
    }}
    
    .nav-links {{
        gap: 1rem;
    }}
    
    .hero h1 {{
        font-size: 2rem;
    }}
    
    .product-layout {{
        grid-template-columns: 1fr;
        gap: 2rem;
    }}
    
    .shop-filters {{
        flex-direction: column;
    }}
    
    .search-form {{
        flex-direction: column;
    }}
}}

/* Accessibility */
.btn:focus,
.search-input:focus,
.search-input-large:focus,
.filter-select:focus {{
    outline: 2px solid {primary_color};
    outline-offset: 2px;
}}

/* Loading States */
.loading {{
    opacity: 0.6;
    pointer-events: none;
}}

/* Utility Classes */
.text-center {{ text-align: center; }}
.text-left {{ text-align: left; }}
.text-right {{ text-align: right; }}
.mb-1 {{ margin-bottom: 0.5rem; }}
.mb-2 {{ margin-bottom: 1rem; }}
.mb-3 {{ margin-bottom: 1.5rem; }}
.mt-1 {{ margin-top: 0.5rem; }}
.mt-2 {{ margin-top: 1rem; }}
.mt-3 {{ margin-top: 1.5rem; }}
"""

def generate_html_js(plan: Dict[str, Any], site_mode: str) -> str:
    """Generate main JavaScript file for HTML/JS scaffold"""
    return f"""// Main JavaScript for HTML/JS Scaffold

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {{
    console.log('Website loaded successfully');
    
    // Initialize components
    initializeNavigation();
    initializeSearch();
    {f"initializeEcommerce();" if site_mode == "ecommerce" else ""}
    
    // Initialize lazy loading
    initializeLazyLoading();
}});

// Navigation functionality
function initializeNavigation() {{
    const navLinks = document.querySelectorAll('.nav-links a');
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    navLinks.forEach(link => {{
        if (link.getAttribute('href') === currentPage) {{
            link.classList.add('active');
        }}
    }});
}}

// Search functionality
function initializeSearch() {{
    const searchInputs = document.querySelectorAll('.search-input, .search-input-large');
    
    searchInputs.forEach(input => {{
        input.addEventListener('input', debounce(handleSearch, 300));
    }});
}}

function handleSearch(event) {{
    const query = event.target.value.toLowerCase();
    console.log('Searching for:', query);
    
    // TODO: Implement actual search functionality
    // This would typically make an API call or filter existing content
}}

// Ecommerce functionality
{f'''function initializeEcommerce() {{
    // Add to cart buttons
    const addToCartButtons = document.querySelectorAll('.btn-primary');
    
    addToCartButtons.forEach(button => {{
        if (button.textContent.includes('Add to Cart')) {{
            button.addEventListener('click', handleAddToCart);
        }}
    }});
    
    // Product filters
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {{
        select.addEventListener('change', handleFilterChange);
    }});
}}

function handleAddToCart(event) {{
    event.preventDefault();
    const button = event.target;
    
    // Simulate add to cart
    button.textContent = 'Added!';
    button.style.background = '#28a745';
    
    setTimeout(() => {{
        button.textContent = 'Add to Cart';
        button.style.background = '';
    }}, 2000);
    
    console.log('Product added to cart');
}}

function handleFilterChange(event) {{
    const selectedCategory = event.target.value;
    console.log('Filter changed to:', selectedCategory);
    
    // TODO: Implement product filtering
    // This would typically filter the product grid
}}''' if site_mode == "ecommerce" else ""}

// Lazy loading for images
function initializeLazyLoading() {{
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {{
        const imageObserver = new IntersectionObserver((entries, observer) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    const img = entry.target;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }}
            }});
        }});
        
        images.forEach(img => imageObserver.observe(img));
    }}
}}

// Utility functions
function debounce(func, wait) {{
    let timeout;
    return function executedFunction(...args) {{
        const later = () => {{
            clearTimeout(timeout);
            func(...args);
        }};
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    }};
}}

// Form handling
function handleFormSubmit(event) {{
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    console.log('Form submitted:', Object.fromEntries(formData));
    
    // TODO: Implement actual form submission
    // This would typically send data to a server
}}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
    anchor.addEventListener('click', function (e) {{
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {{
            target.scrollIntoView({{
                behavior: 'smooth',
                block: 'start'
            }});
        }}
    }});
}});

// Mobile menu toggle (if needed)
function toggleMobileMenu() {{
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('mobile-open');
}}

// Error handling
window.addEventListener('error', function(event) {{
    console.error('JavaScript error:', event.error);
}});

// Performance monitoring
window.addEventListener('load', function() {{
    if ('performance' in window) {{
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log('Page load time:', loadTime + 'ms');
    }}
}});
"""

def generate_html_sitemap(plan: Dict[str, Any], project_config: Dict[str, Any]) -> str:
    """Generate sitemap.xml for HTML/JS scaffold"""
    base_url = "https://example.com"  # TODO: Get from config
    pages = plan.get("pages", [])
    
    sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    
    # Add home page
    sitemap_content += f'''    <url>
        <loc>{base_url}/</loc>
        <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
'''
    
    # Add other pages
    for page in pages:
        if page.get("slug") != "/":
            page_name = page.get("name", "page").lower().replace(" ", "")
            sitemap_content += f'''    <url>
        <loc>{base_url}/{page_name}.html</loc>
        <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
'''
    
    sitemap_content += '</urlset>'
    return sitemap_content

def generate_html_robots(project_config: Dict[str, Any]) -> str:
    """Generate robots.txt for HTML/JS scaffold"""
    return f"""User-agent: *
Allow: /

Sitemap: https://example.com/public/sitemap.xml

# Generated by VSBVibe for {project_config.get('project_name', 'Project')}
"""

# Streamlit-specific generation functions
def generate_streamlit_shop_page(plan: Dict[str, Any], project_config: Dict[str, Any]) -> str:
    """Generate Streamlit shop page"""
    return '''import streamlit as st
import sys
import os

# Add components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'styles'))

from nav import render_navigation
from footer import render_footer
from inject import inject_global_styles
from product_card import render_product_grid

st.set_page_config(
    page_title="Shop - Your Store",
    page_icon="🛍️",
    layout="wide"
)

def main():
    """Shop page - Product List Page (PLP)"""
    
    # Inject global styles
    inject_global_styles()
    
    # Render navigation
    render_navigation()
    
    # Shop header
    st.title("🛍️ Our Products")
    st.write("Discover our amazing collection of products")
    
    # Search and filters
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search products...", placeholder="Enter product name")
    
    with col2:
        category = st.selectbox("Category", ["All", "Category A", "Category B", "Category C"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Name", "Price", "Popularity", "Newest"])
    
    st.markdown("---")
    
    # Sample products (TODO: Replace with real data in Step 5)
    sample_products = [
        {
            "id": 1,
            "name": "Premium Product 1",
            "price": "$99.99",
            "description": "High-quality product with excellent features",
            "image": "https://via.placeholder.com/300x200/007bff/ffffff?text=Product+1"
        },
        {
            "id": 2,
            "name": "Premium Product 2", 
            "price": "$149.99",
            "description": "Advanced product with premium materials",
            "image": "https://via.placeholder.com/300x200/28a745/ffffff?text=Product+2"
        },
        {
            "id": 3,
            "name": "Premium Product 3",
            "price": "$79.99", 
            "description": "Affordable quality with great value",
            "image": "https://via.placeholder.com/300x200/dc3545/ffffff?text=Product+3"
        },
        {
            "id": 4,
            "name": "Premium Product 4",
            "price": "$199.99",
            "description": "Top-tier product with exclusive features", 
            "image": "https://via.placeholder.com/300x200/ffc107/ffffff?text=Product+4"
        }
    ]
    
    # Filter products based on search and category
    filtered_products = sample_products
    if search_term:
        filtered_products = [p for p in filtered_products if search_term.lower() in p["name"].lower()]
    
    if category != "All":
        # TODO: Implement category filtering when real data is available
        pass
    
    # Display products
    if filtered_products:
        render_product_grid(filtered_products, columns=2)
    else:
        st.info("No products found matching your criteria.")
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
'''

def generate_streamlit_product_page(plan: Dict[str, Any], project_config: Dict[str, Any]) -> str:
    """Generate Streamlit product detail page"""
    return '''import streamlit as st
import sys
import os

# Add components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'styles'))

from nav import render_navigation
from footer import render_footer
from inject import inject_global_styles

st.set_page_config(
    page_title="Product Details - Your Store",
    page_icon="📦",
    layout="wide"
)

def main():
    """Product Detail Page (PDP)"""
    
    # Inject global styles
    inject_global_styles()
    
    # Render navigation
    render_navigation()
    
    # Breadcrumb navigation
    st.markdown("🏠 [Home](/) > [Shop](/Shop) > Product Details")
    
    # Product details layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Product images
        st.image("https://via.placeholder.com/500x400/007bff/ffffff?text=Product+Image", 
                caption="Product Main Image")
        
        # Thumbnail gallery
        st.write("**More Images:**")
        thumb_cols = st.columns(4)
        for i in range(4):
            with thumb_cols[i]:
                if st.button(f"📷", key=f"thumb_{i}"):
                    st.info(f"Viewing image {i+1}")
                st.image(f"https://via.placeholder.com/100x80/6c757d/ffffff?text=Thumb+{i+1}")
    
    with col2:
        # Product information
        st.header("Premium Sample Product")
        st.subheader("$149.99")
        
        # Product rating
        st.write("⭐⭐⭐⭐⭐ (4.8/5) - 127 reviews")
        
        st.write("""
        **Product Description:**
        
        This is a premium quality product designed with attention to detail 
        and crafted from the finest materials. It offers exceptional value 
        and performance for discerning customers.
        
        **Key Features:**
        - Premium materials and construction
        - Exceptional durability and reliability  
        - Modern design and functionality
        - Satisfaction guarantee
        """)
        
        # Product options
        st.write("**Product Options:**")
        col_a, col_b = st.columns(2)
        
        with col_a:
            size = st.selectbox("Size", ["Small", "Medium", "Large", "X-Large"])
            color = st.selectbox("Color", ["Black", "White", "Blue", "Red"])
        
        with col_b:
            quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1)
            shipping = st.selectbox("Shipping", ["Standard (5-7 days)", "Express (2-3 days)", "Overnight"])
        
        # Action buttons
        st.markdown("---")
        col_x, col_y, col_z = st.columns(3)
        
        with col_x:
            if st.button("🛒 Add to Cart", type="primary"):
                st.success("Added to cart!")
                st.balloons()
        
        with col_y:
            if st.button("💝 Add to Wishlist"):
                st.info("Added to wishlist!")
        
        with col_z:
            if st.button("🚀 Buy Now"):
                st.info("Redirecting to checkout...")
    
    # Product details tabs
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Description", "📊 Specifications", "⭐ Reviews", "❓ FAQ"])
    
    with tab1:
        st.write("""
        **Detailed Product Description**
        
        This premium product represents the perfect blend of quality, functionality, 
        and style. Carefully designed and meticulously crafted, it meets the highest 
        standards of excellence.
        
        **Materials & Construction:**
        - Premium grade materials sourced from trusted suppliers
        - Advanced manufacturing processes ensure consistency
        - Rigorous quality control at every stage
        - Environmentally conscious production methods
        
        **Design Philosophy:**
        Our design team focused on creating a product that not only performs 
        exceptionally but also enhances your daily experience. Every detail 
        has been considered to provide maximum value and satisfaction.
        """)
    
    with tab2:
        st.write("**Technical Specifications:**")
        
        specs_data = {
            "Dimensions": "10\" x 8\" x 2\"",
            "Weight": "2.5 lbs",
            "Material": "Premium grade composite",
            "Color Options": "Black, White, Blue, Red",
            "Warranty": "2 years manufacturer warranty",
            "Certifications": "ISO 9001, CE Marked",
            "Country of Origin": "Made in USA"
        }
        
        for spec, value in specs_data.items():
            col_spec, col_val = st.columns([1, 2])
            with col_spec:
                st.write(f"**{spec}:**")
            with col_val:
                st.write(value)
    
    with tab3:
        st.write("**Customer Reviews & Ratings**")
        
        # Review summary
        col_rating, col_breakdown = st.columns([1, 2])
        
        with col_rating:
            st.metric("Average Rating", "4.8/5", "⭐⭐⭐⭐⭐")
            st.write("Based on 127 reviews")
        
        with col_breakdown:
            st.write("**Rating Breakdown:**")
            st.progress(0.85, text="5 stars (85%)")
            st.progress(0.10, text="4 stars (10%)")
            st.progress(0.03, text="3 stars (3%)")
            st.progress(0.01, text="2 stars (1%)")
            st.progress(0.01, text="1 star (1%)")
        
        # Sample reviews
        reviews = [
            {
                "name": "Sarah M.",
                "rating": 5,
                "date": "2024-01-15",
                "comment": "Absolutely love this product! Exceeded my expectations in every way. The quality is outstanding and it arrived quickly."
            },
            {
                "name": "John D.",
                "rating": 5,
                "date": "2024-01-10", 
                "comment": "Perfect for my needs. Great build quality and excellent customer service. Highly recommended!"
            },
            {
                "name": "Emily R.",
                "rating": 4,
                "date": "2024-01-08",
                "comment": "Very good product overall. Minor issue with packaging but the product itself is excellent."
            }
        ]
        
        st.markdown("---")
        for review in reviews:
            with st.expander(f"{'⭐' * review['rating']} {review['name']} - {review['date']}"):
                st.write(f"*\"{review['comment']}\"*")
    
    with tab4:
        st.write("**Frequently Asked Questions**")
        
        faqs = [
            {
                "question": "What is the return policy?",
                "answer": "We offer a 30-day return policy for all products. Items must be in original condition with packaging."
            },
            {
                "question": "How long does shipping take?",
                "answer": "Standard shipping takes 5-7 business days. Express shipping (2-3 days) and overnight options are available."
            },
            {
                "question": "Is there a warranty?",
                "answer": "Yes, all products come with a 2-year manufacturer warranty covering defects and normal wear."
            },
            {
                "question": "Can I track my order?",
                "answer": "Absolutely! You'll receive a tracking number via email once your order ships."
            }
        ]
        
        for faq in faqs:
            with st.expander(f"❓ {faq['question']}"):
                st.write(faq['answer'])
    
    # Related products
    st.markdown("---")
    st.header("🔗 Related Products")
    
    related_cols = st.columns(3)
    related_products = [
        {"name": "Related Product 1", "price": "$89.99", "image": "https://via.placeholder.com/200x150/28a745/ffffff?text=Related+1"},
        {"name": "Related Product 2", "price": "$119.99", "image": "https://via.placeholder.com/200x150/dc3545/ffffff?text=Related+2"},
        {"name": "Related Product 3", "price": "$159.99", "image": "https://via.placeholder.com/200x150/ffc107/ffffff?text=Related+3"}
    ]
    
    for i, product in enumerate(related_products):
        with related_cols[i]:
            st.image(product["image"], use_column_width=True)
            st.write(f"**{product['name']}**")
            st.write(product["price"])
            if st.button("View Details", key=f"related_{i}"):
                st.info(f"Viewing {product['name']}")
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
'''

def generate_streamlit_search_page(plan: Dict[str, Any], project_config: Dict[str, Any]) -> str:
    """Generate Streamlit search page"""
    return '''import streamlit as st
import sys
import os

# Add components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'styles'))

from nav import render_navigation
from footer import render_footer
from inject import inject_global_styles
from product_card import render_product_card

st.set_page_config(
    page_title="Search - Your Store",
    page_icon="🔍",
    layout="wide"
)

def main():
    """Search page for products and content"""
    
    # Inject global styles
    inject_global_styles()
    
    # Render navigation
    render_navigation()
    
    # Search header
    st.title("🔍 Search")
    st.write("Find exactly what you're looking for")
    
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Search Query",
                placeholder="What are you looking for?",
                label_visibility="collapsed"
            )
        
        with col2:
            search_submitted = st.form_submit_button("🔍 Search", type="primary")
    
    # Advanced search options
    with st.expander("🔧 Advanced Search Options"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox("Category", ["All Categories", "Electronics", "Clothing", "Home & Garden", "Sports"])
            price_range = st.slider("Price Range", 0, 1000, (0, 1000), format="$%d")
        
        with col2:
            brand_filter = st.multiselect("Brands", ["Brand A", "Brand B", "Brand C", "Brand D"])
            rating_filter = st.selectbox("Minimum Rating", ["Any", "4+ Stars", "3+ Stars", "2+ Stars"])
        
        with col3:
            sort_options = st.selectbox("Sort Results", ["Relevance", "Price: Low to High", "Price: High to Low", "Newest", "Best Rating"])
            availability = st.checkbox("In Stock Only", value=True)
    
    # Search results
    if search_query or search_submitted:
        st.markdown("---")
        
        # Search results header
        col1, col2 = st.columns([2, 1])
        with col1:
            if search_query:
                st.subheader(f"Search Results for: '{search_query}'")
            else:
                st.subheader("All Products")
        
        with col2:
            results_count = 12  # TODO: Replace with actual count
            st.write(f"**{results_count} results found**")
        
        # Sample search results (TODO: Replace with real search in Step 5)
        sample_results = [
            {
                "id": 1,
                "name": "Premium Wireless Headphones",
                "price": "$199.99",
                "description": "High-quality wireless headphones with noise cancellation",
                "image": "https://via.placeholder.com/300x200/007bff/ffffff?text=Headphones",
                "rating": 4.8,
                "reviews": 156
            },
            {
                "id": 2,
                "name": "Smart Fitness Watch",
                "price": "$299.99", 
                "description": "Advanced fitness tracking with heart rate monitor",
                "image": "https://via.placeholder.com/300x200/28a745/ffffff?text=Watch",
                "rating": 4.6,
                "reviews": 89
            },
            {
                "id": 3,
                "name": "Portable Bluetooth Speaker",
                "price": "$79.99",
                "description": "Compact speaker with powerful sound and long battery life",
                "image": "https://via.placeholder.com/300x200/dc3545/ffffff?text=Speaker",
                "rating": 4.4,
                "reviews": 203
            },
            {
                "id": 4,
                "name": "Wireless Charging Pad",
                "price": "$39.99",
                "description": "Fast wireless charging for compatible devices",
                "image": "https://via.placeholder.com/300x200/ffc107/ffffff?text=Charger",
                "rating": 4.2,
                "reviews": 67
            }
        ]
        
        # Filter results based on search query (simple simulation)
        if search_query:
            filtered_results = [
                result for result in sample_results 
                if search_query.lower() in result["name"].lower() or 
                   search_query.lower() in result["description"].lower()
            ]
        else:
            filtered_results = sample_results
        
        # Display results
        if filtered_results:
            # Results grid
            cols = st.columns(2)
            for i, result in enumerate(filtered_results):
                with cols[i % 2]:
                    with st.container():
                        col_img, col_info = st.columns([1, 2])
                        
                        with col_img:
                            st.image(result["image"], use_column_width=True)
                        
                        with col_info:
                            st.subheader(result["name"])
                            st.write(f"**{result['price']}**")
                            st.write(f"{'⭐' * int(result['rating'])} ({result['rating']}) - {result['reviews']} reviews")
                            st.write(result["description"])
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("View Details", key=f"view_{result['id']}"):
                                    st.info(f"Viewing {result['name']}")
                            with col_btn2:
                                if st.button("Add to Cart", key=f"cart_{result['id']}"):
                                    st.success("Added to cart!")
                    
                    st.markdown("---")
            
            # Pagination (placeholder)
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("← Previous"):
                    st.info("Previous page")
            
            with col2:
                st.write("**Page 1 of 3**")
            
            with col3:
                if st.button("Next →"):
                    st.info("Next page")
        
        else:
            # No results found
            st.info("🔍 No products found matching your search criteria.")
            
            st.write("**Suggestions:**")
            st.write("• Check your spelling")
            st.write("• Try different keywords")
            st.write("• Use more general terms")
            st.write("• Browse our categories")
            
            # Popular searches
            st.subheader("Popular Searches")
            popular_searches = ["headphones", "watch", "speaker", "charger", "phone case"]
            
            search_cols = st.columns(len(popular_searches))
            for i, search_term in enumerate(popular_searches):
                with search_cols[i]:
                    if st.button(f"#{search_term}", key=f"popular_{i}"):
                        st.rerun()
    
    else:
        # Search suggestions when no query
        st.markdown("---")
        st.subheader("🎯 Popular Categories")
        
        category_cols = st.columns(4)
        categories = [
            {"name": "Electronics", "icon": "📱", "count": 156},
            {"name": "Clothing", "icon": "👕", "count": 89},
            {"name": "Home & Garden", "icon": "🏠", "count": 203},
            {"name": "Sports", "icon": "⚽", "count": 67}
        ]
        
        for i, category in enumerate(categories):
            with category_cols[i]:
                if st.button(f"{category['icon']} {category['name']}\\n{category['count']} items", key=f"cat_{i}"):
                    st.info(f"Browsing {category['name']}")
        
        # Recent searches (if any)
        st.subheader("🕒 Recent Searches")
        st.info("Your recent searches will appear here")
        
        # Search tips
        st.subheader("💡 Search Tips")
        st.write("""
        - Use specific product names for better results
        - Try different spellings or synonyms
        - Use filters to narrow down results
        - Browse categories if you're not sure what to search for
        """)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
'''

def generate_streamlit_sitemap(plan: Dict[str, Any], project_config: Dict[str, Any]) -> str:
    """Generate sitemap.xml for Streamlit scaffold"""
    base_url = "https://example.com"  # TODO: Get from config
    pages = plan.get("pages", [])
    
    sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    
    # Add pages from plan
    for page in pages:
        slug = page.get("slug", "/")
        priority = "1.0" if slug == "/" else "0.8"
        changefreq = "daily" if slug == "/" else "weekly"
        
        sitemap_content += f'''    <url>
        <loc>{base_url}{slug}</loc>
        <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
        <changefreq>{changefreq}</changefreq>
        <priority>{priority}</priority>
    </url>
'''
    
    sitemap_content += '</urlset>'
    return sitemap_content

def generate_streamlit_robots(project_config: Dict[str, Any]) -> str:
    """Generate robots.txt for Streamlit scaffold"""
    return f"""User-agent: *
Allow: /

Sitemap: https://example.com/_public/sitemap.xml

# Generated by VSBVibe for {project_config.get('project_name', 'Project')}
# Streamlit-specific paths
Disallow: /_stcore/
Disallow: /_stapp/
"""

def show_tests_panel():
    st.subheader("🧪 Project Tests")
    
    # Run basic tests for Step 1
    if st.button("🚀 Run Step 1 Tests", type="primary"):
        test_runner = TestRunner(st.session_state.project_manager)
        results = test_runner.run_step1_tests()
        
        # Display results
        st.write("**Test Results:**")
        for test_name, result in results.items():
            if result["passed"]:
                st.success(f"✅ {test_name}: {result['message']}")
            else:
                st.error(f"❌ {test_name}: {result['message']}")
        
        # Overall status
        passed_tests = sum(1 for r in results.values() if r["passed"])
        total_tests = len(results)
        
        if passed_tests == total_tests:
            st.success(f"🎉 All tests passed! ({passed_tests}/{total_tests})")
        else:
            st.warning(f"⚠️ {passed_tests}/{total_tests} tests passed")
    
    # Step 2 tests
    if st.session_state.step >= 2:
        if st.button("🚀 Run Step 2 Tests", type="primary"):
            test_runner = TestRunner(st.session_state.project_manager)
            results = test_runner.run_step2_tests()
            
            # Display results
            st.write("**Step 2 Test Results:**")
            for test_name, result in results.items():
                if result["passed"]:
                    st.success(f"✅ {test_name}: {result['message']}")
                else:
                    st.error(f"❌ {test_name}: {result['message']}")
            
            # Overall status
            passed_tests = sum(1 for r in results.values() if r["passed"])
            total_tests = len(results)
            
            if passed_tests == total_tests:
                st.success(f"🎉 All Step 2 tests passed! ({passed_tests}/{total_tests})")
            else:
                st.warning(f"⚠️ {passed_tests}/{total_tests} Step 2 tests passed")
    
    st.info("Additional tests will be available as you progress through the steps")

def show_logs_panel():
    st.subheader("📊 Activity Logs")
    
    logs_path = os.path.join(
        st.session_state.project_manager.get_current_project_path(),
        "_vsbvibe", "logs", "activity.json"
    )
    
    if os.path.exists(logs_path):
        logs = load_json(logs_path) or []
        
        if logs:
            st.write(f"**Recent Activity** ({len(logs)} entries)")
            
            # Show recent logs
            for log in reversed(logs[-10:]):  # Show last 10 entries
                timestamp = log.get("timestamp", "")[:19].replace("T", " ")
                action = log.get("action", "Unknown")
                details = log.get("details", "")
                
                with st.expander(f"{action} - {timestamp}", expanded=False):
                    st.write(details)
                    if log.get("data"):
                        st.json(log["data"])
        else:
            st.info("No activity logs found")
    else:
        st.info("Activity logging will start once you begin using the system")

        
        if submitted and project_name and base_folder:
            try:
                project_path = st.session_state.project_manager.create_project(
                    project_name, company_brand, reference_url, 
                    requirements, content_mode, base_folder
                )
                st.session_state.current_project = project_name
                st.success(f"Project created at: {project_path}")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating project: {str(e)}")
    
    # Load existing project
    st.subheader("Load Existing Project")
    existing_folder = st.text_input("Project Folder Path")
    if st.button("Load Project") and existing_folder:
        try:
            project_name = st.session_state.project_manager.load_project(existing_folder)
            st.session_state.current_project = project_name
            st.success(f"Loaded project: {project_name}")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading project: {str(e)}")

if __name__ == "__main__":
    main()