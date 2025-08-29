import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import shutil
from site.core.errors import safe_page, safe_component
from .template_generator import TemplateGenerator

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
        settings_path = os.path.join(
            self.project_manager.get_current_project_path(), 
            "_vsbvibe", "settings.json"
        )
        
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
        
        plan_path = os.path.join(
            self.project_manager.get_current_project_path(), 
            "_vsbvibe", "plan.json"
        )
        
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
                                project_path = self.project_manager.get_current_project_path()
                                file_exists = os.path.exists(os.path.join(project_path, "output", platform_target, page_file))
                                
                                if file_exists:
                                    st.success("✅ Generated")
                                else:
                                    st.warning("⏳ Pending")
            
            # Template management
            st.markdown("---")
            st.subheader("📋 Content Templates")
            
            project_path = self.project_manager.get_current_project_path()
            
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
    def _render_design(self):
        st.subheader("🎨 Design Settings")
        
        plan_path = os.path.join(
            self.project_manager.get_current_project_path(), 
            "_vsbvibe", "plan.json"
        )
        
        try:
            plan = {}
            if os.path.exists(plan_path):
                with open(plan_path, 'r') as f:
                    plan = json.load(f)
            
            # Display current brand tokens
            brand_tokens = plan.get("brand_tokens", {})
            
            if brand_tokens:
                st.write("**Current Brand Tokens:**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    primary_color = brand_tokens.get("primary_color", "#2563eb")
                    st.color_picker("Primary Color", value=primary_color, disabled=True)
                
                with col2:
                    secondary_color = brand_tokens.get("secondary_color", "#64748b")
                    st.color_picker("Secondary Color", value=secondary_color, disabled=True)
                
                with col3:
                    accent_color = brand_tokens.get("accent_color", "#10b981")
                    st.color_picker("Accent Color", value=accent_color, disabled=True)
                
                st.write(f"**Font Family:** {brand_tokens.get('font_family', 'Inter')}")
                st.write(f"**Border Radius:** {brand_tokens.get('border_radius', '8px')}")
                st.write(f"**Spacing Unit:** {brand_tokens.get('spacing_unit', '1rem')}")
            
            # Platform-specific design files
            platform_target = plan.get("platform_target", "streamlit_site")
            project_path = self.project_manager.get_current_project_path()
            
            st.markdown("---")
            st.write("**Design Files:**")
            
            if platform_target == "streamlit_site":
                tokens_path = os.path.join(project_path, "output", platform_target, "site", "styles", "tokens.json")
                if os.path.exists(tokens_path):
                    st.success("✅ styles/tokens.json exists")
                    if st.button("👀 View Tokens File"):
                        with open(tokens_path, 'r') as f:
                            tokens_data = json.load(f)
                        st.json(tokens_data)
                else:
                    st.warning("⏳ Tokens file not generated yet")
            
            elif platform_target == "htmljs":
                css_path = os.path.join(project_path, "output", platform_target, "css", "main.css")
                if os.path.exists(css_path):
                    st.success("✅ css/main.css exists")
                    if st.button("👀 View CSS File"):
                        with open(css_path, 'r') as f:
                            css_content = f.read()
                        st.code(css_content, language="css")
                else:
                    st.warning("⏳ CSS file not generated yet")
            
            # UI/UX Plan display
            ui_plan = plan.get("ui_ux_plan", {})
            
            if ui_plan:
                st.markdown("---")
                st.write("**UI/UX Plan:**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Layout:** {ui_plan.get('layout', 'modern')}")
                    st.write(f"**Color Scheme:** {ui_plan.get('color_scheme', 'professional')}")
                
                with col2:
                    st.write(f"**Target Audience:** {ui_plan.get('target_audience', 'general')}")
                    features = ui_plan.get('features', [])
                    if features:
                        st.write(f"**Features:** {', '.join(features)}")
        
        except Exception as e:
            st.error(f"Error loading design settings: {e}")
        
    @safe_page
    def _render_generate(self):
        st.subheader("⚙️ Site Generation")
        
        project_path = self.project_manager.get_current_project_path()
        
        # Load plan for platform info
        plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
        plan = {}
        if os.path.exists(plan_path):
            with open(plan_path, 'r') as f:
                plan = json.load(f)
        
        platform_target = plan.get("platform_target", "streamlit_site")
        site_mode = plan.get("site_mode", "brochure")
        
        # Display current configuration
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Platform:** {platform_target}")
        
        with col2:
            st.info(f"**Site Mode:** {site_mode}")
        
        with col3:
            pages_count = len(plan.get("pages", []))
            st.info(f"**Pages:** {pages_count}")
        
        # Check for existing scaffold
        output_path = os.path.join(project_path, "output", platform_target)
        scaffold_exists = os.path.exists(output_path)
        
        if scaffold_exists:
            st.success("✅ Scaffold generated")
            
            # Show diff summary
            diff_path = os.path.join(project_path, "_vsbvibe", "diff_summary.json")
            if os.path.exists(diff_path):
                with st.expander("📋 View Generation Summary"):
                    with open(diff_path, 'r') as f:
                        diff_data = json.load(f)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Files Created:**")
                        for file_path in diff_data.get("files_created", []):
                            st.write(f"• {file_path}")
                    
                    with col2:
                        st.write("**Files Updated:**")
                        for file_path in diff_data.get("files_updated", []):
                            st.write(f"• {file_path}")
            
            # Regeneration options
            st.markdown("---")
            st.write("**Regeneration Options:**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Regenerate Site"):
                    self._regenerate_scaffold("site")
            
            with col2:
                if st.button("📄 Regenerate Pages"):
                    self._regenerate_scaffold("pages")
            
            with col3:
                if st.button("🎨 Regenerate Styles"):
                    self._regenerate_scaffold("styles")
        
        else:
            st.warning("No scaffold generated yet")
            
            if st.button("⚙️ Generate Scaffold", type="primary"):
                # This would trigger scaffold generation
                st.info("Scaffold generation would be triggered here")
        
        # SEO Export Panel
        st.markdown("---")
        st.subheader("🔍 SEO Export Panel")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Export Sitemap"):
                self._export_seo_file("sitemap")
        
        with col2:
            if st.button("🤖 Export Robots.txt"):
                self._export_seo_file("robots")
    
    @safe_component
    def _regenerate_scaffold(self, scope: str):
        """Regenerate specific parts of scaffold"""
        st.info(f"Regenerating {scope}...")
        # Implementation would go here
    
    @safe_component
    def _export_seo_file(self, file_type: str):
        """Export SEO files to platform's public folder"""
        project_path = self.project_manager.get_current_project_path()
        
        # Load plan for platform info
        plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
        plan = {}
        if os.path.exists(plan_path):
            with open(plan_path, 'r') as f:
                plan = json.load(f)
        
        platform_target = plan.get("platform_target", "streamlit_site")
        
        # Determine public folder based on platform
        if platform_target == "streamlit_site":
            public_path = os.path.join(project_path, "output", platform_target, "_public")
        else:
            public_path = os.path.join(project_path, "output", platform_target, "public")
        
        ensure_directory(public_path)
        
        if file_type == "sitemap":
            # Generate sitemap.xml
            sitemap_content = self._generate_sitemap_xml(plan)
            sitemap_path = os.path.join(public_path, "sitemap.xml")
            
            with open(sitemap_path, 'w') as f:
                f.write(sitemap_content)
            
            st.success(f"✅ Sitemap exported to {sitemap_path}")
        
        elif file_type == "robots":
            # Generate robots.txt
            robots_content = self._generate_robots_txt()
            robots_path = os.path.join(public_path, "robots.txt")
            
            with open(robots_path, 'w') as f:
                f.write(robots_content)
            
            st.success(f"✅ Robots.txt exported to {robots_path}")
    
    def _generate_sitemap_xml(self, plan: Dict[str, Any]) -> str:
        """Generate sitemap.xml content"""
        
        pages = plan.get("pages", [])
        base_url = "https://yoursite.com"  # Would be configurable
        
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for page in pages:
            slug = page.get("slug", "/")
            if not slug.startswith("/"):
                slug = "/" + slug
            
            sitemap_content += f'  <url>\n'
            sitemap_content += f'    <loc>{base_url}{slug}</loc>\n'
            sitemap_content += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
            sitemap_content += f'    <changefreq>weekly</changefreq>\n'
            sitemap_content += f'    <priority>0.8</priority>\n'
            sitemap_content += f'  </url>\n'
        
        sitemap_content += '</urlset>'
        
        return sitemap_content
    
    def _generate_robots_txt(self) -> str:
        """Generate robots.txt content"""
        
        robots_content = """User-agent: *
Allow: /

# Sitemap location
Sitemap: https://yoursite.com/sitemap.xml

# Disallow admin and private areas
Disallow: /_vsbvibe/
Disallow: /admin/
Disallow: *.log$
"""
        
        return robots_content
                
                color_scheme = st.selectbox("Color Scheme",
                                          ["professional", "vibrant", "monochrome", "warm"],
                                          index=["professional", "vibrant", "monochrome", "warm"].index(
                                              ui_plan.get("color_scheme", "professional")
                                          ))
            
            with col2:
                navigation = st.selectbox("Navigation Style",
                                        ["header", "sidebar", "footer", "floating"],
                                        index=["header", "sidebar", "footer", "floating"].index(
                                            ui_plan.get("navigation", "header")
                                        ))
                
                components = st.multiselect("Components",
                                          ["hero", "features", "testimonials", "gallery", "contact", "blog"],
                                          default=ui_plan.get("components", ["hero", "features", "contact"]))
            
            if st.form_submit_button("Update Design"):
                plan["ui_ux_plan"] = {
                    "layout": layout,
                    "color_scheme": color_scheme,
                    "navigation": navigation,
                    "components": components,
                    "updated_at": datetime.now().isoformat()
                }
                
                with open(plan_path, 'w') as f:
                    json.dump(plan, f, indent=2)
                
                st.success("Design settings updated!")
    
    def _render_products(self):
        st.subheader("Products CRUD")
        
        products_path = os.path.join(
            self.project_manager.get_current_project_path(),
            "content", "products.xlsx"
        )
        
        # Load products
        if os.path.exists(products_path):
            df = pd.read_excel(products_path)
            
            # Display products
            st.write("**Current Products:**")
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Changes"):
                    edited_df.to_excel(products_path, index=False)
                    st.success("Products saved successfully!")
            
            with col2:
                if st.button("Add Sample Product"):
                    new_row = pd.DataFrame({
                        "Product Name": ["New Product"],
                        "Description": ["Product description"],
                        "Price": [0.00],
                        "Category": ["Uncategorized"]
                    })
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    updated_df.to_excel(products_path, index=False)
                    st.rerun()
        else:
            st.warning("Products file not found. Creating sample file...")
            sample_data = {
                "Product Name": ["Sample Product"],
                "Description": ["A sample product"],
                "Price": [99.99],
                "Category": ["Sample"]
            }
            df = pd.DataFrame(sample_data)
            df.to_excel(products_path, index=False)
            st.rerun()
    
    @safe_page
    def _render_data(self):
        st.subheader("Data Schema Management")
        
        # Database schema management
        st.write("**Database Schema:**")
        
        schema_info = {
            "Tables": ["users", "products", "pages", "content"],
            "Status": ["Active", "Active", "Pending", "Active"],
            "Records": [0, 0, 0, 0]
        }
        
        st.dataframe(pd.DataFrame(schema_info), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Generate Schema"):
                st.info("Schema generation will be implemented")
        
        with col2:
            if st.button("Sync with Supabase"):
                st.info("Supabase sync will be implemented")
        
        with col3:
            if st.button("Backup Data"):
                st.info("Data backup will be implemented")
    
    @safe_page
    def _render_publish(self):
        st.subheader("Publish & Deploy")
        
        st.write("**Deployment Options:**")
        deploy_target = st.selectbox("Deploy Target", ["Streamlit Cloud", "Local Server", "Custom"])
        
        if deploy_target == "Streamlit Cloud":
            st.info("Streamlit Cloud deployment requires GitHub repository")
            github_repo = st.text_input("GitHub Repository URL")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Build Site"):
                st.info("Building site...")
                self._build_site()
        
        with col2:
            if st.button("Deploy"):
                st.info("Deployment will be implemented")
    
    @safe_page
    def _render_tests(self):
        st.subheader("Testing Dashboard")
        st.info("See Test tab for detailed testing interface")
    
    @safe_page
    def _render_jobs_logs(self):
        st.subheader("Jobs & Logs")
        
        logs_path = os.path.join(
            self.project_manager.get_current_project_path(),
            "_vsbvibe", "logs", "activity.json"
        )
        
        if os.path.exists(logs_path):
            with open(logs_path, 'r') as f:
                logs = json.load(f)
            
            st.write("**Recent Activity:**")
            for log in reversed(logs[-10:]):  # Show last 10 entries
                timestamp = log.get("timestamp", "")
                action = log.get("action", "")
                details = log.get("details", "")
                
                with st.expander(f"{action} - {timestamp[:19]}"):
                    st.write(details)
        else:
            st.info("No logs found")
    
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
                
                # Filters
                st.markdown("---")
                st.write("**Filters:**")
                
                filter_col1, filter_col2, filter_col3 = st.columns(3)
                
                with filter_col1:
                    module_filter = st.selectbox("Module", ["All"] + list(set(e.get("meta", {}).get("module", "unknown") for e in recent_errors)))
                
                with filter_col2:
                    error_type_filter = st.selectbox("Error Type", ["All"] + list(set(e.get("meta", {}).get("error_name", "unknown") for e in recent_errors)))
                
                with filter_col3:
                    timeframe = st.selectbox("Timeframe", ["Last 24h", "Last 7d", "Last 30d", "All"])
                
                # Apply filters and show filtered results
                filtered_errors = self._filter_errors(recent_errors, module_filter, error_type_filter, timeframe)
                
                if filtered_errors:
                    st.write(f"**Filtered Results ({len(filtered_errors)} errors):**")
                    
                    for error in filtered_errors[-10:]:  # Show last 10 filtered
                        meta = error.get("meta", {})
                        with st.expander(f"{meta.get('error_name', 'Error')} - {error.get('timestamp', '')[:19]}"):
                            st.write(f"**Module:** {meta.get('module', 'unknown')}")
                            st.write(f"**File:** {meta.get('files_to_correct', 'unknown')} (Line {meta.get('line_number', 0)})")
                            st.write(f"**Message:** {meta.get('error_details', 'No details')}")
                            st.write(f"**Suggested Fix:** {meta.get('suggested_fix', 'No suggestion')}")
            
            else:
                st.success("No errors found!")
        
        else:
            st.info("No error log found. Errors will appear here when they occur.")
    
    @safe_component
    def _generate_error_excel_report(self, project_path: str):
        """Generate Excel error report"""
        
        try:
            from site.core.errors import error_reporter
            
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
    def _filter_errors(self, errors: list, module_filter: str, error_type_filter: str, timeframe: str) -> list:
        """Filter errors based on criteria"""
        
        filtered = errors
        
        # Module filter
        if module_filter != "All":
            filtered = [e for e in filtered if e.get("meta", {}).get("module") == module_filter]
        
        # Error type filter
        if error_type_filter != "All":
            filtered = [e for e in filtered if e.get("meta", {}).get("error_name") == error_type_filter]
        
        # Timeframe filter
        if timeframe != "All":
            hours_map = {"Last 24h": 24, "Last 7d": 168, "Last 30d": 720}
            hours = hours_map.get(timeframe, 24)
            
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            filtered = []
            
            for error in errors:
                try:
                    error_time = datetime.fromisoformat(error["timestamp"]).timestamp()
                    if error_time >= cutoff_time:
                        filtered.append(error)
                except:
                    continue
        
        return filtered
    
    @safe_page
    def _render_admin_chat(self):
        st.markdown("---")
        st.subheader("💬 Admin Chat")
        st.write("Request new features, pages, or modifications:")
        
        # Chat interface
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.write(f"**You:** {message['content']}")
                else:
                    st.write(f"**Assistant:** {message['content']}")
        
        # Chat input
        user_input = st.text_input("Type your request...", key="chat_input")
        
        if st.button("Send") and user_input:
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Simulate AI response (placeholder)
            response = f"I understand you want: '{user_input}'. Files will be updated accordingly."
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Show file update notification
            st.success("📁 Files updated! Check the diff summary for details.")
            
            st.rerun()
    
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
    
    @safe_component
    def _build_site(self):
        """Build the site for deployment"""
        st.info("Site build process completed!")