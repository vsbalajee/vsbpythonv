"""
Step 3 Interface - Generate Scaffold
"""

import streamlit as st
import os
import json
import openai
from datetime import datetime
from core.state import get_session_state
from core.telemetry import log_user_action

def render_step3_interface():
    # Lazy imports to avoid boot-time crashes
    from core.errors import safe_page, safe_component
    from modules.scaffold_generator import ScaffoldGenerator
    from modules.project_manager import ProjectManager
    from modules.project_manager import ProjectManager

    @safe_page
    def _render_step3():
        """Render Step 3 - Generate Scaffold"""
        
        st.header("⚙️ Step 3: Generate Scaffold")
        st.write("Generate production-ready site scaffold from your UI/UX plan.")
        
        # Progress indicator
        progress_cols = st.columns(10)
        for i in range(10):
            with progress_cols[i]:
                if i == 2:
                    st.markdown("🔵")  # Current step
                elif i < 2:
                    st.markdown("✅")  # Completed steps
                else:
                    st.markdown("⚪")  # Future steps
        
        st.markdown("---")
        
        # Preflight validation
        project_path = get_session_state("project_path")
        if not project_path:
            st.error("No project loaded. Please complete previous steps first.")
            return
        
        # Check preflight log
        preflight_path = os.path.join(project_path, "_vsbvibe", "logs", "preflight.log")
        
        if not os.path.exists(preflight_path):
            st.error("Preflight validation not passed. Run the validation prompt again before scaffold generation.")
            return
        
        try:
            with open(preflight_path, 'r') as f:
                preflight_content = f.read().strip()
            
            if "OK" not in preflight_content:
                st.error("Preflight validation not passed. Run the validation prompt again before scaffold generation.")
                return
        except:
            st.error("Could not read preflight validation. Please run validation again.")
            return
        
        st.success("✅ Preflight validation passed")
        
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
        
        # Display plan info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Platform:** {plan.get('platform_target', 'Unknown')}")
        
        with col2:
            st.info(f"**Site Mode:** {plan.get('site_mode', 'Unknown')}")
        
        with col3:
            st.info(f"**Pages:** {len(plan.get('pages', []))}")
        
        # Check for existing scaffold
        output_path = os.path.join(project_path, "output", plan.get('platform_target', 'streamlit_site'))
        scaffold_exists = os.path.exists(output_path)
        
        if scaffold_exists:
            st.success("✅ Scaffold already generated")
            
            # Show existing files
            with st.expander("View Generated Files", expanded=False):
                _display_generated_files(output_path, safe_component)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Regenerate Scaffold", type="secondary"):
                    _generate_scaffold_with_ai(project_path, plan, safe_component)
                    st.rerun()
            
            with col2:
                if st.button("Continue to Step 4", type="primary"):
                    st.session_state.current_step = 4
                    st.rerun()
        
        else:
            st.info("Ready to generate scaffold. This will create all necessary files for your website.")
            
            # Generation options
            with st.expander("Generation Options", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    include_seo = st.checkbox("Include SEO utilities", value=True)
                    include_analytics = st.checkbox("Include analytics", value=True)
                
                with col2:
                    include_admin = st.checkbox("Include admin panel", value=True)
                    include_tests = st.checkbox("Include test files", value=True)
                    use_ai_generation = st.checkbox("Use AI code generation", value=True)
            
            if st.button("Generate Scaffold", type="primary"):
                _generate_scaffold_with_ai(project_path, plan, safe_component, {
                    "include_seo": include_seo,
                    "include_analytics": include_analytics,
                    "include_admin": include_admin,
                    "include_tests": include_tests,
                    "use_ai_generation": use_ai_generation
                })
                st.rerun()

    def _display_generated_files(output_path: str, safe_component):
        """Display generated files in tree structure"""
        
        @safe_component
        def _show_files():
            files = []
            for root, dirs, filenames in os.walk(output_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, output_path)
                    file_size = os.path.getsize(file_path)
                    files.append({
                        "File": rel_path,
                        "Size": f"{file_size} bytes",
                        "Type": filename.split('.')[-1] if '.' in filename else "file"
                    })
            
            if files:
                import pandas as pd
                df = pd.DataFrame(files)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No files found in output directory")
        
        _show_files()

    def _generate_scaffold_with_ai(project_path: str, plan: dict, safe_component, options: dict = None):
        """Generate scaffold with AI assistance"""
        
        if options is None:
            options = {
                "include_seo": True,
                "include_analytics": True,
                "include_admin": True,
                "include_tests": True,
                "use_ai_generation": True
            }
        
        @safe_component
        def _do_generation():
            try:
                with st.spinner("Generating scaffold with AI assistance..."):
                    
                    # Load project config
                    project_manager = ProjectManager()
                    project_manager.current_project_path = project_path
                    project_config = project_manager.load_project_config()
                    
                    # AI-enhanced scaffold generation
                    if options.get("use_ai_generation", True):
                        enhanced_plan = _enhance_plan_with_ai(plan, project_config)
                        if enhanced_plan:
                            plan.update(enhanced_plan)
                    
                    # Create scaffold generator
                    generator = ScaffoldGenerator(project_config, plan, options)
                    
                    # Generate scaffold
                    result = generator.generate()
                    
                    if result["success"]:
                        st.success("✅ Scaffold generated successfully!")
                        
                        # Show summary
                        st.write("**Generated Files:**")
                        for file_path in result["files_created"]:
                            st.write(f"• {file_path}")
                        
                        # Update project status
                        project_config["status"] = "step3_complete"
                        project_config["updated_at"] = datetime.now().isoformat()
                        project_manager.save_project_config(project_config)
                        
                        log_user_action("scaffold_generated", {
                            "platform": plan.get("platform_target"),
                            "files_count": len(result["files_created"]),
                            "ai_enhanced": options.get("use_ai_generation", False)
                        })
                    
                    else:
                        st.error(f"Error generating scaffold: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                from core.errors import error_reporter
                error_id = error_reporter.capture_error(e, {
                    "module": "step3",
                    "function": "_generate_scaffold_with_ai",
                    "platform": plan.get("platform_target"),
                    "use_ai": options.get("use_ai_generation", False)
                })
                st.error(f"Error during scaffold generation: {str(e)} (Error ID: {error_id})")
        
        _do_generation()
    
    def _enhance_plan_with_ai(plan: dict, project_config: dict) -> dict:
        """Use AI to enhance the plan with custom code suggestions"""
        
        try:
            openai_key = st.secrets.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                return {}
            
            openai.api_key = openai_key
            model = st.secrets.get("openai_model", "gpt-4o-mini")
            
            enhancement_prompt = f"""
Based on this website plan, suggest code enhancements and custom components:

Project: {project_config.get('project_name', '')}
Company: {project_config.get('company_name', '')}
Site Mode: {plan.get('site_mode', '')}
Platform: {plan.get('platform_target', '')}
Pages: {json.dumps(plan.get('pages', []), indent=2)}

Provide JSON response with:
1. custom_components: array of component suggestions with name, purpose, code_hints
2. styling_enhancements: object with color_palette, typography, animations
3. functionality_additions: array of feature suggestions
4. code_optimizations: array of performance/structure improvements

Return only valid JSON.
"""
            
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a senior web developer. Suggest code enhancements for website scaffolds."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                temperature=0.4
            )
            
            enhancements = json.loads(response.choices[0].message.content)
            return {"ai_enhancements": enhancements}
            
        except Exception as e:
            st.warning(f"AI enhancement failed: {str(e)}. Using standard generation.")
            return {}
    