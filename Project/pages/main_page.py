"""
Main page module for the SIES GST Attendance System
Contains the landing page UI and functionality
"""
import streamlit as st
from ..config import navigate

def render():
    """Render the main landing page"""
    # Create a layout with columns
    col1, col2 = st.columns([1, 2])
    
    # Display logo in the first column
    with col1:
        st.image("SIESLOGO.PNG", width=200)
    
    # Display title in the second column
    with col2:
        st.title("SIES GST Attendance Portal")
        st.subheader("Face Recognition Based Attendance System")
    
    # Add a separator
    st.markdown("<hr style='margin-bottom: 30px'>", unsafe_allow_html=True)
    
    # Welcome message with better styling
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h3 style='color: #1e88e5;'>Welcome to SIES GST Attendance Portal</h3>
        <p>This system uses facial recognition technology to mark attendance efficiently and securely.</p>
        <p>If you have already registered, please login with your credentials.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for buttons
    button_col1, button_col2 = st.columns(2)
    
    # Add styled buttons
    with button_col1:
        st.button("Register", on_click=lambda:navigate("Register"), use_container_width=True)
    
    with button_col2:
        st.button("Login", on_click=lambda:navigate("Login"), use_container_width=True)
        
    # Add footer
    st.markdown("<div style='text-align: center; margin-top: 50px; color: gray;'>© 2025 SIES Graduate School of Technology</div>", unsafe_allow_html=True) 