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
    
    project_path = st.session_state.project_manager.get_current_project_path()
    plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
    site_path = os.path.join(project_path, "site")
    
    # Check if plan exists
    if not os.path.exists(plan_path):
        st.error("❌ No plan found. Please complete Step 2 first.")
        return
    
    # Check if scaffold already exists
    scaffold_exists = os.path.exists(site_path) and os.path.exists(os.path.join(site_path, "app.py"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Generation Options:**")
        generate_components = st.checkbox("Generate Components", value=True)
        generate_seo = st.checkbox("Generate SEO Utilities", value=True)
        generate_styles = st.checkbox("Generate Styling System", value=True)
        
    with col2:
        st.write("**Scaffold Status:**")
        if scaffold_exists:
            st.success("✅ Scaffold exists")
            st.info("Use 'Regenerate' to update existing files")
        else:
            st.info("⏳ No scaffold generated yet")
    
    # Generation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏗️ Generate Scaffold", type="primary", disabled=scaffold_exists):
            if generate_scaffold(project_path, generate_components, generate_seo, generate_styles):
                st.success("✅ Scaffold generated successfully!")
                st.session_state.step = max(st.session_state.step, 3)
                st.rerun()
            else:
                st.error("❌ Error generating scaffold")
    
    with col2:
        if st.button("🔄 Regenerate", disabled=not scaffold_exists):
            if generate_scaffold(project_path, generate_components, generate_seo, generate_styles, regenerate=True):
                st.success("✅ Scaffold regenerated successfully!")
                st.rerun()
            else:
                st.error("❌ Error regenerating scaffold")
    
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
        st.write("**Generated Files:**")
        
        # List key files
        key_files = [
            "site/app.py",
            "site/pages/00_Home.py",
            "site/components/nav.py",
            "site/components/footer.py",
            "site/styles/tokens.json",
            "site/seo/jsonld.py"
        ]
        
        for file_path in key_files:
            full_path = os.path.join(project_path, file_path)
            if os.path.exists(full_path):
                st.success(f"✅ {file_path}")
            else:
                st.error(f"❌ {file_path}")
    
    # Preview instructions
    preview_path = os.path.join(project_path, "_vsbvibe", "preview.json")
    if os.path.exists(preview_path):
        st.write("**Preview Instructions:**")
        preview_data = load_json(preview_path)
        if preview_data:
            st.info(f"📁 Navigate to: {preview_data.get('directory', 'site/')}")
            st.info(f"🚀 Run: {preview_data.get('command', 'streamlit run app.py')}")
            st.info(f"🌐 URL: {preview_data.get('url', 'http://localhost:8501')}")

def generate_scaffold(project_path: str, components: bool = True, seo: bool = True, styles: bool = True, regenerate: bool = False) -> bool:
    """Generate the Streamlit scaffold from plan"""
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
        
        # Create site directory structure
        site_path = os.path.join(project_path, "site")
        directories = [
            "pages",
            "components", 
            "styles",
            "seo",
            "utils",
            "assets"
        ]
        
        for directory in directories:
            ensure_directory(os.path.join(site_path, directory))
        
        # Track generated files for diff
        generated_files = []
        
        # Generate main app.py
        app_content = generate_main_app(plan, project_config)
        app_path = os.path.join(site_path, "app.py")
        with open(app_path, 'w') as f:
            f.write(app_content)
        generated_files.append("site/app.py")
        
        # Generate pages
        pages = plan.get("pages", [])
        for page in pages:
            page_content = generate_page(page, plan, project_config)
            page_filename = f"{page.get('priority', 0):02d}_{page.get('name', 'Unknown').replace(' ', '_')}.py"
            page_path = os.path.join(site_path, "pages", page_filename)
            
            with open(page_path, 'w') as f:
                f.write(page_content)
            generated_files.append(f"site/pages/{page_filename}")
        
        # Generate components
        if components:
            component_files = generate_components(plan, project_config)
            for filename, content in component_files.items():
                comp_path = os.path.join(site_path, "components", filename)
                with open(comp_path, 'w') as f:
                    f.write(content)
                generated_files.append(f"site/components/{filename}")
        
        # Generate styles
        if styles:
            tokens_content = generate_tokens(plan)
            tokens_path = os.path.join(site_path, "styles", "tokens.json")
            save_json(tokens_path, tokens_content)
            generated_files.append("site/styles/tokens.json")
            
            inject_content = generate_style_injector(plan)
            inject_path = os.path.join(site_path, "styles", "inject.py")
            with open(inject_path, 'w') as f:
                f.write(inject_content)
            generated_files.append("site/styles/inject.py")
        
        # Generate SEO utilities
        if seo:
            seo_files = generate_seo_utilities(seo_defaults, project_config)
            for filename, content in seo_files.items():
                seo_path = os.path.join(site_path, "seo", filename)
                with open(seo_path, 'w') as f:
                    f.write(content)
                generated_files.append(f"site/seo/{filename}")
        
        # Generate preview instructions
        preview_data = {
            "directory": "site/",
            "command": "streamlit run app.py",
            "url": "http://localhost:8501",
            "generated_at": datetime.now().isoformat()
        }
        preview_path = os.path.join(project_path, "_vsbvibe", "preview.json")
        save_json(preview_path, preview_data)
        
        # Generate diff summary
        diff_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": "regenerate" if regenerate else "generate",
            "files_created": generated_files,
            "files_updated": [],
            "total_files": len(generated_files)
        }
        diff_path = os.path.join(project_path, "_vsbvibe", "diff_summary.json")
        save_json(diff_path, diff_data)
        
        # Log scaffold generation
        log_activity(project_path, "scaffold_generated", f"Generated {len(generated_files)} files")
        
        return True
        
    except Exception as e:
        print(f"Error generating scaffold: {e}")
        return False

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