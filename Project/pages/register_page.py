"""
Registration page module for the SIES GST Attendance System
Contains the registration form UI and functionality
"""
import streamlit as st
from datetime import date
import time

from ..config import navigate, BRANCH_OPTIONS, ADMISSION_YEARS
from ..auth import create_user

def render(db):
    """
    Render the registration page
    
    Args:
        db: Firestore database instance
    """
    st.title("Welcome to Registration Page")
    st.warning("Once the registeration is done, Contact Admin to active your Facial Recognition to mark attendance")
    st.warning("Register with a valid Email ID for future updates.")
    st.button("Back to main page", on_click=lambda: navigate("main"))

    # Registration form using Streamlit form for proper Enter key handling
    with st.form(key="registration_form"):
        email = st.text_input("Enter Email")
        password = st.text_input("Enter Password", type="password")
        first_name = st.text_input("Enter the First Name")
        middle_name = st.text_input("Enter the Middle Name")
        last_name = st.text_input("Enter the Last Name")
        prn_no = st.text_input("Enter PRN Number")
        phone_number = st.text_input("Enter Phone Number")

        # Add Branch field with dropdown options
        branch = st.selectbox("Select Branch", BRANCH_OPTIONS)

        # Create a list of years for admission/graduation
        years = ADMISSION_YEARS
        year_of_admission = st.selectbox("Select Year of Admission", years)

        # Ensure graduation year is after admission year
        if year_of_admission:
            graduation_years = [y for y in years if y >= year_of_admission]
            year_of_graduation = st.selectbox("Select Year of Graduation", graduation_years)
        else:
            year_of_graduation = st.selectbox("Select Year of Graduation", years)

        default_date = date(2000, 1, 1)
        birth_date = st.date_input("Select Your Birth Date", min_value=date(1995, 1, 1), 
                              max_value=date.today(), value=default_date)

        parent_name = st.text_input("Enter Parent Name")
        parent_phone_number = st.text_input("Enter Parent Phone Number")
        
        # Add profile image upload field (required)
        st.write("Upload the Image (Required)")
        profile_image = st.file_uploader("Choose a profile image", type=["jpg", "jpeg", "png"])
        
        # 🔹 Register Submit Button (works with Enter key too)
        submit_button = st.form_submit_button(label="Register")
        
        if submit_button:
            # Check if any field is empty including profile image
            if not all([email, password, first_name, middle_name, last_name, prn_no, phone_number, parent_name, parent_phone_number, profile_image, branch]):
                st.error("Error: Please fill in all the fields including the profile image and branch.")
            else:
                result = create_user(
                    email, password, first_name, middle_name, last_name, 
                    prn_no, phone_number, year_of_admission, year_of_graduation, 
                    birth_date, parent_name, parent_phone_number, profile_image, branch, db
                )
                st.write(result)
                if "successfully" in result:
                    st.balloons()  # Show balloons on successful registration
                    time.sleep(3)
                    st.session_state["page"] = "main"
                    st.rerun() 