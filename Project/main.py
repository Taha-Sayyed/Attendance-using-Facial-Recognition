"""
Main entry point for the SIES GST Attendance System
This file initializes the application and handles page routing
"""
import streamlit as st
import os
import sys

# Add the parent directory to sys.path to make imports work
sys.path.append(os.path.abspath('..'))

# Import configuration
from config import init_session_state, init_firebase, navigate

# Import page modules
from pages import main_page, register_page, login_page, home_page

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="SIES GST Attendance System",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # Initialize session state
    init_session_state()
    
    # Initialize Firebase
    db = init_firebase()
    
    # Check if Firebase initialized successfully
    if db:
        st.sidebar.success("Firebase connected successfully")
    else:
        st.sidebar.error("Failed to connect to Firebase")
    
    # Route to the appropriate page based on session state
    if st.session_state["page"] == "main":
        main_page.render()
    elif st.session_state["page"] == "Register":
        register_page.render(db)
    elif st.session_state["page"] == "Login":
        login_page.render(db)
    elif st.session_state["page"] == "home":
        home_page.render(db)
    else:
        st.error(f"Unknown page: {st.session_state['page']}")
        st.session_state["page"] = "main"
        st.rerun()

if __name__ == "__main__":
    main() 