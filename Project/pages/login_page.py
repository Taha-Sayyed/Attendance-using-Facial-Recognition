"""
Login page module for the SIES GST Attendance System
Contains the login form UI and functionality
"""
import streamlit as st
from ..config import navigate, API_KEY
from ..auth import login_user, get_user_details

def render(db):
    """
    Render the login page
    
    Args:
        db: Firestore database instance
    """
    st.title("Welcome to Login Page")
    st.button("Back to main page", on_click=lambda: navigate("main"))
    
    # If user is already logged in, redirect to home
    if st.session_state["user"]:
        st.session_state["page"] = "home"
        st.rerun()
    else:
        # Function to handle login
        def handle_login():
            email = st.session_state.get("login_email", "")
            password = st.session_state.get("login_password", "")
            if email and password:
                result = login_user(email, password, API_KEY)
                if "idToken" in result:
                    # Get the user ID (localId) to retrieve full user details
                    user_id = result.get("localId", "")
                    user_data = {"email": email, "idToken": result["idToken"]}
                    
                    # Retrieve complete user details from Firestore if ID is available
                    if user_id:
                        try:
                            user_info = get_user_details(user_id, db)
                            if user_info:
                                user_data.update(user_info)
                        except Exception as e:
                            st.error(f"Error retrieving user data: {e}")
                    
                    st.session_state["user"] = user_data
                    st.session_state["page"] = "home"  # Navigate to home page after login
                    st.session_state["show_balloons"] = True  # Flag to show balloons
                    st.rerun()
                else:
                    st.error("❌ Login Failed: " + result.get("error", {}).get("message", "Unknown error"))
        
        # Create a form to handle Enter key submission correctly
        with st.form(key="login_form"):
            email = st.text_input("Enter Email", key="login_email")
            password = st.text_input("Enter Password", type="password", key="login_password")
            submit_button = st.form_submit_button(label="Login")
            
            # Form submission handler
            if submit_button:
                handle_login() 