"""
Step 4 Interface - Excel Template Generation
"""

import streamlit as st
import os
from datetime import datetime
from modules.project_manager import ProjectManager
from modules.template_generator import TemplateGenerator
from core.state import get_session_state
from core.telemetry import log_user_action
from site.core.errors import safe_page, safe_component

@safe_page
def render_step4_interface():
    """Render Step 4 - Excel Template Generation"""
    
    st.header("📋 Step 4: Content Templates")
    st.write("Generate Excel templates for offline content preparation.")
    
    # Progress indicator
    progress_cols = st.columns(10)
    for i in range(10):
        with progress_cols[i]:
            if i == 3:
                st.markdown("🔵")  # Current step
            elif i < 3:
                st.markdown("✅")  # Completed steps
            else:
                st.markdown("⚪")  # Future steps
    
    st.markdown("---")
    
    # Check project state
    project_path = get_session_state("project_path")
    if not project_path:
        st.error("No project loaded. Please complete previous steps first.")
        return
    
    # Load project configuration
    project_manager = ProjectManager()
    project_manager.current_project_path = project_path
    project_config = project_manager.load_project_config()
    
    if not project_config:
        st.error("Could not load project configuration.")
        return
    
    # Load plan
    plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
    if not os.path.exists(plan_path):
        st.error("No plan found. Please complete Step 2 first.")
        return
    
    try:
        with open(plan_path, 'r') as f:
            plan = json.load(f)
    except:
        st.error("Could not load plan. Please regenerate plan in Step 2.")
        return
    
    # Display project info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Project:** {project_config.get('project_name', 'Unknown')}")
    
    with col2:
        st.info(f"**Site Mode:** {plan.get('site_mode', 'Unknown')}")
    
    with col3:
        products_enabled = plan.get("entities", {}).get("products", False)
        st.info(f"**Products:** {'Enabled' if products_enabled else 'Disabled'}")
    
    # Template generation section
    st.subheader("📊 Template Generation")
    
    # Check what templates are needed
    templates_needed = []
    if plan.get("entities", {}).get("products", False):
        templates_needed.append("Products")
    
    brochure_pages = [p for p in plan.get("pages", []) if p.get('type') not in ['product_list', 'product_detail']]
    if brochure_pages:
        templates_needed.append("Pages")
    
    if templates_needed:
        st.write(f"**Templates Required:** {', '.join(templates_needed)}")
    else:
        st.warning("No templates required based on current plan.")
        return
    
    # Check for existing templates
    content_path = os.path.join(project_path, "content")
    products_path = os.path.join(content_path, "products.xlsx")
    pages_path = os.path.join(content_path, "pages.xlsx")
    readme_path = os.path.join(content_path, "README_import.md")
    
    templates_exist = []
    if plan.get("entities", {}).get("products", False) and os.path.exists(products_path):
        templates_exist.append("Products")
    if brochure_pages and os.path.exists(pages_path):
        templates_exist.append("Pages")
    
    # Template status
    if templates_exist:
        st.success(f"✅ Existing templates: {', '.join(templates_exist)}")
        
        # Show template details
        _display_template_details(project_path, plan)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Regenerate Templates", type="secondary"):
                _generate_templates(project_manager)
                st.rerun()
        
        with col2:
            if st.button("Continue to Step 5", type="primary"):
                st.session_state.current_step = 5
                st.rerun()
    
    else:
        st.info("Ready to generate Excel templates for content preparation.")
        
        # Generation options
        with st.expander("Template Options", expanded=True):
            st.write("**What will be generated:**")
            
            if plan.get("entities", {}).get("products", False):
                st.write("• **products.xlsx** - Product catalog template with validation")
            
            if brochure_pages:
                st.write("• **pages.xlsx** - Page content template with markdown support")
            
            st.write("• **README_import.md** - Comprehensive import guide")
            st.write("• **content/images/** - Folder for local images")
            st.write("• **content/samples/** - CSV sample files")
        
        if st.button("📋 Generate Templates", type="primary"):
            _generate_templates(project_manager)
            st.rerun()

@safe_component
def _display_template_details(project_path: str, plan: dict):
    """Display details about existing templates"""
    
    content_path = os.path.join(project_path, "content")
    
    # Products template details
    if plan.get("entities", {}).get("products", False):
        products_path = os.path.join(content_path, "products.xlsx")
        if os.path.exists(products_path):
            with st.expander("📦 Products Template Details"):
                try:
                    df = pd.read_excel(products_path)
                    st.write(f"**Rows:** {len(df)}")
                    st.write(f"**Columns:** {', '.join(df.columns)}")
                    
                    # Show preview
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    # Download button
                    with open(products_path, 'rb') as f:
                        st.download_button(
                            "📥 Download products.xlsx",
                            data=f.read(),
                            file_name="products.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Error reading products template: {e}")
    
    # Pages template details
    brochure_pages = [p for p in plan.get("pages", []) if p.get('type') not in ['product_list', 'product_detail']]
    if brochure_pages:
        pages_path = os.path.join(content_path, "pages.xlsx")
        if os.path.exists(pages_path):
            with st.expander("📄 Pages Template Details"):
                try:
                    df = pd.read_excel(pages_path)
                    st.write(f"**Rows:** {len(df)}")
                    st.write(f"**Columns:** {', '.join(df.columns)}")
                    
                    # Show preview
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    # Download button
                    with open(pages_path, 'rb') as f:
                        st.download_button(
                            "📥 Download pages.xlsx",
                            data=f.read(),
                            file_name="pages.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Error reading pages template: {e}")
    
    # Documentation
    readme_path = os.path.join(content_path, "README_import.md")
    if os.path.exists(readme_path):
        with st.expander("📖 Import Documentation"):
            try:
                with open(readme_path, 'r') as f:
                    readme_content = f.read()
                st.markdown(readme_content[:1000] + "..." if len(readme_content) > 1000 else readme_content)
            except Exception as e:
                st.error(f"Error reading documentation: {e}")

@safe_component
def _generate_templates(project_manager: ProjectManager):
    """Generate Excel templates using TemplateGenerator"""
    
    try:
        with st.spinner("Generating Excel templates..."):
            
            template_generator = TemplateGenerator(project_manager)
            results = template_generator.generate_templates()
            
            st.success("✅ Templates generated successfully!")
            
            # Show summary
            st.write("**Generated Files:**")
            for file_path in results["files_created"]:
                st.write(f"• {file_path}")
            
            # Update project status
            project_config = project_manager.get_project_config()
            if project_config:
                project_config["status"] = "step4_complete"
                project_config["updated_at"] = datetime.now().isoformat()
                project_manager.save_project_config(project_config)
            
            log_user_action("templates_generated", {
                "templates_count": results["templates_generated"],
                "files_count": len(results["files_created"])
            })
    
    except Exception as e:
        st.error(f"Error generating templates: {str(e)}")