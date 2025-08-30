"""
Scaffold generation utilities for Vsbvibe
Generates production-ready applications from UI/UX plans with platform awareness
"""

import json
import os
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from typing import Dict, Any, List, Optional
from .utils import ensure_directory, save_json
from core.errors import safe_component

def _build_sitemap_xml(urls, base_url):
    """Build sitemap XML safely without triple-quoted literals"""
    base = (base_url or "").rstrip("/")
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for path in urls or []:
        u = SubElement(urlset, "url")
        loc = SubElement(u, "loc")
        loc.text = f"{base}/{str(path).lstrip('/')}"
    xml = tostring(urlset, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml

def _build_robots_txt(base_url):
    """Build robots.txt safely"""
    base = (base_url or "").rstrip("/")
    lines = ["User-agent: *", "Allow: /"]
    if base:
        lines.append(f"Sitemap: {base}/sitemap.xml")
    return "\n".join(lines).strip() + "\n"

class ScaffoldGenerator:
    """Generate production-ready website scaffolds"""
    
    def __init__(self, project_config: Dict[str, Any], plan: Dict[str, Any], options: Dict[str, Any] = None):
        self.project_config = project_config
        self.plan = plan
        self.options = options or {}
        self.project_path = project_config.get("local_folder", "")
        self.project_name = project_config.get("project_name", "project").lower().replace(" ", "-")
    
    @safe_component
    def generate(self) -> Dict[str, Any]:
        """Generate complete scaffold"""
        
        try:
            platform_target = self.plan.get("platform_target", "react_vite")
            
            if platform_target == "react_vite":
                return self._generate_react_vite_scaffold()
            elif platform_target == "streamlit_site":
                return self._generate_streamlit_scaffold()
            elif platform_target == "htmljs":
                return self._generate_htmljs_scaffold()
            else:
                return {"success": False, "error": f"Unsupported platform: {platform_target}"}
                
        except Exception as e:
            from core.errors import error_reporter
            error_id = error_reporter.capture_error(e, {
                "module": "scaffold_generator",
                "function": "generate",
                "platform": self.plan.get("platform_target"),
                "project": self.project_config.get("project_name")
            })
            return {"success": False, "error": str(e), "error_id": error_id}
    
    @safe_component
    def _generate_streamlit_scaffold(self) -> Dict[str, Any]:
        """Generate Streamlit site scaffold"""
        
        output_path = os.path.join(self.project_path, self.project_name, "output", "streamlit_site")
        ensure_directory(output_path)
        
        files_created = []
        
        # Generate main app.py
        app_content = self._generate_streamlit_app()
        app_path = os.path.join(output_path, "app.py")
        with open(app_path, 'w') as f:
            f.write(app_content)
        files_created.append("app.py")
        
        # Generate pages
        pages_dir = os.path.join(output_path, "pages")
        ensure_directory(pages_dir)
        
        for i, page in enumerate(self.plan.get("pages", [])):
            page_content = self._generate_streamlit_page(page)
            page_filename = f"{i+1:02d}_{page.get('name', 'Page').replace(' ', '_')}.py"
            page_path = os.path.join(pages_dir, page_filename)
            with open(page_path, 'w') as f:
                f.write(page_content)
            files_created.append(f"pages/{page_filename}")
        
        # Generate components
        components_dir = os.path.join(output_path, "components")
        ensure_directory(components_dir)
        
        # Navigation component
        nav_content = self._generate_navigation_component()
        nav_path = os.path.join(components_dir, "nav.py")
        with open(nav_path, 'w') as f:
            f.write(nav_content)
        files_created.append("components/nav.py")
        
        # Generate SEO utilities if enabled
        if self.options.get("include_seo", True):
            seo_files = self._generate_seo_files(output_path)
            files_created.extend(seo_files)
        
        # Generate styles
        styles_dir = os.path.join(output_path, "styles")
        ensure_directory(styles_dir)
        
        tokens_content = json.dumps(self.plan.get("brand_tokens", {}), indent=2)
        tokens_path = os.path.join(styles_dir, "tokens.json")
        with open(tokens_path, 'w') as f:
            f.write(tokens_content)
        files_created.append("styles/tokens.json")
        
        return {
            "success": True,
            "files_created": files_created,
            "output_path": output_path
        }
    
    @safe_component
    def _generate_streamlit_app(self) -> str:
        """Generate main Streamlit app.py"""
        
        company_name = self.project_config.get("company_name", "Your Company")
        
        return f'''"""
{company_name} Website
Generated by Vsbvibe
"""

import streamlit as st
from components.nav import render_navigation

def main():
    st.set_page_config(
        page_title="{company_name}",
        page_icon="🚀",
        layout="wide"
    )
    
    render_navigation()
    
    st.title("Welcome to {company_name}")
    st.write("Your website is ready!")

if __name__ == "__main__":
    main()
'''
    
    @safe_component
    def _generate_streamlit_page(self, page: Dict[str, Any]) -> str:
        """Generate individual Streamlit page"""
        
        page_name = page.get("name", "Page")
        page_type = page.get("type", "basic")
        
        return f'''"""
{page_name} Page
Generated by Vsbvibe
"""

import streamlit as st

def main():
    st.title("{page_name}")
    
    # Page content based on type: {page_type}
    st.write("Content for {page_name.lower()} page will be generated here.")
    
    # Sections: {', '.join(page.get('sections', []))}

if __name__ == "__main__":
    main()
'''
    
    @safe_component
    def _generate_navigation_component(self) -> str:
        """Generate navigation component"""
        
        nav_items = self.plan.get("navigation", {}).get("header", [])
        
        return f'''"""
Navigation Component
Generated by Vsbvibe
"""

import streamlit as st

def render_navigation():
    """Render site navigation"""
    
    with st.container():
        cols = st.columns(len({nav_items}) + 1)
        
        with cols[0]:
            st.markdown("**{self.project_config.get('company_name', 'Company')}**")
        
        # Navigation items: {nav_items}
        for i, item in enumerate({nav_items}, 1):
            with cols[i]:
                st.markdown(f"[{{item.get('name', 'Link')}}]({{item.get('url', '/')}})")
'''
    
    @safe_component
    def _generate_seo_files(self, output_path: str) -> List[str]:
        """Generate SEO files using safe builders"""
        
        files_created = []
        
        # Create public directory
        public_dir = os.path.join(output_path, "_public")
        ensure_directory(public_dir)
        
        # Generate sitemap.xml
        pages = self.plan.get("pages", [])
        routes = [page.get("slug", "/") for page in pages]
        base_url = self.project_config.get("base_url", "")
        
        # Safe generation (no triple-quoted literals)
        xml_content = _build_sitemap_xml(routes, base_url)
        robots_txt = _build_robots_txt(base_url)
        
        sitemap_path = os.path.join(public_dir, "sitemap.xml")
        robots_path = os.path.join(public_dir, "robots.txt")
        
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        files_created.append("_public/sitemap.xml")
        
        with open(robots_path, "w", encoding="utf-8") as f:
            f.write(robots_txt)
        files_created.append("_public/robots.txt")
        
        return files_created
    
    @safe_component
    def _generate_react_vite_scaffold(self) -> Dict[str, Any]:
        """Generate React + Vite scaffold"""
        
        output_path = os.path.join(self.project_path, self.project_name, "output", "react_vite")
        ensure_directory(output_path)
        
        files_created = []
        
        # Generate package.json
        package_json = self._generate_package_json()
        package_path = os.path.join(output_path, "package.json")
        with open(package_path, 'w') as f:
            f.write(package_json)
        files_created.append("package.json")
        
        # Generate vite.config.js
        vite_config = self._generate_vite_config()
        vite_path = os.path.join(output_path, "vite.config.js")
        with open(vite_path, 'w') as f:
            f.write(vite_config)
        files_created.append("vite.config.js")
        
        # Generate index.html
        html_content = self._generate_react_index_html()
        html_path = os.path.join(output_path, "index.html")
        with open(html_path, 'w') as f:
            f.write(html_content)
        files_created.append("index.html")
        
        # Generate src directory
        src_dir = os.path.join(output_path, "src")
        ensure_directory(src_dir)
        
        # Generate App.jsx
        app_content = self._generate_react_app()
        app_path = os.path.join(src_dir, "App.jsx")
        with open(app_path, 'w') as f:
            f.write(app_content)
        files_created.append("src/App.jsx")
        
        # Generate main.jsx
        main_content = self._generate_react_main()
        main_path = os.path.join(src_dir, "main.jsx")
        with open(main_path, 'w') as f:
            f.write(main_content)
        files_created.append("src/main.jsx")
        
        # Generate CSS
        css_content = self._generate_react_css()
        css_path = os.path.join(src_dir, "App.css")
        with open(css_path, 'w') as f:
            f.write(css_content)
        files_created.append("src/App.css")
        
        # Generate components
        components_dir = os.path.join(src_dir, "components")
        ensure_directory(components_dir)
        
        # Navigation component
        nav_content = self._generate_react_navigation()
        nav_path = os.path.join(components_dir, "Navigation.jsx")
        with open(nav_path, 'w') as f:
            f.write(nav_content)
        files_created.append("src/components/Navigation.jsx")
        
        # Generate pages
        pages_dir = os.path.join(src_dir, "pages")
        ensure_directory(pages_dir)
        
        for page in self.plan.get("pages", []):
            page_content = self._generate_react_page(page)
            page_filename = f"{page.get('name', 'Page').replace(' ', '')}.jsx"
            page_path = os.path.join(pages_dir, page_filename)
            with open(page_path, 'w') as f:
                f.write(page_content)
            files_created.append(f"src/pages/{page_filename}")
        
        # Generate SEO files if enabled
        if self.options.get("include_seo", True):
            public_dir = os.path.join(output_path, "public")
            ensure_directory(public_dir)
            seo_files = self._generate_seo_files(output_path)
            files_created.extend(seo_files)
        
        return {
            "success": True,
            "files_created": files_created,
            "output_path": output_path
        }
    
    @safe_component
    def _generate_package_json(self) -> str:
        """Generate package.json for React + Vite"""
        
        company_name = self.project_config.get("company_name", "Your Company")
        project_name = self.project_config.get("project_name", "website").lower().replace(" ", "-")
        
        package_data = {
            "name": project_name,
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.43",
                "@types/react-dom": "^18.2.17",
                "@vitejs/plugin-react": "^4.2.1",
                "eslint": "^8.55.0",
                "eslint-plugin-react": "^7.33.2",
                "eslint-plugin-react-hooks": "^4.6.0",
                "eslint-plugin-react-refresh": "^0.4.5",
                "vite": "^5.0.8"
            }
        }
        
        return json.dumps(package_data, indent=2)
    
    @safe_component
    def _generate_vite_config(self) -> str:
        """Generate vite.config.js"""
        
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
"""
    
    @safe_component
    def _generate_react_index_html(self) -> str:
        """Generate index.html for React app"""
        
        company_name = self.project_config.get("company_name", "Your Company")
        
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{company_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
    
    @safe_component
    def _generate_react_main(self) -> str:
        """Generate main.jsx entry point"""
        
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './App.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
"""
    
    @safe_component
    def _generate_react_app(self) -> str:
        """Generate main App.jsx component"""
        
        company_name = self.project_config.get("company_name", "Your Company")
        pages = self.plan.get("pages", [])
        
        # Generate imports for pages
        page_imports = []
        routes = []
        
        for page in pages:
            page_name = page.get('name', 'Page').replace(' ', '')
            page_imports.append(f"import {page_name} from './pages/{page_name}'")
            
            slug = page.get('slug', '/')
            if slug == '/':
                routes.append(f'        <Route path="/" element={{{page_name} /}} />')
            else:
                routes.append(f'        <Route path="{slug}" element={{{page_name} /}} />')
        
        imports_str = '\n'.join(page_imports)
        routes_str = '\n'.join(routes)
        
    @safe_component
    def _generate_htmljs_scaffold(self) -> Dict[str, Any]:
        """Generate HTML/JS static site scaffold"""
        
        output_path = os.path.join(self.project_path, self.project_name, "output", "htmljs")
        ensure_directory(output_path)
        
        files_created = []
        
        # Generate index.html
        html_content = self._generate_html_index()
        html_path = os.path.join(output_path, "index.html")
        with open(html_path, 'w') as f:
            f.write(html_content)
        files_created.append("index.html")
        
        # Generate CSS
        css_dir = os.path.join(output_path, "css")
        ensure_directory(css_dir)
        
        css_content = self._generate_main_css()
        css_path = os.path.join(css_dir, "main.css")
        with open(css_path, 'w') as f:
            f.write(css_content)
        files_created.append("css/main.css")
        
        # Generate JavaScript
        js_dir = os.path.join(output_path, "js")
        ensure_directory(js_dir)
        
        js_content = self._generate_main_js()
        js_path = os.path.join(js_dir, "main.js")
        with open(js_path, 'w') as f:
            f.write(js_content)
        files_created.append("js/main.js")
        
        return {
            "success": True,
            "files_created": files_created,
            "output_path": output_path
        }
    
    @safe_component
    def _generate_html_index(self) -> str:
        """Generate HTML index page"""
        
        company_name = self.project_config.get("company_name", "Your Company")
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name}</title>
    <link rel="stylesheet" href="css/main.css">
</head>
<body>
    <header>
        <nav>
            <h1>{company_name}</h1>
        </nav>
    </header>
    
    <main>
        <section class="hero">
            <h2>Welcome to {company_name}</h2>
            <p>Your website is ready!</p>
        </section>
    </main>
    
    <script src="js/main.js"></script>
</body>
</html>'''
    
    @safe_component
    def _generate_main_css(self) -> str:
        """Generate main CSS file"""
        
        brand_tokens = self.plan.get("brand_tokens", {})
        primary_color = brand_tokens.get("primary_color", "#2563eb")
        font_family = brand_tokens.get("font_family", "Inter, sans-serif")
        
        return f'''/* Generated by Vsbvibe */

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: {font_family};
    line-height: 1.6;
    color: #333;
}}

header {{
    background: {primary_color};
    color: white;
    padding: 1rem 0;
}}

nav {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}}

.hero {{
    text-align: center;
    padding: 4rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
}}

.hero h2 {{
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: {primary_color};
}}
'''
    
    @safe_component
    def _generate_main_js(self) -> str:
        """Generate main JavaScript file"""
        
        return '''// Generated by Vsbvibe

document.addEventListener('DOMContentLoaded', function() {
    console.log('Website loaded successfully!');
    
    // Add any interactive functionality here
});
'''