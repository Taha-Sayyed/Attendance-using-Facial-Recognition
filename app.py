import streamlit as st
from streamlit_webrtc import webrtc_streamer,VideoTransformerBase
import cv2 as cv
import numpy
import av
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import date
from dotenv import load_dotenv
import os
import requests
import json
import time
import base64
import io

# Import necessary modules for image processing and prediction
import pickle
import numpy as np
from PIL import Image

# Import your classifier prediction function (assuming this function is defined in classifier_model_for_testing.py)
from classifier_model_for_testing import predict_person  # This function should encapsulate all pre-processing steps as in your classifier code

# Load API Key from .env file
load_dotenv()
api_key = os.getenv('API_KEY')

if "page" not in st.session_state:
    st.session_state["page"] = "main"

if "user" not in st.session_state:
    st.session_state["user"] = None

def navigate(page):
    st.session_state["page"] = page

#Logic added By Taha Sayyed --------------------------------------------------------------------------
# Firebase initialization
cred = credentials.Certificate("techfusion-firestore-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()
st.write("Firebase Initialized Successfully ✅")

# Function to convert image to base64 string
def image_to_base64(img):
    # Ensure image is in RGB mode (not RGBA) to prevent JPEG encoding issues
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Use BytesIO for in-memory file handling
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)  # Reduce quality to keep size manageable
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

# Define Firebase user registration function
def create_user(email, password, first_name, middle_name, last_name, prn_no, phone_number, 
                year_of_admission, year_of_graduation, birth_date, parent_name, parent_phone_number, profile_image, branch):
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

# Function to authenticate user using Firebase REST API
def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, data=json.dumps(payload))
    return response.json()

# Logic added by Taha Sayyed ----------------------------------------
# ------------------- Live Video Transformer -------------------

class FaceDetectionTransformer(VideoTransformerBase):
    def __init__(self):
        self.current_prediction = "No face detected"
    
    def transform(self, frame: av.VideoFrame) -> np.ndarray:
        # Get frame as numpy array in BGR format
        img = frame.to_ndarray(format="bgr24")
        # Convert to PIL image (RGB) for classifier input
        pil_img = Image.fromarray(cv.cvtColor(img, cv.COLOR_BGR2RGB))
        
        # Process the image with our face recognition function
        result = predict_person(pil_img)
        
        # If result is a string (error message), overlay text on original frame
        if isinstance(result, str):
            cv.putText(img, result, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.current_prediction = result
            return img
        
        # Otherwise, the result is an annotated image
        # Convert annotated PIL image back to BGR numpy array
        annotated_np = cv.cvtColor(np.array(result), cv.COLOR_RGB2BGR)
        
        # Import the last_predictions variable from the classifier module
        from classifier_model_for_testing import last_predictions
        
        # Update our current prediction
        if last_predictions:
            self.current_prediction = last_predictions[0]  # Get the first prediction if multiple faces
        else:
            self.current_prediction = "Unknown"
            
        return annotated_np
# Logic added by Taha Sayyed ----------------------------------------


#Main Page [Landing page]
if st.session_state["page"] == "main":
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
    st.markdown("<div style='text-align: center; margin-top: 50px; color: gray;'>© 2023 SIES Graduate School of Technology</div>", unsafe_allow_html=True)

# Registeration Page
elif st.session_state["page"] == "Register":
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
        branch_options = ["CS", "EXTC", "AIML", "AIDS", "IT", "MECHANICAL"]
        branch = st.selectbox("Select Branch", branch_options)

        # Create a list of years for admission/graduation
        years = list(range(2020, 2031))
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
                    birth_date, parent_name, parent_phone_number, profile_image, branch
                )
                st.write(result)
                if "successfully" in result:
                    st.balloons()  # Show balloons on successful registration
                    time.sleep(3)
                    st.session_state["page"] = "main"
                    st.rerun()

elif st.session_state["page"] == "Login":
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
                result = login_user(email, password)
                if "idToken" in result:
                    # Get the user ID (localId) to retrieve full user details
                    user_id = result.get("localId", "")
                    user_data = {"email": email, "idToken": result["idToken"]}
                    
                    # Retrieve complete user details from Firestore if ID is available
                    if user_id:
                        try:
                            user_doc = db.collection("users").document(user_id).get()
                            if user_doc.exists:
                                user_data.update(user_doc.to_dict())
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

# Home Page
elif st.session_state["page"] == "home":
    # Show balloons on successful login
    if st.session_state.get("show_balloons", False):
        st.balloons()
        st.session_state["show_balloons"] = False  # Reset flag
        
    st.title("Welcome to Home Page")
    
    # Display logged-in user's name or email
    if st.session_state["user"]:
        user_name = st.session_state["user"].get("first_name", st.session_state["user"]["email"])
        st.write(f"👋 Welcome, {user_name}")
    
    # Retrieve and display the logged-in user's information in the sidebar
    if st.session_state["user"]:
        user_email = st.session_state["user"]["email"]
        
        # Query Firestore to get user details
        # First check if we already have user details in session
        if "profile_image" in st.session_state["user"]:
            user_info = st.session_state["user"]
            has_user_info = True
        else:
            # Query the user from Firestore by email
            user_docs = db.collection("users").where("email", "==", user_email).limit(1).stream()
            user_info = None
            for doc in user_docs:
                user_info = doc.to_dict()
                # Update session state with user details for future use
                st.session_state["user"].update(user_info)
                break
                
            has_user_info = user_info is not None
        
        # Display user profile in sidebar
        with st.sidebar:
            st.header("Student Profile")
            
            # Display profile image at the top of sidebar if available
            if has_user_info and "profile_image" in user_info:
                try:
                    # Decode the base64 string to display the image
                    img_data = user_info["profile_image"]
                    # Use HTML for reliable image display from base64
                    st.markdown(f"""
                    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                        <img src="data:image/jpeg;base64,{img_data}" 
                            style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error displaying profile image: {str(e)}")
            
            # Display user details
            if has_user_info:
                name = f"{user_info.get('first_name', '')} {user_info.get('middle_name', '')} {user_info.get('last_name', '')}"
                st.markdown(f"**Name:** {name}")
                st.markdown(f"**Email:** {user_info.get('email', '')}")
                st.markdown(f"**PRN Number:** {user_info.get('prn_no', '')}")
                st.markdown(f"**Batch:** {user_info.get('year_of_admission', '')}-{user_info.get('year_of_graduation', '')}")
                st.markdown(f"**Branch:** {user_info.get('branch', '')}")
        
        # New attendance button to start live video stream
        if st.button("Mark my attendance"):     
            st.session_state["mark_attendance_active"] = True
        
        if st.session_state.get("mark_attendance_active"):
            from streamlit_webrtc import webrtc_streamer
            
            st.write("Live video stream:")
            # Create a shared variable to store the current prediction
            if "current_face" not in st.session_state:
                st.session_state["current_face"] = "No face detected"
            
            # Create the video streamer
            webrtc_ctx = webrtc_streamer(
                key="attendance", 
                video_processor_factory=FaceDetectionTransformer
            )
            
            # Add the submit attendance button
            if webrtc_ctx.video_processor:
                if st.button("Submit your attendance"):
                    # Get the current prediction from the transformer
                    current_prediction = webrtc_ctx.video_processor.current_prediction
                    
                    # Display appropriate message based on the prediction
                    if current_prediction in ["No face detected", "Unknown"]:
                        st.error("Either no face is detected or Unknown face is detected")
                    else:
                        st.success(f"{current_prediction} has marked the attendance")
                        
                        # Optional: Record the attendance in Firestore
                        if st.session_state["user"]:
                            try:
                                # Add attendance record to Firestore
                                attendance_data = {
                                    "user_email": st.session_state["user"]["email"],
                                    "name": current_prediction,
                                    "timestamp": firestore.SERVER_TIMESTAMP
                                }
                                db.collection("attendance").add(attendance_data)
                                st.info("Attendance recorded in database")
                            except Exception as e:
                                st.warning(f"Could not record attendance in database: {e}")
    # Logout Button
    if st.button("Logout"):
        st.session_state["user"] = None
        st.session_state["page"] = "main"
        st.rerun()
    
#Logic added By Taha Sayyed --------------------------------------------------------------------------