"""
Step 2 Interface - Reference Analysis & UI/UX Plan
"""

import streamlit as st
import os
import json
from datetime import datetime
from modules.project_manager import ProjectManager
from core.state import get_session_state, update_session_state
from core.telemetry import log_user_action

def render_step2_interface():
    """Render Step 2 - Reference Analysis & UI/UX Plan"""
    
    st.header("🔍 Step 2: Reference Analysis & UI/UX Plan")
    st.write("Analyze requirements and generate a comprehensive UI/UX plan.")
    
    # Progress indicator
    progress_cols = st.columns(10)
    for i in range(10):
        with progress_cols[i]:
            if i == 1:
                st.markdown("🔵")  # Current step
            elif i == 0:
                st.markdown("✅")  # Completed step
            else:
                st.markdown("⚪")  # Future steps
    
    st.markdown("---")
    
    # Check if project is loaded
    project_path = get_session_state("project_path")
    if not project_path:
        st.error("No project loaded. Please complete Step 1 first.")
        return
    
    # Load project configuration
    project_manager = ProjectManager()
    project_manager.current_project_path = project_path
    project_config = project_manager.load_project_config()
    
    if not project_config:
        st.error("Could not load project configuration.")
        return
    
    # Display project info
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Project:** {project_config.get('project_name', 'Unknown')}")
        st.info(f"**Company:** {project_config.get('company_name', 'Unknown')}")
    
    with col2:
        st.info(f"**Content Mode:** {project_config.get('content_mode', 'Unknown')}")
        st.info(f"**Status:** {project_config.get('status', 'Unknown')}")
    
    # Check for existing plan
    plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
    existing_plan = None
    
    if os.path.exists(plan_path):
        try:
            with open(plan_path, 'r') as f:
                existing_plan = json.load(f)
        except:
            pass
    
    # Analysis section
    st.subheader("📋 Requirements Analysis")
    
    requirements = project_config.get("requirements", "")
    if requirements:
        with st.expander("View Requirements", expanded=False):
            st.text_area("Requirements", value=requirements, height=150, disabled=True)
    
    # Reference analysis
    reference_url = project_config.get("reference_url", "")
    screenshots = project_config.get("screenshots", [])
    
    if reference_url or screenshots:
        st.subheader("🔗 Reference Analysis")
        
        if reference_url:
            st.write(f"**Reference URL:** {reference_url}")
        
        if screenshots:
            st.write(f"**Screenshots:** {len(screenshots)} files uploaded")
            
            # Show screenshot thumbnails
            if st.checkbox("Show Screenshots"):
                cols = st.columns(min(len(screenshots), 3))
                for i, screenshot in enumerate(screenshots):
                    with cols[i % 3]:
                        screenshot_path = os.path.join(project_path, screenshot)
                        if os.path.exists(screenshot_path):
                            st.image(screenshot_path, caption=f"Screenshot {i+1}")
    
    # Plan generation
    st.subheader("🎯 UI/UX Plan Generation")
    
    if existing_plan:
        st.success("✅ Plan already exists")
        
        # Show plan summary
        with st.expander("View Current Plan", expanded=True):
            _display_plan_summary(existing_plan)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Regenerate Plan", type="secondary"):
                _generate_plan(project_manager, project_config)
                st.rerun()
        
        with col2:
            if st.button("Continue to Step 3", type="primary"):
                st.session_state.current_step = 3
                st.rerun()
    
    else:
        st.info("No plan generated yet. Click below to analyze requirements and create UI/UX plan.")
        
        if st.button("Generate Plan", type="primary"):
            _generate_plan(project_manager, project_config)
            st.rerun()

def _display_plan_summary(plan: dict):
    """Display plan summary"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Platform & Mode:**")
        st.write(f"• Platform: {plan.get('platform_target', 'Unknown')}")
        st.write(f"• Site Mode: {plan.get('site_mode', 'Unknown')}")
        
        st.write("**Pages:**")
        pages = plan.get("pages", [])
        for page in pages:
            st.write(f"• {page.get('name', 'Unknown')} ({page.get('slug', '/')})")
    
    with col2:
        st.write("**Brand Tokens:**")
        brand_tokens = plan.get("brand_tokens", {})
        st.write(f"• Primary Color: {brand_tokens.get('primary_color', '#007bff')}")
        st.write(f"• Font Family: {brand_tokens.get('font_family', 'Inter')}")
        
        st.write("**Features:**")
        entities = plan.get("entities", {})
        if entities.get("products"):
            st.write("• E-commerce enabled")
        if entities.get("blog"):
            st.write("• Blog enabled")
        if entities.get("contact"):
            st.write("• Contact forms enabled")

def _generate_plan(project_manager: ProjectManager, project_config: dict):
    """Generate UI/UX plan from requirements"""
    
    try:
        with st.spinner("Analyzing requirements and generating plan..."):
            
            # Analyze requirements
            requirements = project_config.get("requirements", "")
            content_mode = project_config.get("content_mode", "AI Generated")
            
            # Detect site characteristics
            site_analysis = _analyze_requirements(requirements)
            
            # Generate plan
            plan = {
                "platform_target": "streamlit_site",  # Default for this implementation
                "site_mode": site_analysis["site_mode"],
                "pages": _generate_pages(site_analysis),
                "navigation": _generate_navigation(site_analysis),
                "brand_tokens": _generate_brand_tokens(site_analysis, project_config),
                "entities": site_analysis["entities"],
                "ui_ux_plan": {
                    "layout": site_analysis["layout_style"],
                    "color_scheme": site_analysis["color_scheme"],
                    "target_audience": site_analysis["target_audience"],
                    "features": site_analysis["features"]
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Generate SEO defaults
            seo_defaults = _generate_seo_defaults(project_config, plan)
            
            # Generate analysis report
            analysis_report = _generate_analysis_report(project_config, site_analysis, plan)
            
            # Save files
            project_path = project_manager.get_current_project_path()
            
            # Save plan
            plan_path = os.path.join(project_path, "_vsbvibe", "plan.json")
            with open(plan_path, 'w') as f:
                json.dump(plan, f, indent=2)
            
            # Save SEO defaults
            seo_path = os.path.join(project_path, "_vsbvibe", "seo_defaults.json")
            with open(seo_path, 'w') as f:
                json.dump(seo_defaults, f, indent=2)
            
            # Save analysis report
            report_path = os.path.join(project_path, "_vsbvibe", "analysis_report.json")
            with open(report_path, 'w') as f:
                json.dump(analysis_report, f, indent=2)
            
            # Create diff summary
            diff_summary = {
                "timestamp": datetime.now().isoformat(),
                "operation": "plan_generation",
                "files_created": ["_vsbvibe/plan.json", "_vsbvibe/seo_defaults.json", "_vsbvibe/analysis_report.json"],
                "files_updated": [],
                "summary": "Generated UI/UX plan, SEO defaults, and analysis report"
            }
            
            diff_path = os.path.join(project_path, "_vsbvibe", "diff_summary.json")
            with open(diff_path, 'w') as f:
                json.dump(diff_summary, f, indent=2)
            
            # Update project status
            project_config["status"] = "step2_complete"
            project_config["updated_at"] = datetime.now().isoformat()
            project_manager.save_project_config(project_config)
            
            log_user_action("plan_generated", {"site_mode": site_analysis["site_mode"]})
            
            st.success("✅ Plan generated successfully!")
            
    except Exception as e:
        st.error(f"Error generating plan: {str(e)}")

def _analyze_requirements(requirements: str) -> dict:
    """Analyze requirements text to determine site characteristics"""
    
    req_lower = requirements.lower()
    
    # Detect site mode
    ecommerce_keywords = ["shop", "store", "product", "buy", "sell", "cart", "checkout", "payment", "ecommerce", "e-commerce"]
    is_ecommerce = any(keyword in req_lower for keyword in ecommerce_keywords)
    
    site_mode = "ecommerce" if is_ecommerce else "brochure"
    
    # Detect features
    features = []
    if any(word in req_lower for word in ["blog", "news", "article"]):
        features.append("blog")
    if any(word in req_lower for word in ["contact", "form", "inquiry"]):
        features.append("contact")
    if any(word in req_lower for word in ["search", "find", "filter"]):
        features.append("search")
    if any(word in req_lower for word in ["gallery", "portfolio", "showcase"]):
        features.append("gallery")
    if any(word in req_lower for word in ["testimonial", "review", "feedback"]):
        features.append("testimonials")
    
    # Detect target audience
    b2b_keywords = ["business", "enterprise", "corporate", "professional", "b2b"]
    b2c_keywords = ["consumer", "customer", "personal", "individual", "b2c"]
    
    if any(keyword in req_lower for keyword in b2b_keywords):
        target_audience = "business"
    elif any(keyword in req_lower for keyword in b2c_keywords):
        target_audience = "consumer"
    else:
        target_audience = "general"
    
    # Detect layout style
    modern_keywords = ["modern", "clean", "minimal", "sleek"]
    classic_keywords = ["traditional", "classic", "formal", "conservative"]
    creative_keywords = ["creative", "artistic", "unique", "bold"]
    
    if any(keyword in req_lower for keyword in modern_keywords):
        layout_style = "modern"
    elif any(keyword in req_lower for keyword in classic_keywords):
        layout_style = "classic"
    elif any(keyword in req_lower for keyword in creative_keywords):
        layout_style = "creative"
    else:
        layout_style = "modern"  # Default
    
    # Detect color scheme preference
    if any(word in req_lower for word in ["professional", "corporate", "business"]):
        color_scheme = "professional"
    elif any(word in req_lower for word in ["vibrant", "colorful", "bright"]):
        color_scheme = "vibrant"
    elif any(word in req_lower for word in ["minimal", "clean", "simple"]):
        color_scheme = "minimal"
    else:
        color_scheme = "professional"  # Default
    
    # Determine entities
    entities = {
        "products": is_ecommerce,
        "blog": "blog" in features,
        "contact": "contact" in features,
        "gallery": "gallery" in features,
        "testimonials": "testimonials" in features
    }
    
    return {
        "site_mode": site_mode,
        "features": features,
        "target_audience": target_audience,
        "layout_style": layout_style,
        "color_scheme": color_scheme,
        "entities": entities
    }

def _generate_pages(analysis: dict) -> list:
    """Generate pages based on analysis"""
    
    pages = [
        {
            "name": "Home",
            "slug": "/",
            "type": "home",
            "priority": 1,
            "sections": ["hero", "features", "cta"]
        }
    ]
    
    # Add e-commerce pages if needed
    if analysis["site_mode"] == "ecommerce":
        pages.extend([
            {
                "name": "Shop",
                "slug": "/shop",
                "type": "product_list",
                "priority": 2,
                "sections": ["header", "filters", "product_grid", "pagination"]
            },
            {
                "name": "Product",
                "slug": "/product/[id]",
                "type": "product_detail",
                "priority": 3,
                "sections": ["breadcrumb", "product_info", "gallery", "details", "related"]
            }
        ])
    
    # Add feature-based pages
    if "blog" in analysis["features"]:
        pages.append({
            "name": "Blog",
            "slug": "/blog",
            "type": "blog",
            "priority": 4,
            "sections": ["header", "post_list", "sidebar"]
        })
    
    if "contact" in analysis["features"]:
        pages.append({
            "name": "Contact",
            "slug": "/contact",
            "type": "contact",
            "priority": 5,
            "sections": ["header", "contact_form", "info", "map"]
        })
    
    # Add about page for brochure sites
    if analysis["site_mode"] == "brochure":
        pages.append({
            "name": "About",
            "slug": "/about",
            "type": "about",
            "priority": 2,
            "sections": ["header", "story", "team", "values"]
        })
    
    return pages

def _generate_navigation(analysis: dict) -> dict:
    """Generate navigation structure"""
    
    header_items = [
        {"name": "Home", "url": "/", "type": "internal"}
    ]
    
    if analysis["site_mode"] == "ecommerce":
        header_items.append({"name": "Shop", "url": "/shop", "type": "internal"})
    
    if analysis["site_mode"] == "brochure":
        header_items.append({"name": "About", "url": "/about", "type": "internal"})
    
    if "blog" in analysis["features"]:
        header_items.append({"name": "Blog", "url": "/blog", "type": "internal"})
    
    if "contact" in analysis["features"]:
        header_items.append({"name": "Contact", "url": "/contact", "type": "internal"})
    
    footer_items = [
        {"name": "Privacy Policy", "url": "/privacy", "type": "internal"},
        {"name": "Terms of Service", "url": "/terms", "type": "internal"}
    ]
    
    return {
        "header": header_items,
        "footer": footer_items,
        "mobile_menu": True,
        "search": "search" in analysis["features"]
    }

def _generate_brand_tokens(analysis: dict, project_config: dict) -> dict:
    """Generate brand tokens based on analysis"""
    
    # Color schemes
    color_schemes = {
        "professional": {"primary": "#2563eb", "secondary": "#64748b"},
        "vibrant": {"primary": "#dc2626", "secondary": "#f59e0b"},
        "minimal": {"primary": "#374151", "secondary": "#9ca3af"}
    }
    
    colors = color_schemes.get(analysis["color_scheme"], color_schemes["professional"])
    
    # Font families
    font_families = {
        "modern": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        "classic": "Georgia, Times, serif",
        "creative": "Poppins, -apple-system, BlinkMacSystemFont, sans-serif"
    }
    
    font_family = font_families.get(analysis["layout_style"], font_families["modern"])
    
    return {
        "primary_color": colors["primary"],
        "secondary_color": colors["secondary"],
        "accent_color": "#10b981",
        "font_family": font_family,
        "border_radius": "8px",
        "spacing_unit": "1rem",
        "created_at": datetime.now().isoformat()
    }

def _generate_seo_defaults(project_config: dict, plan: dict) -> dict:
    """Generate SEO defaults configuration"""
    
    return {
        "json_ld": {
            "organization": True,
            "website": True,
            "breadcrumbs": True,
            "product": plan.get("site_mode") == "ecommerce"
        },
        "meta_defaults": {
            "title_template": f"{project_config.get('company_name', 'Company')} - {{page_title}}",
            "meta_description": f"Welcome to {project_config.get('company_name', 'our website')}",
            "keywords": ["website", "business", project_config.get('company_name', 'company').lower()],
            "og_image": "/assets/og-image.jpg",
            "favicon": "/assets/favicon.ico"
        },
        "technical_seo": {
            "sitemap": True,
            "robots": True,
            "canonical": True,
            "structured_data": True
        },
        "performance": {
            "lazy_loading": True,
            "image_optimization": True,
            "preconnect_hints": True,
            "code_splitting": True
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def _generate_analysis_report(project_config: dict, analysis: dict, plan: dict) -> dict:
    """Generate analysis report"""
    
    # Get requirements version
    requirements_version = 1
    versions_path = os.path.join(
        project_config.get("local_folder", ""),
        project_config.get("project_name", "").lower().replace(" ", "-"),
        "_vsbvibe", "requirements_versions.json"
    )
    
    if os.path.exists(versions_path):
        try:
            with open(versions_path, 'r') as f:
                versions = json.load(f)
                requirements_version = len(versions) + 1
        except:
            pass
    
    return {
        "requirements_version": requirements_version,
        "analysis_timestamp": datetime.now().isoformat(),
        "rationale": {
            "site_mode_reasoning": f"Detected '{analysis['site_mode']}' based on keywords in requirements",
            "platform_selection": "streamlit_site chosen for rapid development and deployment",
            "features_detected": analysis["features"],
            "target_audience": analysis["target_audience"],
            "design_decisions": {
                "layout_style": analysis["layout_style"],
                "color_scheme": analysis["color_scheme"],
                "reasoning": "Based on industry keywords and target audience analysis"
            }
        },
        "plan_summary": {
            "total_pages": len(plan.get("pages", [])),
            "navigation_items": len(plan.get("navigation", {}).get("header", [])),
            "entities_enabled": list(k for k, v in analysis["entities"].items() if v)
        },
        "next_steps": [
            "Generate scaffold based on plan",
            "Import content and data",
            "Customize design and styling",
            "Test and deploy"
        ]
    }