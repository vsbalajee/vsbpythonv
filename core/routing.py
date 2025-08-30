"""
Routing and navigation logic for Vsbvibe application
"""

import streamlit as st
from typing import Dict, Any

def handle_routing():
    """Main routing handler for the application"""
    
    # Initialize page state
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    
    # Sidebar navigation
    render_sidebar_navigation()
    
    # Main content routing
    current_step = st.session_state.current_step
    
    if current_step == 1:
        render_step1()
    elif current_step == 2:
        render_step2()
    elif current_step == 3:
        render_step3()
    elif current_step == 4:
        render_step4()
    elif current_step == 5:
        render_step5()
    elif current_step == 6:
        render_step6()
    elif current_step == 7:
        render_step7()
    elif current_step == 8:
        render_step8()
    elif current_step == 9:
        render_step9()
    elif current_step == 10:
        render_step10()
    else:
        render_admin_interface()

def render_sidebar_navigation():
    """Render sidebar navigation"""
    
    st.sidebar.title("🚀 Vsbvibe")
    st.sidebar.markdown("*Website Builder & Generator*")
    st.sidebar.markdown("---")
    
    # Step navigation
    steps = [
        "1️⃣ Project Setup",
        "2️⃣ Analysis & Plan", 
        "3️⃣ Generate Scaffold",
        "4️⃣ Content Import",
        "5️⃣ Data & Products",
        "6️⃣ AI Content",
        "7️⃣ Design & Style",
        "8️⃣ SEO & Performance",
        "9️⃣ Test & Preview",
        "🔟 Deploy & Publish"
    ]
    
    current_step = st.session_state.get("current_step", 1)
    
    for i, step in enumerate(steps, 1):
        if st.sidebar.button(step, key=f"step_{i}"):
            st.session_state.current_step = i
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Admin interface
    if st.sidebar.button("🛠️ Admin Interface"):
        st.session_state.current_step = "admin"
        st.rerun()
    
    # Help section
    with st.sidebar.expander("ℹ️ Help"):
        st.write("""
        **Vsbvibe Workflow:**
        1. Set up project basics
        2. Analyze requirements 
        3. Generate site scaffold
        4. Import content
        5. Add products/data
        6. Generate AI content
        7. Customize design
        8. Optimize SEO
        9. Test everything
        10. Deploy live
        11. Netlify Deployment
        12. Digital Ocean Deployment
        """)

def render_step1():
    """Render Step 1 - Project Setup"""
    from interfaces.step1 import render_step1_interface
    render_step1_interface()

def render_step2():
    """Render Step 2 - Analysis & Plan"""
    from interfaces.step2 import render_step2_interface
    render_step2_interface()

def render_step3():
    """Render Step 3 - Generate Scaffold"""
    from interfaces.step3 import render_step3_interface
    render_step3_interface()

def render_step4():
    """Render Step 4 - Content Import"""
    from interfaces.step4 import render_step4_interface
    render_step4_interface()

def render_step5():
    """Render Step 5 - Data & Products"""
    from interfaces.step5 import render_step5_interface
    render_step5_interface()

def render_step6():
    """Render Step 6 - AI Content"""
    st.header("🤖 Step 6: AI Content Generation")
    st.info("Step 6 implementation coming soon...")

def render_step7():
    """Render Step 7 - Design & Style"""
    st.header("🎨 Step 7: Design & Style")
    st.info("Step 7 implementation coming soon...")

def render_step8():
    """Render Step 8 - SEO & Performance"""
    st.header("🔍 Step 8: SEO & Performance")
    st.info("Step 8 implementation coming soon...")

def render_step9():
    """Render Step 9 - Test & Preview"""
    st.header("🧪 Step 9: Test & Preview")
    st.info("Step 9 implementation coming soon...")

def render_step10():
    """Render Step 10 - Deploy & Publish"""
    st.header("🚀 Step 10: Deploy & Publish")
    st.info("Step 10 implementation coming soon...")

def render_admin_interface():
    """Render Admin Interface"""
    from modules.admin_interface import render_admin_interface as _render_admin
    _render_admin()