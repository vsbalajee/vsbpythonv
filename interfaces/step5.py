"""
Step 5 Interface - Data Import & Image Auto-Mapping
"""

import streamlit as st
import os
import pandas as pd
from datetime import datetime
from modules.project_manager import ProjectManager
from modules.data_importer import DataImporter
from core.state import get_session_state
from core.telemetry import log_user_action
from core.errors import safe_page, safe_component

@safe_page
def render_step5_interface():
    """Render Step 5 - Data Import & Image Auto-Mapping"""
    
    st.header("📊 Step 5: Data Import & Image Auto-Mapping")
    st.write("Import content from Excel templates with automatic image mapping and validation.")
    
    # Progress indicator
    progress_cols = st.columns(10)
    for i in range(10):
        with progress_cols[i]:
            if i == 4:
                st.markdown("🔵")  # Current step
            elif i < 4:
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
        st.error("Could not load plan.")
        return
    
    # Initialize data importer
    data_importer = DataImporter(project_manager)
    
    # Display import configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Platform:** {plan.get('platform_target', 'Unknown')}")
    
    with col2:
        st.info(f"**Site Mode:** {plan.get('site_mode', 'Unknown')}")
    
    with col3:
        products_enabled = plan.get("entities", {}).get("products", False)
        st.info(f"**Products:** {'Enabled' if products_enabled else 'Disabled'}")
    
    # File upload section
    st.subheader("📁 Upload Content Files")
    
    col1, col2 = st.columns(2)
    
    products_file = None
    pages_file = None
    
    with col1:
        if products_enabled:
            products_file = st.file_uploader(
                "Products Excel File",
                type=["xlsx"],
                help="Upload your completed products.xlsx template"
            )
        else:
            st.info("Products not enabled for this project")
    
    with col2:
        # Check if pages template was generated
        pages_template_path = os.path.join(project_path, "content", "pages.xlsx")
        if os.path.exists(pages_template_path):
            pages_file = st.file_uploader(
                "Pages Excel File",
                type=["xlsx"],
                help="Upload your completed pages.xlsx template"
            )
        else:
            st.info("No pages template found")
    
    # Images folder info
    st.subheader("🖼️ Image Auto-Mapping")
    
    images_path = os.path.join(project_path, "content", "images")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Image Folder:**")
        st.code(images_path)
        
        if os.path.exists(images_path):
            try:
                image_files = [f for f in os.listdir(images_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))]
                st.write(f"**Images Found:** {len(image_files)}")
                
                if image_files and st.checkbox("Show Image Files"):
                    for img in image_files[:10]:  # Show first 10
                        st.write(f"• {img}")
                    if len(image_files) > 10:
                        st.write(f"... and {len(image_files) - 10} more")
            except:
                st.warning("Could not read images folder")
        else:
            st.warning("Images folder not found")
    
    with col2:
        st.write("**Auto-Mapping Rules:**")
        st.write("• `slug.jpg` → Primary image")
        st.write("• `slug_main.jpg` → Primary (preferred)")
        st.write("• `slug_1.jpg`, `slug_2.jpg` → Extras")
        st.write("• `slug-1.jpg`, `slug-2.jpg` → Extras")
        st.write("• `https://...` → External URLs")
    
    # Import process
    st.subheader("🔍 Import Process")
    
    # Initialize session state for import
    if "import_results" not in st.session_state:
        st.session_state.import_results = None
    
    if "import_step" not in st.session_state:
        st.session_state.import_step = "upload"
    
    # Step 1: Dry Run
    if st.session_state.import_step == "upload":
        if products_file or pages_file:
            if st.button("🔍 Dry Run Validation", type="primary"):
                with st.spinner("Validating files and mapping images..."):
                    results = data_importer.dry_run_import(products_file, pages_file)
                    st.session_state.import_results = results
                    st.session_state.import_step = "preview"
                    st.rerun()
        else:
            st.info("Upload at least one Excel file to begin validation.")
    
    # Step 2: Preview Results
    elif st.session_state.import_step == "preview":
        results = st.session_state.import_results
        
        if results:
            _display_import_preview(results)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Run Again"):
                    st.session_state.import_step = "upload"
                    st.session_state.import_results = None
                    st.rerun()
            
            with col2:
                if results["summary"]["ready_to_apply"]:
                    if st.button("✅ Apply Import", type="primary"):
                        with st.spinner("Applying import..."):
                            apply_results = data_importer.apply_import(results)
                            st.session_state.apply_results = apply_results
                            st.session_state.import_step = "complete"
                            st.rerun()
                else:
                    st.error("Fix validation issues before applying")
            
            with col3:
                # Download issues CSV if available
                issues_path = os.path.join(project_path, "_vsbvibe", "issues.csv")
                if os.path.exists(issues_path):
                    with open(issues_path, 'rb') as f:
                        st.download_button(
                            "📥 Download Issues CSV",
                            data=f.read(),
                            file_name="issues.csv",
                            mime="text/csv"
                        )
    
    # Step 3: Import Complete
    elif st.session_state.import_step == "complete":
        apply_results = st.session_state.get("apply_results", {})
        
        if apply_results.get("success"):
            st.success("✅ Import completed successfully!")
            
            # Show summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Products Imported", apply_results.get("products_applied", 0))
            
            with col2:
                st.metric("Pages Imported", apply_results.get("pages_applied", 0))
            
            with col3:
                st.metric("Snapshot Created", "✅" if apply_results.get("snapshot_path") else "❌")
            
            # Undo option
            st.markdown("---")
            st.subheader("🔄 Undo Import")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("↩️ Undo Last Import"):
                    with st.spinner("Restoring previous content..."):
                        undo_results = data_importer.undo_last_import()
                        
                        if undo_results["success"]:
                            st.success("✅ Import undone successfully!")
                            st.session_state.import_step = "upload"
                            st.session_state.import_results = None
                            st.rerun()
                        else:
                            st.error(f"Undo failed: {undo_results['message']}")
            
            with col2:
                if st.button("Continue to Step 6", type="primary"):
                    st.session_state.current_step = 6
                    st.rerun()
        
        else:
            st.error(f"Import failed: {apply_results.get('message', 'Unknown error')}")
            
            if st.button("🔄 Try Again"):
                st.session_state.import_step = "upload"
                st.session_state.import_results = None
                st.rerun()

@safe_component
def _display_import_preview(results: Dict[str, Any]):
    """Display import preview with validation results"""
    
    st.subheader("📋 Import Preview")
    
    # Summary metrics
    summary = results["summary"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", summary["total_rows"])
    
    with col2:
        st.metric("Products", summary["products_count"])
    
    with col3:
        st.metric("Pages", summary["pages_count"])
    
    with col4:
        st.metric("Issues", summary["total_issues"])
    
    # Global issues
    if results["global_issues"]:
        st.error("**Global Issues:**")
        for issue in results["global_issues"]:
            st.write(f"• {issue}")
    
    # Products preview
    if results["products"]["rows"]:
        st.markdown("---")
        st.subheader("🛍️ Products Preview")
        
        # Products summary
        p_counts = results["products"]["counts"]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Valid", p_counts["valid"], delta=None)
        
        with col2:
            st.metric("Warnings", p_counts["warnings"], delta=None)
        
        with col3:
            st.metric("Errors", p_counts["errors"], delta=None)
        
        # Products table
        products_data = []
        for row in results["products"]["rows"]:
            products_data.append({
                "Status": row["status"],
                "Row": row["row"],
                "Slug": row["slug"],
                "Title": row["title"],
                "Price": f"${row.get('price', 0):.2f}" if isinstance(row.get('price'), (int, float)) else row.get('price', ''),
                "Main Image": row.get("image_main", "None"),
                "Extras": len(row.get("image_extras", [])),
                "Message": row["message"]
            })
        
        if products_data:
            df = pd.DataFrame(products_data)
            st.dataframe(df, use_container_width=True)
    
    # Pages preview
    if results["pages"]["rows"]:
        st.markdown("---")
        st.subheader("📄 Pages Preview")
        
        # Pages summary
        p_counts = results["pages"]["counts"]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Valid", p_counts["valid"], delta=None)
        
        with col2:
            st.metric("Warnings", p_counts["warnings"], delta=None)
        
        with col3:
            st.metric("Errors", p_counts["errors"], delta=None)
        
        # Pages table
        pages_data = []
        for row in results["pages"]["rows"]:
            pages_data.append({
                "Status": row["status"],
                "Row": row["row"],
                "Slug": row["slug"],
                "Title": row["title"],
                "Hero Image": row.get("hero_image", "None"),
                "Message": row["message"]
            })
        
        if pages_data:
            df = pd.DataFrame(pages_data)
            st.dataframe(df, use_container_width=True)
    
    # Status legend
    st.markdown("---")
    st.subheader("📊 Status Legend")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("✅ **Valid** - All fields OK, images found")
        st.write("🟠 **Fuzzy** - Probable image match, needs confirmation")
        st.write("🔴 **Missing** - Required field or main image missing")
    
    with col2:
        st.write("🟣 **Multiple** - Multiple main images found, choose one")
        st.write("🔵 **External** - Using external image URL")