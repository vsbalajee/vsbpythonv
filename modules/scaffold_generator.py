"""
Scaffold generation utilities for Vsbvibe
Generates production-ready applications from UI/UX plans with platform awareness
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from .utils import ensure_directory, save_json

class ScaffoldGenerator:
    """Platform-aware scaffold generator"""
    
    def __init__(self, project_config: Dict[str, Any], plan: Dict[str, Any], options: Dict[str, Any] = None):
        self.project_config = project_config
        self.plan = plan
        self.options = options or {}
        self.project_path = project_config.get("local_folder", "")
        self.project_name = project_config.get("project_name", "website")
        
    def generate(self) -> Dict[str, Any]:
        """Generate scaffold based on platform target"""
        
        platform_target = self.plan.get("platform_target")
        
        if platform_target == "streamlit_site":
            return self._generate_streamlit_scaffold()
        elif platform_target == "htmljs":
            return self._generate_htmljs_scaffold()
        elif platform_target == "reactvite":
            return self._generate_reactvite_handoff()
        else:
            return {"success": False, "error": f"Unknown platform target: {platform_target}"}
    
    def _generate_streamlit_scaffold(self) -> Dict[str, Any]:
        """Generate Streamlit scaffold"""
        
        try:
            # Create output directory
            output_path = os.path.join(self.project_path, self.project_name.lower().replace(" ", "-"), "output", "streamlit_site")
            ensure_directory(output_path)
            
            files_created = []
            
            # Generate main app
            app_content = self._generate_streamlit_app()
            app_path = os.path.join(output_path, "app.py")
            with open(app_path, 'w') as f:
                f.write(app_content)
            files_created.append("app.py")
            
            # Generate pages
            pages_path = os.path.join(output_path, "pages")
            ensure_directory(pages_path)
            
            for i, page in enumerate(self.plan.get("pages", [])):
                page_content = self._generate_streamlit_page(page)
                page_filename = f"{i:02d}_{page.get('name', 'Page').replace(' ', '_')}.py"
                page_file_path = os.path.join(pages_path, page_filename)
                
                with open(page_file_path, 'w') as f:
                    f.write(page_content)
                files_created.append(f"pages/{page_filename}")
            
            # Generate components
            components_path = os.path.join(output_path, "components")
            ensure_directory(components_path)
            
            components = self._generate_streamlit_components()
            for component_name, component_content in components.items():
                component_path = os.path.join(components_path, component_name)
                with open(component_path, 'w') as f:
                    f.write(component_content)
                files_created.append(f"components/{component_name}")
            
            # Generate styles
            styles_path = os.path.join(output_path, "styles")
            ensure_directory(styles_path)
            
            # Generate tokens
            tokens = self._generate_design_tokens()
            tokens_path = os.path.join(styles_path, "tokens.json")
            save_json(tokens_path, tokens)
            files_created.append("styles/tokens.json")
            
            # Generate style injector
            inject_content = self._generate_style_injector()
            inject_path = os.path.join(styles_path, "inject.py")
            with open(inject_path, 'w') as f:
                f.write(inject_content)
            files_created.append("styles/inject.py")
            
            # Generate SEO utilities
            if self.options.get("include_seo", True):
                seo_path = os.path.join(output_path, "seo")
                ensure_directory(seo_path)
                
                seo_files = self._generate_seo_utilities()
                for seo_name, seo_content in seo_files.items():
                    seo_file_path = os.path.join(seo_path, seo_name)
                    with open(seo_file_path, 'w') as f:
                        f.write(seo_content)
                    files_created.append(f"seo/{seo_name}")
            
            # Generate preview instructions
            preview_instructions = self._generate_preview_instructions("streamlit_site")
            preview_path = os.path.join(self.project_path, self.project_name.lower().replace(" ", "-"), "_vsbvibe", "preview.json")
            save_json(preview_path, preview_instructions)
            
            # Create diff summary
            self._create_diff_summary(files_created, [])
            
            # Log scaffold generation
            self._log_scaffold_generation("streamlit_site", len(files_created))
            
            return {
                "success": True,
                "platform": "streamlit_site",
                "files_created": files_created,
                "output_path": output_path
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_streamlit_app(self) -> str:
        """Generate main Streamlit app"""
        
        return f'''"""
{self.project_config.get('project_name', 'Website')} - Main Application
Generated by Vsbvibe
"""

import streamlit as st
import sys
import os

# Add components to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'styles'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'seo'))

from nav import render_navigation
from footer import render_footer
from inject import inject_global_styles

# Page configuration
st.set_page_config(
    page_title="{self.project_config.get('project_name', 'Website')}",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """Main application entry point"""
    
    # Inject global styles
    inject_global_styles()
    
    # Render navigation
    render_navigation()
    
    # Main content
    st.title("Welcome to {self.project_config.get('company_name', 'Our Company')}")
    st.write("Your website is ready! Navigate using the pages in the sidebar.")
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
'''
    
    def _generate_streamlit_page(self, page: Dict[str, Any]) -> str:
        """Generate individual Streamlit page"""
        
        page_name = page.get("name", "Page")
        page_type = page.get("type", "generic")
        
        return f'''"""
{page_name} Page - {self.project_config.get('project_name', 'Website')}
Generated by Vsbvibe
"""

import streamlit as st
import sys
import os

# Add components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'styles'))

from nav import render_navigation
from footer import render_footer
from inject import inject_global_styles

# Page configuration
st.set_page_config(
    page_title="{page_name} - {self.project_config.get('project_name', 'Website')}",
    page_icon="🚀",
    layout="wide"
)

def main():
    """Main page function"""
    
    # Inject global styles
    inject_global_styles()
    
    # Render navigation
    render_navigation()
    
    # Page content
    st.title("{page_name}")
    st.write("Welcome to the {page_name.lower()} page.")
    
    # TODO: Add page-specific content in Step 5
    st.info("Page content will be added in Step 5 - Data & Products")
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
'''
    
    def _generate_streamlit_components(self) -> Dict[str, str]:
        """Generate Streamlit components"""
        
        components = {}
        
        # Navigation component
        nav_items = self.plan.get("navigation", {}).get("header", [])
        
        components["nav.py"] = f'''"""
Navigation component
"""

import streamlit as st

def render_navigation():
    """Render main navigation"""
    
    # Navigation bar
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"**{self.project_config.get('company_name', 'Company')}**")
    
    with col2:
        nav_cols = st.columns(len({nav_items}) if {nav_items} else 3)
        
        nav_items_list = {nav_items} if {nav_items} else [
            {{"name": "Home", "url": "/"}},
            {{"name": "About", "url": "/about"}},
            {{"name": "Contact", "url": "/contact"}}
        ]
        
        for i, item in enumerate(nav_items_list):
            with nav_cols[i]:
                if st.button(item.get("name", "Link"), key=f"nav_{{i}}"):
                    st.info(f"Navigation to {{item.get('name', 'Page')}}")
'''
        
        # Footer component
        components["footer.py"] = f'''"""
Footer component
"""

import streamlit as st

def render_footer():
    """Render site footer"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("{self.project_config.get('company_name', 'Company')}")
        st.write("Your trusted partner for professional services.")
    
    with col2:
        st.subheader("Quick Links")
        st.markdown("- [Home](/)\\n- [About](/about)\\n- [Contact](/contact)")
    
    with col3:
        st.subheader("Contact")
        st.write("Email: info@company.com\\nPhone: (555) 123-4567")
    
    # Copyright
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #6c757d;'>"
        f"© 2024 {self.project_config.get('company_name', 'Company')}. All rights reserved."
        f"</div>", 
        unsafe_allow_html=True
    )
'''
        
        return components
    
    def _generate_design_tokens(self) -> Dict[str, Any]:
        """Generate design tokens"""
        
        brand_tokens = self.plan.get("brand_tokens", {})
        
        return {
            "colors": {
                "primary": brand_tokens.get("primary_color", "#2563eb"),
                "secondary": brand_tokens.get("secondary_color", "#64748b"),
                "accent": brand_tokens.get("accent_color", "#10b981"),
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "info": "#3b82f6"
            },
            "typography": {
                "font_family": brand_tokens.get("font_family", "Inter, sans-serif"),
                "font_sizes": {
                    "xs": "0.75rem",
                    "sm": "0.875rem", 
                    "base": "1rem",
                    "lg": "1.125rem",
                    "xl": "1.25rem",
                    "2xl": "1.5rem"
                }
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem", 
                "lg": "1.5rem",
                "xl": "2rem"
            }
        }
    
    def _generate_style_injector(self) -> str:
        """Generate CSS injection utility"""
        
        brand_tokens = self.plan.get("brand_tokens", {})
        primary_color = brand_tokens.get("primary_color", "#2563eb")
        
        return f'''"""
Global style injection for Streamlit
"""

import streamlit as st
import json
import os

def inject_global_styles():
    """Inject global CSS styles"""
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main .block-container {{
        padding-top: 2rem;
        max-width: 1200px;
    }}
    
    .stButton > button[kind="primary"] {{
        background-color: {primary_color};
        border-color: {primary_color};
        color: white;
        border-radius: 8px;
        font-weight: 500;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: {primary_color}dd;
        transform: translateY(-1px);
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
'''
    
    def _generate_seo_utilities(self) -> Dict[str, str]:
        """Generate SEO utility files"""
        
        seo_files = {}
        
        # JSON-LD utility
        seo_files["jsonld.py"] = '''"""
JSON-LD schema markup utilities
"""

import json
from typing import Dict, Any

def generate_organization_schema(name: str, url: str) -> Dict[str, Any]:
    """Generate Organization schema"""
    return {
        "@context": "https://schema.org",
        "@type": "Organization", 
        "name": name,
        "url": url
    }

def generate_website_schema(name: str, url: str) -> Dict[str, Any]:
    """Generate Website schema"""
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": name,
        "url": url
    }
'''
        
        # Sitemap utility
        seo_files["sitemap.py"] = '''"""
Sitemap generation utilities
"""

from datetime import datetime
from typing import List, Dict, Any

def generate_sitemap_xml(pages: List[Dict[str, Any]], base_url: str = "https://example.com") -> str:
    """Generate sitemap.xml content"""
    
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    
    for page in pages:
        url = page.get("slug", "/")
        if not url.startswith("http"):
            url = base_url.rstrip("/") + url
        
        xml_content += f'''
    <url>
        <loc>{url}</loc>
        <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>{"1.0" if page.get("slug") == "/" else "0.8"}</priority>
    </url>'''
    
    xml_content += '''
</urlset>'''
    
    return xml_content
'''
        
        return seo_files
    
    def _generate_preview_instructions(self, platform: str) -> Dict[str, Any]:
        """Generate preview instructions"""
        
        if platform == "streamlit_site":
            return {
                "platform": "streamlit_site",
                "instructions": [
                    "Navigate to the output/streamlit_site directory",
                    "Run: streamlit run app.py",
                    "Open browser to http://localhost:8501",
                    "Use sidebar navigation to view different pages"
                ],
                "requirements": ["streamlit>=1.29.0", "pandas>=2.0.0"],
                "notes": "Ensure all dependencies are installed before running"
            }
        
        return {"platform": platform, "instructions": [], "requirements": [], "notes": ""}
    
    def _create_diff_summary(self, files_created: List[str], files_updated: List[str]):
        """Create diff summary"""
        
        diff_summary = {
            "timestamp": datetime.now().isoformat(),
            "operation": "scaffold_generation",
            "platform": self.plan.get("platform_target"),
            "files_created": files_created,
            "files_updated": files_updated,
            "total_files": len(files_created) + len(files_updated),
            "summary": f"Generated {len(files_created)} files for {self.plan.get('platform_target')} platform"
        }
        
        diff_path = os.path.join(
            self.project_path, 
            self.project_name.lower().replace(" ", "-"),
            "_vsbvibe", 
            "diff_summary.json"
        )
        
        save_json(diff_path, diff_summary)
    
    def _log_scaffold_generation(self, platform: str, files_count: int):
        """Log scaffold generation"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "scaffold_generated",
            "platform": platform,
            "files_count": files_count,
            "project": self.project_config.get("project_name")
        }
        
        log_path = os.path.join(
            self.project_path,
            self.project_name.lower().replace(" ", "-"),
            "_vsbvibe", 
            "logs", 
            "scaffold.log"
        )
        
        ensure_directory(os.path.dirname(log_path))
        
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\\n")
    
    def _generate_htmljs_scaffold(self) -> Dict[str, Any]:
        """Generate HTML/JS scaffold (placeholder)"""
        return {"success": False, "error": "HTML/JS scaffold not implemented yet"}
    
    def _generate_reactvite_handoff(self) -> Dict[str, Any]:
        """Generate React/Vite handoff (placeholder)"""
        return {"success": False, "error": "React/Vite handoff not implemented yet"}

def generate_main_app(plan: Dict[str, Any], project_config: Dict[str, Any]) -> str:
    """Generate the main Streamlit app.py file"""
    
    project_name = project_config.get("project_name", "My Website")
    company_name = project_config.get("company_name", "My Company")
    
    # Get navigation from plan
    navigation = plan.get("navigation", {})
    header_items = navigation.get("header", [])
    
    app_content = f'''"""
{project_name} - Main Streamlit Application
Generated by Vsbvibe
"""

import streamlit as st
import sys
import os

# Add components to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'styles'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'seo'))

from nav import render_navigation
from footer import render_footer
from inject import inject_global_styles

# Page configuration
st.set_page_config(
    page_title="{project_name}",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """Main application entry point"""
    
    # Inject global styles
    inject_global_styles()
    
    # Render navigation
    render_navigation()
    
    # Main content area
    st.title("Welcome to {company_name}")
    st.markdown("---")
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Your Success is Our Mission")
        st.write("""
        Welcome to our website. We're here to help you achieve your goals 
        with our professional services and solutions.
        """)
        
        if st.button("Get Started", type="primary"):
            st.success("Thank you for your interest! Contact us to learn more.")
    
    with col2:
        st.image("https://via.placeholder.com/400x300/007bff/ffffff?text=Hero+Image", 
                caption="Professional Services")
    
    # Features section
    st.markdown("---")
    st.header("Our Services")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🎯 Strategy")
        st.write("Strategic planning and consultation to help you reach your goals.")
    
    with col2:
        st.subheader("⚡ Implementation")
        st.write("Expert implementation of solutions tailored to your needs.")
    
    with col3:
        st.subheader("📈 Growth")
        st.write("Ongoing support and optimization for sustainable growth.")
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
'''
    
    return app_content

def generate_page(page: Dict[str, Any], plan: Dict[str, Any], project_config: Dict[str, Any]) -> str:
    """Generate individual page files"""
    
    page_name = page.get("name", "Unknown")
    page_type = page.get("type", "generic")
    sections = page.get("sections", [])
    
    # Import statements
    imports = '''import streamlit as st
import sys
import os

# Add components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'styles'))

from nav import render_navigation
from footer import render_footer
from inject import inject_global_styles
'''
    
    # Page-specific imports based on type
    if page_type in ["product_list", "product_detail"]:
        imports += "from product_card import render_product_card\\n"
    
    if page_type == "contact":
        imports += "from grids import render_contact_form\\n"
    
    # Page configuration
    page_config = f'''
st.set_page_config(
    page_title="{page_name} - {project_config.get('project_name', 'Website')}",
    page_icon="🚀",
    layout="wide"
)
'''
    
    # Main function based on page type
    if page_type == "home":
        main_content = generate_home_page_content(sections, project_config)
    elif page_type == "product_list":
        main_content = generate_product_list_content(sections, project_config)
    elif page_type == "product_detail":
        main_content = generate_product_detail_content(sections, project_config)
    elif page_type == "contact":
        main_content = generate_contact_page_content(sections, project_config)
    elif page_type == "blog":
        main_content = generate_blog_page_content(sections, project_config)
    else:
        main_content = generate_generic_page_content(page_name, sections, project_config)
    
    page_content = f'''{imports}

{page_config}

def main():
    """Main page function"""
    
    # Inject global styles
    inject_global_styles()
    
    # Render navigation
    render_navigation()
    
{main_content}
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
'''
    
    return page_content

def generate_home_page_content(sections: List[Dict], project_config: Dict[str, Any]) -> str:
    """Generate home page content"""
    company_name = project_config.get("company_name", "My Company")
    
    return f'''    # Hero Section
    st.title("Welcome to {company_name}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Your Success is Our Mission")
        st.write("""
        We provide professional services and solutions to help you 
        achieve your business goals. Our experienced team is dedicated 
        to delivering exceptional results.
        """)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Get Started", type="primary"):
                st.success("Thank you for your interest!")
        with col_b:
            if st.button("Learn More"):
                st.info("Contact us to learn more about our services.")
    
    with col2:
        st.image("https://via.placeholder.com/400x300/007bff/ffffff?text=Hero+Image", 
                caption="Professional Services")
    
    # Features Section
    st.markdown("---")
    st.header("Why Choose Us")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🎯 Expertise")
        st.write("Years of experience in delivering quality solutions.")
    
    with col2:
        st.subheader("⚡ Efficiency")
        st.write("Fast and reliable service delivery.")
    
    with col3:
        st.subheader("📈 Results")
        st.write("Proven track record of successful projects.")
'''

def generate_product_list_content(sections: List[Dict], project_config: Dict[str, Any]) -> str:
    """Generate product list page content"""
    return '''    # Product List Page
    st.title("Our Products")
    st.write("Discover our range of products and services.")
    
    # Search and filters
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("Search products...", placeholder="Enter product name")
    
    with col2:
        category = st.selectbox("Category", ["All", "Category A", "Category B", "Category C"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Name", "Price", "Popularity"])
    
    # Product grid
    st.markdown("---")
    
    # Sample products (will be replaced with real data in Step 5)
    products = [
        {"name": "Product 1", "price": "$99.99", "image": "https://via.placeholder.com/300x200/28a745/ffffff?text=Product+1"},
        {"name": "Product 2", "price": "$149.99", "image": "https://via.placeholder.com/300x200/dc3545/ffffff?text=Product+2"},
        {"name": "Product 3", "price": "$79.99", "image": "https://via.placeholder.com/300x200/ffc107/ffffff?text=Product+3"},
        {"name": "Product 4", "price": "$199.99", "image": "https://via.placeholder.com/300x200/17a2b8/ffffff?text=Product+4"},
    ]
    
    # Display products in grid
    cols = st.columns(2)
    for i, product in enumerate(products):
        with cols[i % 2]:
            with st.container():
                st.image(product["image"], use_column_width=True)
                st.subheader(product["name"])
                st.write(f"**Price:** {product['price']}")
                if st.button(f"View Details", key=f"product_{i}"):
                    st.success(f"Viewing {product['name']} details...")
                st.markdown("---")
'''

def generate_product_detail_content(sections: List[Dict], project_config: Dict[str, Any]) -> str:
    """Generate product detail page content"""
    return '''    # Product Detail Page
    st.title("Product Details")
    
    # Breadcrumb
    st.markdown("🏠 [Home](/) > [Products](/Shop) > Product Name")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Product image
        st.image("https://via.placeholder.com/500x400/007bff/ffffff?text=Product+Image", 
                caption="Product Image")
        
        # Thumbnail gallery
        st.write("**More Images:**")
        thumb_cols = st.columns(4)
        for i in range(4):
            with thumb_cols[i]:
                st.image(f"https://via.placeholder.com/100x80/6c757d/ffffff?text=Thumb+{i+1}")
    
    with col2:
        # Product info
        st.header("Sample Product")
        st.subheader("$149.99")
        
        st.write("""
        **Description:**
        This is a detailed description of the product. It includes all the 
        important features, benefits, and specifications that customers 
        need to know before making a purchase decision.
        """)
        
        # Product options
        st.write("**Options:**")
        size = st.selectbox("Size", ["Small", "Medium", "Large", "X-Large"])
        color = st.selectbox("Color", ["Red", "Blue", "Green", "Black"])
        quantity = st.number_input("Quantity", min_value=1, value=1)
        
        # Action buttons
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Add to Cart", type="primary"):
                st.success("Added to cart!")
        with col_b:
            if st.button("Buy Now"):
                st.info("Redirecting to checkout...")
    
    # Product details tabs
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Description", "Specifications", "Reviews"])
    
    with tab1:
        st.write("""
        **Detailed Description:**
        
        This product is designed with quality and functionality in mind. 
        It features premium materials and expert craftsmanship to ensure 
        long-lasting performance and satisfaction.
        
        **Key Features:**
        - High-quality materials
        - Expert craftsmanship
        - Durable construction
        - Satisfaction guaranteed
        """)
    
    with tab2:
        st.write("""
        **Technical Specifications:**
        
        - Dimensions: 10" x 8" x 2"
        - Weight: 2.5 lbs
        - Material: Premium grade
        - Color options: Multiple
        - Warranty: 1 year
        """)
    
    with tab3:
        st.write("**Customer Reviews:**")
        
        # Sample reviews
        reviews = [
            {"name": "John D.", "rating": 5, "comment": "Excellent product! Highly recommended."},
            {"name": "Sarah M.", "rating": 4, "comment": "Good quality, fast shipping."},
            {"name": "Mike R.", "rating": 5, "comment": "Perfect for my needs. Great value."}
        ]
        
        for review in reviews:
            st.write(f"**{review['name']}** - {'⭐' * review['rating']}")
            st.write(f"*{review['comment']}*")
            st.markdown("---")
'''

def generate_contact_page_content(sections: List[Dict], project_config: Dict[str, Any]) -> str:
    """Generate contact page content"""
    company_name = project_config.get("company_name", "My Company")
    
    return f'''    # Contact Page
    st.title("Contact {company_name}")
    st.write("Get in touch with us. We'd love to hear from you!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Send us a message")
        
        with st.form("contact_form"):
            name = st.text_input("Full Name *")
            email = st.text_input("Email Address *")
            phone = st.text_input("Phone Number")
            subject = st.text_input("Subject *")
            message = st.text_area("Message *", height=150)
            
            # Form submission
            submitted = st.form_submit_button("Send Message", type="primary")
            
            if submitted:
                if name and email and subject and message:
                    st.success("Thank you for your message! We'll get back to you soon.")
                else:
                    st.error("Please fill in all required fields.")
    
    with col2:
        st.subheader("Contact Information")
        
        st.write("""
        **Address:**
        123 Business Street
        Suite 100
        City, State 12345
        
        **Phone:**
        (555) 123-4567
        
        **Email:**
        info@company.com
        
        **Business Hours:**
        Monday - Friday: 9:00 AM - 6:00 PM
        Saturday: 10:00 AM - 4:00 PM
        Sunday: Closed
        """)
        
        # Map placeholder
        st.subheader("Location")
        st.image("https://via.placeholder.com/300x200/6c757d/ffffff?text=Map+Placeholder", 
                caption="Our Location")
'''

def generate_blog_page_content(sections: List[Dict], project_config: Dict[str, Any]) -> str:
    """Generate blog page content"""
    return '''    # Blog Page
    st.title("Our Blog")
    st.write("Stay updated with our latest news, insights, and updates.")
    
    # Blog filters
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search = st.text_input("Search articles...", placeholder="Enter keywords")
    
    with col2:
        category = st.selectbox("Category", ["All", "News", "Insights", "Updates", "Tips"])
    
    st.markdown("---")
    
    # Sample blog posts
    posts = [
        {
            "title": "Getting Started with Our Services",
            "date": "March 15, 2024",
            "category": "Tips",
            "excerpt": "Learn how to make the most of our services with this comprehensive guide.",
            "image": "https://via.placeholder.com/400x200/007bff/ffffff?text=Blog+Post+1"
        },
        {
            "title": "Industry Insights and Trends",
            "date": "March 10, 2024", 
            "category": "Insights",
            "excerpt": "Stay ahead of the curve with our analysis of current industry trends.",
            "image": "https://via.placeholder.com/400x200/28a745/ffffff?text=Blog+Post+2"
        },
        {
            "title": "Company News and Updates",
            "date": "March 5, 2024",
            "category": "News", 
            "excerpt": "Read about our latest developments and company milestones.",
            "image": "https://via.placeholder.com/400x200/dc3545/ffffff?text=Blog+Post+3"
        }
    ]
    
    # Display blog posts
    for post in posts:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(post["image"], use_column_width=True)
        
        with col2:
            st.subheader(post["title"])
            st.write(f"**{post['date']}** | *{post['category']}*")
            st.write(post["excerpt"])
            
            if st.button(f"Read More", key=f"post_{post['title']}"):
                st.success("Opening full article...")
        
        st.markdown("---")
'''

def generate_generic_page_content(page_name: str, sections: List[Dict], project_config: Dict[str, Any]) -> str:
    """Generate generic page content"""
    return f'''    # {page_name} Page
    st.title("{page_name}")
    st.write("Welcome to the {page_name.lower()} page.")
    
    # Page content sections
    for section in {sections}:
        st.markdown("---")
        st.header(section.get("name", "Section"))
        st.write("This section will contain relevant content based on your requirements.")
    
    # Call to action
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("Get Started", type="primary"):
            st.success("Thank you for your interest!")
'''

def generate_components(plan: Dict[str, Any], project_config: Dict[str, Any]) -> Dict[str, str]:
    """Generate component files"""
    
    components = {}
    
    # Navigation component
    navigation = plan.get("navigation", {})
    header_items = navigation.get("header", [])
    
    nav_content = f'''"""
Navigation component for {project_config.get("project_name", "Website")}
"""

import streamlit as st

def render_navigation():
    """Render the main navigation"""
    
    # Header navigation
    st.markdown("""
    <style>
    .nav-container {{
        background-color: #ffffff;
        padding: 1rem 0;
        border-bottom: 1px solid #e9ecef;
        margin-bottom: 2rem;
    }}
    .nav-brand {{
        font-size: 1.5rem;
        font-weight: bold;
        color: #007bff;
        text-decoration: none;
    }}
    .nav-links {{
        display: flex;
        gap: 2rem;
        align-items: center;
    }}
    .nav-link {{
        color: #495057;
        text-decoration: none;
        font-weight: 500;
    }}
    .nav-link:hover {{
        color: #007bff;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Navigation bar
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f'<a href="/" class="nav-brand">{project_config.get("company_name", "Company")}</a>', 
                   unsafe_allow_html=True)
    
    with col2:
        # Navigation menu
        nav_cols = st.columns(len({header_items}) if {header_items} else 4)
        
        nav_items = {header_items} if {header_items} else [
            {{"name": "Home", "url": "/"}},
            {{"name": "Products", "url": "/Shop"}},
            {{"name": "About", "url": "/About"}},
            {{"name": "Contact", "url": "/Contact"}}
        ]
        
        for i, item in enumerate(nav_items):
            with nav_cols[i]:
                if st.button(item.get("name", "Link"), key=f"nav_{i}"):
                    st.info(f"Navigation to {{item.get('name', 'Page')}}")
'''
    
    components["nav.py"] = nav_content
    
    # Footer component
    footer_content = f'''"""
Footer component for {project_config.get("project_name", "Website")}
"""

import streamlit as st

def render_footer():
    """Render the site footer"""
    
    st.markdown("---")
    
    # Footer content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("{project_config.get('company_name', 'Company')}")
        st.write("""
        Your trusted partner for professional services and solutions.
        """)
    
    with col2:
        st.subheader("Quick Links")
        st.markdown("""
        - [Home](/)
        - [Products](/Shop)
        - [About](/About)
        - [Contact](/Contact)
        """)
    
    with col3:
        st.subheader("Contact Info")
        st.write("""
        **Email:** info@company.com
        **Phone:** (555) 123-4567
        **Address:** 123 Business St, City, State
        """)
    
    # Copyright
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #6c757d;'>"
        f"© 2024 {project_config.get('company_name', 'Company')}. All rights reserved."
        f"</div>", 
        unsafe_allow_html=True
    )
'''
    
    components["footer.py"] = footer_content
    
    # Hero component
    hero_content = '''"""
Hero section component
"""

import streamlit as st

def render_hero(title: str, subtitle: str, cta_text: str = "Get Started", image_url: str = None):
    """Render a hero section"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title(title)
        st.write(subtitle)
        
        if st.button(cta_text, type="primary"):
            st.success("Thank you for your interest!")
    
    with col2:
        if image_url:
            st.image(image_url, caption="Hero Image")
        else:
            st.image("https://via.placeholder.com/400x300/007bff/ffffff?text=Hero+Image", 
                    caption="Hero Image")

def render_feature_grid(features: list):
    """Render a grid of features"""
    
    cols = st.columns(len(features))
    
    for i, feature in enumerate(features):
        with cols[i]:
            st.subheader(feature.get("icon", "🎯") + " " + feature.get("title", "Feature"))
            st.write(feature.get("description", "Feature description"))
'''
    
    components["hero.py"] = hero_content
    
    # Product card component
    product_card_content = '''"""
Product card component
"""

import streamlit as st

def render_product_card(product: dict, key: str = None):
    """Render a product card"""
    
    with st.container():
        # Product image
        image_url = product.get("image", "https://via.placeholder.com/300x200/007bff/ffffff?text=Product")
        st.image(image_url, use_column_width=True)
        
        # Product info
        st.subheader(product.get("name", "Product Name"))
        st.write(f"**Price:** {product.get('price', '$0.00')}")
        
        # Description
        if product.get("description"):
            st.write(product["description"][:100] + "..." if len(product.get("description", "")) > 100 else product.get("description", ""))
        
        # Action button
        if st.button("View Details", key=key or f"product_{product.get('id', 'unknown')}"):
            st.success(f"Viewing {product.get('name', 'product')} details...")

def render_product_grid(products: list, columns: int = 3):
    """Render a grid of product cards"""
    
    if not products:
        st.info("No products available")
        return
    
    # Create columns
    cols = st.columns(columns)
    
    for i, product in enumerate(products):
        with cols[i % columns]:
            render_product_card(product, key=f"grid_product_{i}")
            st.markdown("---")
'''
    
    components["product_card.py"] = product_card_content
    
    # Grids component
    grids_content = '''"""
Grid and layout components
"""

import streamlit as st

def render_contact_form():
    """Render a contact form"""
    
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *")
            email = st.text_input("Email Address *")
        
        with col2:
            phone = st.text_input("Phone Number")
            subject = st.text_input("Subject *")
        
        message = st.text_area("Message *", height=150)
        
        submitted = st.form_submit_button("Send Message", type="primary")
        
        if submitted:
            if name and email and subject and message:
                st.success("Thank you for your message! We'll get back to you soon.")
                return True
            else:
                st.error("Please fill in all required fields.")
                return False

def render_testimonials(testimonials: list):
    """Render testimonials grid"""
    
    if not testimonials:
        return
    
    st.subheader("What Our Customers Say")
    
    cols = st.columns(min(len(testimonials), 3))
    
    for i, testimonial in enumerate(testimonials):
        with cols[i % 3]:
            st.write(f"*\\"{testimonial.get('text', 'Great service!')}\\"*")
            st.write(f"**{testimonial.get('name', 'Customer')}**")
            st.write(f"{'⭐' * testimonial.get('rating', 5)}")

def render_stats_grid(stats: list):
    """Render statistics grid"""
    
    if not stats:
        return
    
    cols = st.columns(len(stats))
    
    for i, stat in enumerate(stats):
        with cols[i]:
            st.metric(
                label=stat.get("label", "Metric"),
                value=stat.get("value", "0"),
                delta=stat.get("delta")
            )
'''
    
    components["grids.py"] = grids_content
    
    # Media component
    media_content = '''"""
Media handling components
"""

import streamlit as st

def render_lazy_image(src: str, alt: str = "", caption: str = "", use_column_width: bool = False):
    """Render an image with lazy loading simulation"""
    
    # In a real implementation, this would handle lazy loading
    # For Streamlit, we'll use the standard image component
    st.image(src, caption=caption, use_column_width=use_column_width)
    
    # Add alt text as caption if provided
    if alt and not caption:
        st.caption(alt)

def render_image_gallery(images: list, columns: int = 3):
    """Render an image gallery"""
    
    if not images:
        st.info("No images available")
        return
    
    cols = st.columns(columns)
    
    for i, image in enumerate(images):
        with cols[i % columns]:
            render_lazy_image(
                src=image.get("src", "https://via.placeholder.com/300x200"),
                alt=image.get("alt", f"Image {i+1}"),
                caption=image.get("caption", ""),
                use_column_width=True
            )

def render_video_embed(video_url: str, title: str = "Video"):
    """Render embedded video"""
    
    st.subheader(title)
    
    # For demo purposes, show placeholder
    st.info(f"Video: {video_url}")
    st.image("https://via.placeholder.com/600x400/dc3545/ffffff?text=Video+Placeholder")
'''
    
    components["media.py"] = media_content
    
    return components

def generate_tokens(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Generate design tokens JSON"""
    
    brand_tokens = plan.get("brand_tokens", {})
    
    tokens = {
        "colors": {
            "primary": brand_tokens.get("primary_color", "#007bff"),
            "secondary": brand_tokens.get("secondary_color", "#6c757d"),
            "accent": brand_tokens.get("accent_color", "#28a745"),
            "success": "#28a745",
            "warning": "#ffc107",
            "danger": "#dc3545",
            "info": "#17a2b8",
            "light": "#f8f9fa",
            "dark": "#343a40",
            "white": "#ffffff",
            "black": "#000000"
        },
        "typography": {
            "font_family": brand_tokens.get("font_family", "Inter, -apple-system, BlinkMacSystemFont, sans-serif"),
            "font_sizes": {
                "xs": "0.75rem",
                "sm": "0.875rem",
                "base": "1rem",
                "lg": "1.125rem",
                "xl": "1.25rem",
                "2xl": "1.5rem",
                "3xl": "1.875rem",
                "4xl": "2.25rem"
            },
            "font_weights": {
                "light": "300",
                "normal": "400",
                "medium": "500",
                "semibold": "600",
                "bold": "700"
            },
            "line_heights": {
                "tight": "1.25",
                "normal": "1.5",
                "relaxed": "1.75"
            }
        },
        "spacing": {
            "xs": "0.25rem",
            "sm": "0.5rem",
            "md": "1rem",
            "lg": "1.5rem",
            "xl": "2rem",
            "2xl": "3rem",
            "3xl": "4rem"
        },
        "borders": {
            "radius": {
                "sm": brand_tokens.get("border_radius", "4px"),
                "md": "8px",
                "lg": "12px",
                "xl": "16px",
                "full": "9999px"
            },
            "width": {
                "thin": "1px",
                "medium": "2px",
                "thick": "4px"
            }
        },
        "shadows": {
            "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
        },
        "breakpoints": {
            "sm": "640px",
            "md": "768px", 
            "lg": "1024px",
            "xl": "1280px"
        }
    }
    
    return tokens

def generate_style_injector(plan: Dict[str, Any]) -> str:
    """Generate CSS injection utility"""
    
    brand_tokens = plan.get("brand_tokens", {})
    primary_color = brand_tokens.get("primary_color", "#007bff")
    font_family = brand_tokens.get("font_family", "Inter, sans-serif")
    
    inject_content = f'''"""
Global style injection for Streamlit
"""

import streamlit as st
import json
import os

def load_tokens():
    """Load design tokens from JSON file"""
    tokens_path = os.path.join(os.path.dirname(__file__), "tokens.json")
    
    try:
        with open(tokens_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback tokens
        return {{
            "colors": {{
                "primary": "{primary_color}",
                "secondary": "#6c757d"
            }},
            "typography": {{
                "font_family": "{font_family}"
            }}
        }}

def inject_global_styles():
    """Inject global CSS styles into Streamlit"""
    
    tokens = load_tokens()
    colors = tokens.get("colors", {{}})
    typography = tokens.get("typography", {{}})
    
    css = f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}
    
    /* Typography */
    html, body, [class*="css"] {{
        font-family: {typography.get("font_family", "Inter, sans-serif")};
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {colors.get("dark", "#343a40")};
        font-weight: 600;
    }}
    
    /* Primary button styling */
    .stButton > button[kind="primary"] {{
        background-color: {colors.get("primary", "#007bff")};
        border-color: {colors.get("primary", "#007bff")};
        color: white;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: {colors.get("primary", "#007bff")}dd;
        border-color: {colors.get("primary", "#007bff")}dd;
        transform: translateY(-1px);
    }}
    
    /* Secondary button styling */
    .stButton > button[kind="secondary"] {{
        background-color: transparent;
        border: 2px solid {colors.get("primary", "#007bff")};
        color: {colors.get("primary", "#007bff")};
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background-color: {colors.get("primary", "#007bff")};
        color: white;
    }}
    
    /* Form inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {{
        border-radius: 8px;
        border: 2px solid #e9ecef;
        font-family: {typography.get("font_family", "Inter, sans-serif")};
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {{
        border-color: {colors.get("primary", "#007bff")};
        box-shadow: 0 0 0 0.2rem {colors.get("primary", "#007bff")}25;
    }}
    
    /* Cards and containers */
    .element-container {{
        margin-bottom: 1rem;
    }}
    
    /* Success/Error messages */
    .stSuccess {{
        background-color: {colors.get("success", "#28a745")}15;
        border-left: 4px solid {colors.get("success", "#28a745")};
        border-radius: 4px;
    }}
    
    .stError {{
        background-color: {colors.get("danger", "#dc3545")}15;
        border-left: 4px solid {colors.get("danger", "#dc3545")};
        border-radius: 4px;
    }}
    
    .stInfo {{
        background-color: {colors.get("info", "#17a2b8")}15;
        border-left: 4px solid {colors.get("info", "#17a2b8")};
        border-radius: 4px;
    }}
    
    .stWarning {{
        background-color: {colors.get("warning", "#ffc107")}15;
        border-left: 4px solid {colors.get("warning", "#ffc107")};
        border-radius: 4px;
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
    }}
    
    /* Custom utility classes */
    .text-center {{
        text-align: center;
    }}
    
    .text-muted {{
        color: {colors.get("secondary", "#6c757d")};
    }}
    
    .border-bottom {{
        border-bottom: 1px solid #e9ecef;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def inject_page_styles(page_specific_css: str = ""):
    """Inject page-specific styles"""
    if page_specific_css:
        st.markdown(f"<style>{page_specific_css}</style>", unsafe_allow_html=True)
'''
    
    return inject_content

def generate_seo_utilities(seo_defaults: Dict[str, Any], project_config: Dict[str, Any]) -> Dict[str, str]:
    """Generate SEO utility files"""
    
    seo_files = {}
    
    # JSON-LD utility
    jsonld_content = f'''"""
JSON-LD schema markup utilities
"""

import json
from typing import Dict, Any, List

def generate_organization_schema(
    name: str = "{project_config.get('company_name', 'Company')}",
    url: str = "https://example.com",
    logo: str = None,
    contact_info: Dict[str, str] = None
) -> Dict[str, Any]:
    """Generate Organization JSON-LD schema"""
    
    schema = {{
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": name,
        "url": url
    }}
    
    if logo:
        schema["logo"] = logo
    
    if contact_info:
        schema["contactPoint"] = {{
            "@type": "ContactPoint",
            "telephone": contact_info.get("phone", ""),
            "contactType": "customer service",
            "email": contact_info.get("email", "")
        }}
    
    return schema

def generate_website_schema(
    name: str = "{project_config.get('project_name', 'Website')}",
    url: str = "https://example.com",
    description: str = None
) -> Dict[str, Any]:
    """Generate WebSite JSON-LD schema"""
    
    schema = {{
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": name,
        "url": url
    }}
    
    if description:
        schema["description"] = description
    
    # Add potential search action
    schema["potentialAction"] = {{
        "@type": "SearchAction",
        "target": f"{{url}}/search?q={{search_term_string}}",
        "query-input": "required name=search_term_string"
    }}
    
    return schema

def generate_breadcrumb_schema(breadcrumbs: List[Dict[str, str]]) -> Dict[str, Any]:
    """Generate BreadcrumbList JSON-LD schema"""
    
    items = []
    for i, crumb in enumerate(breadcrumbs):
        items.append({{
            "@type": "ListItem",
            "position": i + 1,
            "name": crumb.get("name", ""),
            "item": crumb.get("url", "")
        }})
    
    return {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }}

def generate_product_schema(
    name: str,
    description: str,
    price: str,
    currency: str = "USD",
    availability: str = "InStock",
    image: str = None,
    brand: str = None
) -> Dict[str, Any]:
    """Generate Product JSON-LD schema"""
    
    schema = {{
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "description": description,
        "offers": {{
            "@type": "Offer",
            "price": price,
            "priceCurrency": currency,
            "availability": f"https://schema.org/{{availability}}"
        }}
    }}
    
    if image:
        schema["image"] = image
    
    if brand:
        schema["brand"] = {{
            "@type": "Brand",
            "name": brand
        }}
    
    return schema

def render_json_ld(schema: Dict[str, Any]) -> str:
    """Render JSON-LD script tag"""
    
    json_str = json.dumps(schema, indent=2)
    return f'<script type="application/ld+json">{{json_str}}</script>'

def get_enabled_schemas(seo_config: Dict[str, Any]) -> List[str]:
    """Get list of enabled JSON-LD schemas"""
    
    json_ld_config = seo_config.get("json_ld", {{}})
    enabled = []
    
    if json_ld_config.get("organization", True):
        enabled.append("organization")
    if json_ld_config.get("website", True):
        enabled.append("website")
    if json_ld_config.get("breadcrumbs", True):
        enabled.append("breadcrumbs")
    if json_ld_config.get("product", True):
        enabled.append("product")
    
    return enabled
'''
    
    seo_files["jsonld.py"] = jsonld_content
    
    # Sitemap utility
    sitemap_content = f'''"""
Sitemap generation utilities
"""

from datetime import datetime
from typing import List, Dict, Any

def generate_sitemap_xml(
    base_url: str = "https://example.com",
    pages: List[Dict[str, Any]] = None,
    include_images: bool = True
) -> str:
    """Generate sitemap.xml content"""
    
    if not pages:
        # Default pages
        pages = [
            {{"url": "/", "priority": "1.0", "changefreq": "daily"}},
            {{"url": "/Shop", "priority": "0.8", "changefreq": "weekly"}},
            {{"url": "/About", "priority": "0.6", "changefreq": "monthly"}},
            {{"url": "/Contact", "priority": "0.7", "changefreq": "monthly"}}
        ]
    
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
'''
    
    for page in pages:
        url = page.get("url", "/")
        if not url.startswith("http"):
            url = base_url.rstrip("/") + url
        
        priority = page.get("priority", "0.5")
        changefreq = page.get("changefreq", "monthly")
        lastmod = page.get("lastmod", datetime.now().strftime("%Y-%m-%d"))
        
        xml_content += f'''
    <url>
        <loc>{{url}}</loc>
        <lastmod>{{lastmod}}</lastmod>
        <changefreq>{{changefreq}}</changefreq>
        <priority>{{priority}}</priority>
    </url>'''
    
    xml_content += '''
</urlset>'''
    
    return xml_content

def generate_sitemap_index(sitemaps: List[str], base_url: str = "https://example.com") -> str:
    """Generate sitemap index file"""
    
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    
    for sitemap in sitemaps:
        if not sitemap.startswith("http"):
            sitemap = base_url.rstrip("/") + "/" + sitemap.lstrip("/")
        
        xml_content += f'''
    <sitemap>
        <loc>{{sitemap}}</loc>
        <lastmod>{{datetime.now().strftime("%Y-%m-%d")}}</lastmod>
    </sitemap>'''
    
    xml_content += '''
</sitemapindex>'''
    
    return xml_content

def get_page_urls_from_plan(plan: Dict[str, Any], base_url: str = "https://example.com") -> List[Dict[str, Any]]:
    """Extract page URLs from plan for sitemap generation"""
    
    pages = plan.get("pages", [])
    sitemap_pages = []
    
    for page in pages:
        slug = page.get("slug", "/")
        priority = "1.0" if slug == "/" else "0.8"
        changefreq = "daily" if slug == "/" else "weekly"
        
        sitemap_pages.append({{
            "url": slug,
            "priority": priority,
            "changefreq": changefreq,
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        }})
    
    return sitemap_pages
'''
    
    seo_files["sitemap.py"] = sitemap_content
    
    # Robots.txt utility
    robots_content = '''"""
Robots.txt generation utilities
"""

from typing import List, Dict, Any

def generate_robots_txt(
    allow_all: bool = True,
    disallow_paths: List[str] = None,
    sitemap_url: str = None,
    crawl_delay: int = None
) -> str:
    """Generate robots.txt content"""
    
    if disallow_paths is None:
        disallow_paths = ["/admin", "/api", "/_vsbvibe"]
    
    robots_content = "User-agent: *\\n"
    
    if allow_all:
        robots_content += "Allow: /\\n"
    
    # Add disallow paths
    for path in disallow_paths:
        robots_content += f"Disallow: {path}\\n"
    
    # Add crawl delay if specified
    if crawl_delay:
        robots_content += f"Crawl-delay: {crawl_delay}\\n"
    
    # Add sitemap URL
    if sitemap_url:
        robots_content += f"\\nSitemap: {sitemap_url}\\n"
    
    return robots_content

def generate_robots_for_development() -> str:
    """Generate robots.txt for development environment"""
    
    return """User-agent: *
Disallow: /

# Development environment - do not index
"""

def generate_robots_for_production(
    sitemap_url: str = "https://example.com/sitemap.xml"
) -> str:
    """Generate robots.txt for production environment"""
    
    return f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api
Disallow: /_vsbvibe

Crawl-delay: 1

Sitemap: {sitemap_url}
"""
'''
    
    seo_files["robots.py"] = robots_content
    
    # Meta tags utility
    meta_content = f'''"""
Meta tags and SEO utilities
"""

from typing import Dict, Any, List

def generate_meta_tags(
    title: str,
    description: str,
    keywords: List[str] = None,
    og_image: str = None,
    canonical_url: str = None,
    author: str = None
) -> str:
    """Generate HTML meta tags"""
    
    meta_html = f"""
    <title>{{title}}</title>
    <meta name="description" content="{{description}}">
    """
    
    if keywords:
        keywords_str = ", ".join(keywords)
        meta_html += f'<meta name="keywords" content="{{keywords_str}}">\\n    '
    
    if author:
        meta_html += f'<meta name="author" content="{{author}}">\\n    '
    
    if canonical_url:
        meta_html += f'<link rel="canonical" href="{{canonical_url}}">\\n    '
    
    # Open Graph tags
    meta_html += f"""
    <meta property="og:title" content="{{title}}">
    <meta property="og:description" content="{{description}}">
    <meta property="og:type" content="website">
    """
    
    if og_image:
        meta_html += f'<meta property="og:image" content="{{og_image}}">\\n    '
    
    # Twitter Card tags
    meta_html += f"""
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{{title}}">
    <meta name="twitter:description" content="{{description}}">
    """
    
    if og_image:
        meta_html += f'<meta name="twitter:image" content="{{og_image}}">\\n    '
    
    return meta_html.strip()

def build_page_title(
    page_title: str,
    site_name: str = "{project_config.get('project_name', 'Website')}",
    separator: str = " - "
) -> str:
    """Build complete page title"""
    
    if page_title.lower() == "home":
        return site_name
    
    return f"{{page_title}}{{separator}}{{site_name}}"

def generate_canonical_url(base_url: str, path: str) -> str:
    """Generate canonical URL"""
    
    base_url = base_url.rstrip("/")
    path = path.lstrip("/")
    
    if not path:
        return base_url
    
    return f"{{base_url}}/{{path}}"

def get_seo_defaults() -> Dict[str, Any]:
    """Get default SEO configuration"""
    
    return {{
        "title_template": "{project_config.get('project_name', 'Website')} - {{page_title}}",
        "meta_description": "Welcome to {project_config.get('company_name', 'our website')}. We provide professional services and solutions.",
        "keywords": ["website", "business", "services", "{project_config.get('company_name', 'company').lower()}"],
        "og_image": "/assets/og-image.jpg",
        "author": "{project_config.get('company_name', 'Website Owner')}",
        "robots": "index, follow",
        "viewport": "width=device-width, initial-scale=1.0"
    }}

def extract_meta_from_content(content: str) -> Dict[str, str]:
    """Extract meta information from content"""
    
    # Simple extraction - in a real implementation, this would be more sophisticated
    words = content.split()
    
    # Generate description from first 150 characters
    description = content[:150] + "..." if len(content) > 150 else content
    
    # Extract potential keywords (simplified)
    keywords = []
    for word in words:
        if len(word) > 4 and word.lower() not in ["this", "that", "with", "from", "they", "have", "been"]:
            keywords.append(word.lower())
    
    return {{
        "description": description,
        "keywords": list(set(keywords))[:10]  # Top 10 unique keywords
    }}
'''
    
    seo_files["meta.py"] = meta_content
    
    return seo_files