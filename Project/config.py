"""
Configuration module for the SIES GST Attendance System
Contains global settings, Firebase initialization, and session state setup
"""
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv
import os

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')

# Initialize session state variables
def init_session_state():
    if "page" not in st.session_state:
        st.session_state["page"] = "main"

    if "user" not in st.session_state:
        st.session_state["user"] = None
        
    if "mark_attendance_active" not in st.session_state:
        st.session_state["mark_attendance_active"] = False
        
    if "current_face" not in st.session_state:
        st.session_state["current_face"] = "No face detected"
        
    if "show_balloons" not in st.session_state:
        st.session_state["show_balloons"] = False

# Firebase initialization
def init_firebase():
    cred = credentials.Certificate("../techfusion-firestore-key.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Function for navigation between pages
def navigate(page):
    st.session_state["page"] = page
    
# Constants and configurations
TIMEZONE = 'Asia/Kolkata'
BRANCH_OPTIONS = ["CS", "EXTC", "AIML", "AIDS", "IT", "MECHANICAL"]
ADMISSION_YEARS = list(range(2020, 2031)) 