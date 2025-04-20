"""
Authentication module for the SIES GST Attendance System
Contains functions for user registration and login
"""
import streamlit as st
import requests
import json
import firebase_admin
from firebase_admin import auth, firestore
from PIL import Image
from .utils import image_to_base64

def create_user(email, password, first_name, middle_name, last_name, prn_no, phone_number, 
                year_of_admission, year_of_graduation, birth_date, parent_name, parent_phone_number, profile_image, branch, db):
    """
    Register a new user with Firebase Authentication and Firestore
    
    Args:
        email (str): User's email
        password (str): User's password
        first_name (str): User's first name
        middle_name (str): User's middle name
        last_name (str): User's last name
        prn_no (str): User's PRN number
        phone_number (str): User's phone number
        year_of_admission (int): Year of admission
        year_of_graduation (int): Year of graduation
        birth_date (date): User's birth date
        parent_name (str): Name of parent/guardian
        parent_phone_number (str): Phone number of parent/guardian
        profile_image (BytesIO): User's profile image
        branch (str): User's branch
        db (firestore.Client): Firestore client instance
        
    Returns:
        str: Success or error message
    """
    if not email or not password or profile_image is None:
        return "Error: Email, password, and profile image are required."
    
    try:
        # Firebase Auth only takes email & password
        user = auth.create_user(email=email, password=password)
        uid = user.uid

        try:
            # Process the profile image
            image = Image.open(profile_image)
            
            # Resize to reduce storage size (300x300 pixels is reasonable for a profile)
            image = image.resize((300, 300))
            
            # Convert image to base64 string for Firestore storage
            profile_image_b64 = image_to_base64(image)
            
            # Save all user details in Firestore
            user_doc = {
                "uid": uid,
                "email": email,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "prn_no": prn_no,
                "phone_number": phone_number,
                "birth_date": str(birth_date),  # Convert date to string
                "year_of_admission": year_of_admission,
                "year_of_graduation": year_of_graduation,
                "parent_name": parent_name,
                "parent_phone_number": parent_phone_number,
                "profile_image": profile_image_b64,  # Store base64 image directly in Firestore
                "branch": branch
            }
            db.collection("users").document(uid).set(user_doc)
            return f"Account for {email} created successfully! ✅"

        except Exception as e:
            return f"Firestore Error: {e}"
        
    except Exception as e:
        return f"Error: {e}"

def login_user(email, password, api_key):
    """
    Authenticate a user using Firebase REST API
    
    Args:
        email (str): User's email
        password (str): User's password
        api_key (str): Firebase API key
        
    Returns:
        dict: Authentication response containing tokens and user info
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, data=json.dumps(payload))
    return response.json()

def get_user_details(user_id, db):
    """
    Retrieve user details from Firestore
    
    Args:
        user_id (str): User ID
        db (firestore.Client): Firestore client instance
        
    Returns:
        dict: User details or None
    """
    try:
        user_doc = db.collection("users").document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict()
        return None
    except Exception as e:
        st.error(f"Error retrieving user data: {e}")
        return None

def get_user_by_email(email, db):
    """
    Find a user by email in Firestore
    
    Args:
        email (str): User's email
        db (firestore.Client): Firestore client instance
        
    Returns:
        dict: User details or None
    """
    try:
        user_docs = db.collection("users").where("email", "==", email).limit(1).stream()
        for doc in user_docs:
            return doc.to_dict()
        return None
    except Exception as e:
        st.error(f"Error retrieving user by email: {e}")
        return None 