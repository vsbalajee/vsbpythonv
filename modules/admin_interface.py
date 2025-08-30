import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import shutil
from core.errors import safe_page, safe_component
from modules.project_manager import ProjectManager

@safe_page
def render_admin_interface():
    """Render Admin Interface"""
    pm = ProjectManager()
    st.title("Admin Interface")

    with st.sidebar:
        st.subheader("Theme")
        color_scheme = st.selectbox("Color Scheme", ["System", "Light", "Dark"], index=0)
        st.caption("Preview-only theme switcher")

    tab_req, tab_keys, tab_products, tab_errors, tab_tests = st.tabs(
        ["Requirements", "Models & Keys", "Products", "Errors", "Tests"]
    )

    with tab_req:
        st.subheader("Requirements (versioned)")
        # render_requirements_panel(pm)

    with tab_keys:
        st.subheader("Models & Keys")

        if st.secrets.get("openai_api_key"):
            st.success("✅ OpenAI key is loaded from Streamlit secrets.")
        else:
            st.error("❌ OpenAI key is missing. Add it in Streamlit secrets or .streamlit/secrets.toml locally.")

        current_model = st.secrets.get("openai_model", "gpt-5-mini")
        st.info(f"Default OpenAI model: **{current_model}** (used automatically in all AI operations)")

    with tab_products:
        st.subheader("Products")
        # render_products_admin()

    with tab_errors:
        st.subheader("Errors & Logs")
        # render_errors_panel()

    with tab_tests:
        st.subheader("Test Module")
        # render_tests_panel()

__all__ = ["render_admin_interface"]

class AdminInterface:
    def __init__(self, project_manager):
        self.project_manager = project_manager
    
    def render(self):
        st.header("🛠️ Admin Dashboard")
        
        # Admin module tabs
        admin_tabs = st.tabs([
            "Requirements", "Models & Keys", "Pages", "Design", 
            "Products", "Data", "Generate", "Publish", "Tests", "Jobs & Logs"
        ])
        
        with admin_tabs[0]:
            self._render_requirements()
        
        with admin_tabs[1]:
            self._render_models_keys()
        
        with admin_tabs[2]:
            self._render_pages()
        
        with admin_tabs[3]:
            self._render_design()
        
        with admin_tabs[4]:
            self._render_products_enhanced()
        
        with admin_tabs[5]:
            self._render_data()
        
        with admin_tabs[6]:
            self._render_generate()
        
        with admin_tabs[7]:
            self._render_publish()
        
        with admin_tabs[8]:
            self._render_tests()
        
        with admin_tabs[9]:
            self._render_jobs_logs()
        
        # Errors tab
        with st.tabs(["Errors"])[0] if len(st.tabs(["Errors"])) > 0 else st.container():
            self._render_errors()
        
        # Admin Chat at the bottom
        self._render_admin_chat()
    
    @safe_page
    def _render_requirements(self):
        st.subheader("Requirements Management")
        
        project_config = self.project_manager.get_project_config()
        if not project_config:
            st.error("No project loaded")
            return
        
        # Current requirements
        st.text_area(
            "Current Requirements", 
            value=project_config.get("requirements", ""), 
            height=200,
            disabled=True
        )
        
        # Update requirements
        with st.form("update_requirements"):
            new_requirements = st.text_area(
                "Update Requirements", 
                placeholder="Enter new or updated requirements..."
            )
            
            version_note = st.text_input("Version Note", placeholder="What changed?")
            
            if st.form_submit_button("Update Requirements"):
                if new_requirements:
                    self._update_requirements(new_requirements, version_note)
                    st.success("Requirements updated successfully!")
                    st.rerun()
    
    @safe_page
    def _render_models_keys(self):
        st.subheader("AI Models & API Keys")
        
        # Load current settings
        project_path = self.project_manager.get_current_project_path()
        settings_path = os.path.join(project_path, "_vsbvibe", "settings.json")
        
        settings = {}
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
        
        with st.form("models_keys"):
            st.write("**AI Models Configuration**")
            openai_key = st.text_input("OpenAI API Key", 
                                     value=settings.get("openai_key", ""), 
                                     type="password")
            
            claude_key = st.text_input("Anthropic API Key", 
                                     value=settings.get("claude_key", ""), 
                                     type="password")
            
            st.write("**Supabase Configuration**")
            supabase_url = st.text_input("Supabase URL", 
                                       value=settings.get("supabase_url", ""))
            supabase_key = st.text_input("Supabase Anon Key", 
                                       value=settings.get("supabase_key", ""), 
                                       type="password")
            
            if st.form_submit_button("Save Settings"):
                new_settings = {
                    "openai_key": openai_key,
                    "claude_key": claude_key,
                    "supabase_url": supabase_url,
                    "supabase_key": supabase_key,
                    "updated_at": datetime.now().isoformat()
                }
                
                with open(settings_path, 'w') as f:
                    json.dump(new_settings, f, indent=2)
                
                st.success("Settings saved successfully!")
    
    @safe_page
    def _render_pages(self):
        st.subheader("📄 Pages Management")
        
        project_path = self.project_manager.get_current_project_path()
        plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
        
        try:
            plan = {}
            if os.path.exists(plan_path):
                with open(plan_path, 'r') as f:
                    plan = json.load(f)
            
            pages = plan.get("pages", [])
            
            if pages:
                st.write("**Planned Pages:**")
                
                # Create enhanced pages display
                for i, page in enumerate(pages):
                    with st.expander(f"{page.get('name', 'Unknown')} ({page.get('slug', '/')})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Type:** {page.get('type', 'unknown')}")
                            st.write(f"**Priority:** {page.get('priority', 0)}")
                        
                        with col2:
                            sections = page.get('sections', [])
                            if sections:
                                st.write("**Sections:**")
                                for section in sections:
                                    st.write(f"• {section}")
                        
                        with col3:
                            # Check if page file exists
                            platform_target = plan.get("platform_target", "streamlit_site")
                            if platform_target == "streamlit_site":
                                page_file = f"site/pages/{i:02d}_{page.get('name', 'Page').replace(' ', '_')}.py"
                                file_exists = os.path.exists(os.path.join(project_path, "output", platform_target, page_file))
                                
                                if file_exists:
                                    st.success("✅ Generated")
                                else:
                                    st.warning("⏳ Pending")
            
            # Template management
            st.markdown("---")
            st.subheader("📋 Content Templates")
            
            # Check for existing templates
            products_path = os.path.join(project_path, "content", "products.xlsx")
            pages_path = os.path.join(project_path, "content", "pages.xlsx")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if plan.get("entities", {}).get("products", False):
                    if os.path.exists(products_path):
                        st.success("✅ Products template exists")
                        if st.button("📥 Download products.xlsx"):
                            with open(products_path, 'rb') as f:
                                st.download_button(
                                    "Download Products Template",
                                    data=f.read(),
                                    file_name="products.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                    else:
                        if st.button("📋 Generate Products Template"):
                            self._generate_templates()
                            st.rerun()
            
            with col2:
                brochure_pages = [p for p in pages if p.get('type') not in ['product_list', 'product_detail']]
                if brochure_pages:
                    if os.path.exists(pages_path):
                        st.success("✅ Pages template exists")
                        if st.button("📥 Download pages.xlsx"):
                            with open(pages_path, 'rb') as f:
                                st.download_button(
                                    "Download Pages Template",
                                    data=f.read(),
                                    file_name="pages.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                    else:
                        if st.button("📋 Generate Pages Template"):
                            self._generate_templates()
                            st.rerun()
            
            # Helper buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📁 Open Images Folder"):
                    images_path = os.path.join(project_path, "content", "images")
                    st.info(f"Images folder: {images_path}")
            
            with col2:
                samples_path = os.path.join(project_path, "content", "samples")
                if os.path.exists(samples_path):
                    if st.button("📊 View Sample Files"):
                        st.info(f"Sample files location: {samples_path}")
            
            with col3:
                if st.button("📖 View Import Guide"):
                    readme_path = os.path.join(project_path, "content", "README_import.md")
                    if os.path.exists(readme_path):
                        with open(readme_path, 'r') as f:
                            st.text_area("Import Guide", value=f.read(), height=300)
        
        except Exception as e:
            st.error(f"Error loading pages: {e}")
        
    @safe_component
    def _generate_templates(self):
        """Generate Excel templates using TemplateGenerator"""
        try:
            from modules.template_generator import TemplateGenerator
            template_generator = TemplateGenerator(self.project_manager)
            results = template_generator.generate_templates()
            
            st.success(f"✅ Generated {results['templates_generated']} templates")
            st.write("**Files Created:**")
            for file_path in results["files_created"]:
                st.write(f"• {file_path}")
                
        except Exception as e:
            st.error(f"Error generating templates: {e}")
    
    @safe_page
    def _render_products_enhanced(self):
        st.subheader("🛍️ Products Management")
        
        project_path = self.project_manager.get_current_project_path()
        products_path = os.path.join(project_path, "content", "products.xlsx")
        
        # Check if products are enabled in plan
        plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
        plan = {}
        if os.path.exists(plan_path):
            with open(plan_path, 'r') as f:
                plan = json.load(f)
        
        products_enabled = plan.get("entities", {}).get("products", False)
        
        if not products_enabled:
            st.info("Products not enabled for this project. Enable in Step 2 plan if needed.")
            return
        
        # Template management
        if os.path.exists(products_path):
            st.success("✅ Products template exists")
            
            # Load and display products
            try:
                df = pd.read_excel(products_path)
                
                st.write("**Current Products:**")
                edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💾 Save Changes"):
                        edited_df.to_excel(products_path, index=False)
                        st.success("Products saved successfully!")
                
                with col2:
                    if st.button("📥 Download Template"):
                        with open(products_path, 'rb') as f:
                            st.download_button(
                                "Download products.xlsx",
                                data=f.read(),
                                file_name="products.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                
                with col3:
                    if st.button("📁 Open Images Folder"):
                        images_path = os.path.join(project_path, "content", "images")
                        st.info(f"Images folder: {images_path}")
                
            except Exception as e:
                st.error(f"Error loading products: {e}")
        
        else:
            st.warning("Products template not found.")
            
            if st.button("📋 Generate Products Template"):
                self._generate_templates()
                st.rerun()
        
        # Sample files
        sample_path = os.path.join(project_path, "content", "samples", "products_sample.csv")
        if os.path.exists(sample_path):
            with st.expander("📊 View Sample Data"):
                sample_df = pd.read_csv(sample_path)
                st.dataframe(sample_df, use_container_width=True)
    
    @safe_page
    def _render_errors(self):
        st.subheader("🚨 Error Management")
        
        project_path = self.project_manager.get_current_project_path()
        if not project_path:
            st.error("No project loaded")
            return
        
        # Error summary
        errors_log_path = os.path.join(project_path, "_vsbvibe", "logs", "errors.log")
        
        if os.path.exists(errors_log_path):
            # Load recent errors
            recent_errors = []
            try:
                with open(errors_log_path, 'r') as f:
                    for line in f:
                        try:
                            error_entry = json.loads(line.strip())
                            recent_errors.append(error_entry)
                        except:
                            continue
            except:
                pass
            
            # Display error table
            if recent_errors:
                st.write("**Recent Errors:**")
                
                # Prepare data for display
                error_data = []
                for error in recent_errors[-20:]:  # Last 20 errors
                    meta = error.get("meta", {})
                    error_data.append({
                        "Time": error.get("timestamp", "")[:19],
                        "Module": meta.get("module", "unknown"),
                        "File:Line": f"{meta.get('files_to_correct', 'unknown')}:{meta.get('line_number', 0)}",
                        "Error": meta.get("error_name", "unknown"),
                        "Status": meta.get("status", "new")
                    })
                
                if error_data:
                    df = pd.DataFrame(error_data)
                    st.dataframe(df, use_container_width=True)
                
                # Error management buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 Generate Error Report"):
                        self._generate_error_excel_report(project_path)
                
                with col2:
                    if st.button("📁 Open Suggestions Folder"):
                        suggestions_path = os.path.join(project_path, "_vsbvibe", "errors", "suggestions")
                        st.info(f"Suggestions folder: {suggestions_path}")
                
                with col3:
                    split_summary_path = os.path.join(project_path, "_vsbvibe", "logs", "split_summary.json")
                    if os.path.exists(split_summary_path):
                        if st.button("📋 Split Summary"):
                            with open(split_summary_path, 'r') as f:
                                split_data = json.load(f)
                            
                            with st.expander("View Split Summary", expanded=True):
                                st.json(split_data)
            
            else:
                st.success("No errors found!")
        
        else:
            st.info("No error log found. Errors will appear here when they occur.")
    
    @safe_page
    def _render_tests(self):
        st.subheader("Testing Dashboard")
        st.info("See Test tab for detailed testing interface")
    
    @safe_component
    def _generate_error_excel_report(self, project_path: str):
        """Generate Excel error report"""
        
        try:
            from core.errors import error_reporter
            
            excel_path = os.path.join(project_path, "_vsbvibe", "errors", "error_report.xlsx")
            
            if os.path.exists(excel_path):
                st.success(f"✅ Error report generated: {excel_path}")
                
                # Show download option
                with open(excel_path, 'rb') as f:
                    st.download_button(
                        "📥 Download Error Report",
                        data=f.read(),
                        file_name="error_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.warning("No error report found. Errors must occur first to generate report.")
                
        except Exception as e:
            st.error(f"Error generating report: {e}")
    
    @safe_component
    def _update_requirements(self, requirements: str, version_note: str):
        """Update project requirements with versioning"""
        project_config = self.project_manager.get_project_config()
        
        # Store previous version
        versions_path = os.path.join(
            self.project_manager.get_current_project_path(),
            "_vsbvibe", "requirements_versions.json"
        )
        
        versions = []
        if os.path.exists(versions_path):
            with open(versions_path, 'r') as f:
                versions = json.load(f)
        
        # Add previous version to history
        versions.append({
            "version": len(versions) + 1,
            "requirements": project_config.get("requirements", ""),
            "note": version_note,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(versions_path, 'w') as f:
            json.dump(versions, f, indent=2)
        
        # Update current requirements
        self.project_manager.update_project_config({"requirements": requirements})

__all__ = ["render_admin_interface"]