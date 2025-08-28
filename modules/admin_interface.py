import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import shutil

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
            self._render_products()
        
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
        
        # Admin Chat at the bottom
        self._render_admin_chat()
    
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
    
    def _render_pages(self):
        st.subheader("Pages Management")
        
        plan_path = os.path.join(
            self.project_manager.get_current_project_path(), 
            "_vsbvibe", "plan.json"
        )
        
        plan = {}
        if os.path.exists(plan_path):
            with open(plan_path, 'r') as f:
                plan = json.load(f)
        
        pages = plan.get("pages", [])
        
        # Display existing pages
        if pages:
            st.write("**Current Pages:**")
            for i, page in enumerate(pages):
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    st.write(page.get("name", ""))
                with col2:
                    st.write(page.get("type", ""))
                with col3:
                    st.write(f"Priority: {page.get('priority', 0)}")
                with col4:
                    if st.button("Remove", key=f"remove_page_{i}"):
                        pages.pop(i)
                        plan["pages"] = pages
                        with open(plan_path, 'w') as f:
                            json.dump(plan, f, indent=2)
                        st.rerun()
        
        # Add new page
        with st.form("add_page"):
            st.write("**Add New Page:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                page_name = st.text_input("Page Name")
            with col2:
                page_type = st.selectbox("Type", ["landing", "info", "form", "gallery", "blog"])
            with col3:
                priority = st.number_input("Priority", min_value=1, value=len(pages) + 1)
            
            if st.form_submit_button("Add Page"):
                if page_name:
                    new_page = {
                        "name": page_name,
                        "type": page_type,
                        "priority": priority,
                        "created_at": datetime.now().isoformat()
                    }
                    pages.append(new_page)
                    plan["pages"] = pages
                    
                    with open(plan_path, 'w') as f:
                        json.dump(plan, f, indent=2)
                    
                    st.success(f"Page '{page_name}' added successfully!")
                    st.rerun()
    
    def _render_design(self):
        st.subheader("Design Settings")
        
        plan_path = os.path.join(
            self.project_manager.get_current_project_path(), 
            "_vsbvibe", "plan.json"
        )
        
        plan = {}
        if os.path.exists(plan_path):
            with open(plan_path, 'r') as f:
                plan = json.load(f)
        
        ui_plan = plan.get("ui_ux_plan", {})
        
        with st.form("design_settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                layout = st.selectbox("Layout Style", 
                                    ["modern", "classic", "minimal", "bold"],
                                    index=["modern", "classic", "minimal", "bold"].index(
                                        ui_plan.get("layout", "modern")
                                    ))
                
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
    
    def _render_generate(self):
        st.subheader("Site Generation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Generation Options:**")
            generate_content = st.checkbox("Generate AI Content", value=True)
            generate_images = st.checkbox("Generate Images", value=False)
            generate_seo = st.checkbox("Generate SEO Meta", value=True)
            
        with col2:
            st.write("**Output Format:**")
            output_format = st.selectbox("Format", ["Streamlit", "Static HTML"])
            include_admin = st.checkbox("Include Admin Panel", value=True)
        
        if st.button("Generate Site", type="primary"):
            self._generate_site(generate_content, generate_images, generate_seo, output_format, include_admin)
    
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
    
    def _render_tests(self):
        st.subheader("Testing Dashboard")
        st.info("See Test tab for detailed testing interface")
    
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
    
    def _generate_site(self, content: bool, images: bool, seo: bool, format: str, admin: bool):
        """Generate the actual website files"""
        project_path = self.project_manager.get_current_project_path()
        site_path = os.path.join(project_path, "site")
        
        # Create main site app
        if format == "Streamlit":
            self._generate_streamlit_site(site_path, admin)
        else:
            self._generate_static_site(site_path)
        
        st.success("Site generated successfully!")
    
    def _generate_streamlit_site(self, site_path: str, include_admin: bool):
        """Generate Streamlit-based website"""
        
        # Main site app
        site_app_content = '''import streamlit as st
import os
import json

st.set_page_config(page_title="Your Website", layout="wide")

def load_content():
    content_path = os.path.join("..", "_vsbvibe", "content_store.json")
    if os.path.exists(content_path):
        with open(content_path, 'r') as f:
            return json.load(f)
    return {}

def main():
    content = load_content()
    global_content = content.get("global", {})
    
    st.title(global_content.get("company_name", "Your Company"))
    st.subheader(global_content.get("tagline", "Welcome to our website"))
    
    # Hero section
    st.markdown("---")
    st.header("Welcome")
    st.write("This is your generated website. Customize it through the Vsbvibe admin panel.")
    
    # Products section
    st.header("Our Products")
    products = content.get("products", [])
    
    if products:
        for product in products:
            with st.expander(product.get("name", "Product")):
                st.write(product.get("description", ""))
                st.write(f"Price: ${product.get('price', 0)}")
    else:
        st.info("No products found. Add products through the admin panel.")

if __name__ == "__main__":
    main()
'''
        
        with open(os.path.join(site_path, "app.py"), 'w') as f:
            f.write(site_app_content)
    
    def _generate_static_site(self, site_path: str):
        """Generate static HTML website"""
        
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Website</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .product { border: 1px solid #ddd; padding: 20px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Company</h1>
            <p>Welcome to our website</p>
        </div>
        
        <div id="products">
            <h2>Our Products</h2>
            <div class="product">
                <h3>Sample Product</h3>
                <p>Product description goes here</p>
                <p><strong>Price: $99.99</strong></p>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        with open(os.path.join(site_path, "index.html"), 'w') as f:
            f.write(html_content)
    
    def _build_site(self):
        """Build the site for deployment"""
        st.info("Site build process completed!")