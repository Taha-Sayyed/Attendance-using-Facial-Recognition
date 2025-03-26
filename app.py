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


# Define Firebase user registration function
def create_user(email, password, first_name, middle_name, last_name, prn_no, phone_number, 
                year_of_admission, year_of_graduation, birth_date, parent_name, parent_phone_number):
    if not email or not password:
        return "Error: Email and password are required."
    
    try:
        # Firebase Auth only takes email & password
        user = auth.create_user(email=email, password=password)
        uid = user.uid

        try:
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
                "parent_phone_number": parent_phone_number
            }
            db.collection("users").document(uid).set(user_doc)
            return f"User {email} created successfully! ✅ (UID: {uid})"

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
    def transform(self, frame: av.VideoFrame) -> np.ndarray:
        # Get frame as numpy array in BGR format
        img = frame.to_ndarray(format="bgr24")
        # Convert to PIL image (RGB) for classifier input
        pil_img = Image.fromarray(cv.cvtColor(img, cv.COLOR_BGR2RGB))
        result = predict_person(pil_img)
        # If result is a string (error message), overlay text on original frame
        if isinstance(result, str):
            cv.putText(img, result, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return img
        # Otherwise, convert annotated PIL image back to BGR numpy array
        annotated_np = cv.cvtColor(np.array(result), cv.COLOR_RGB2BGR)
        return annotated_np
# Logic added by Taha Sayyed ----------------------------------------


#Main Page [Landing page]
if st.session_state["page"] == "main":
    st.title("Welcome to Landing Page")
    st.warning("If you already registered then Login with your Email")
    st.button("Register",on_click=lambda:navigate("Register"))
    st.button("Login",on_click=lambda:navigate("Login"))

# Registeration Page
elif st.session_state["page"] == "Register":
    st.title("Welcome to Registration Page")
    st.warning("Once the registeration is done, Contact Admin to active your Facial Recognition to mark attendance")
    st.warning("Register with a valid Email ID for future updates.")
    st.button("Back to main page", on_click=lambda: navigate("main"))

    # Registration form UI
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")
    first_name = st.text_input("Enter the First Name")
    middle_name = st.text_input("Enter the Middle Name")
    last_name = st.text_input("Enter the Last Name")
    prn_no = st.text_input("Enter PRN Number")
    phone_number = st.text_input("Enter Phone Number")

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

    # 🔹 Register Button
    if st.button("Register"):
        # Check if any field is empty
        if not all([email, password, first_name, middle_name, last_name, prn_no, phone_number, parent_name, parent_phone_number]):
            st.error("Error: Please fill in all the fields.")
        else:
            result = create_user(
                email, password, first_name, middle_name, last_name, 
                prn_no, phone_number, year_of_admission, year_of_graduation, 
                birth_date, parent_name, parent_phone_number
            )
            st.write(result)
            # time.sleep(3)
            # st.session_state["page"]="main"
            # st.rerun()

    
        

elif st.session_state["page"] == "Login":
    st.title("Welcome to Login Page")
    st.button("Back to main page", on_click=lambda: navigate("main"))
    
    # If user is already logged in, redirect to home
    if st.session_state["user"]:
        st.session_state["page"] = "home"
        st.rerun()
    else:
        # Login UI
        email = st.text_input("Enter Email", key="login_email")
        password = st.text_input("Enter Password", type="password", key="login_password")
        
        if st.button("Login"):
            result = login_user(email, password)
            if "idToken" in result:
                st.session_state["user"] = {"email": email, "idToken": result["idToken"]}
                st.session_state["page"] = "home"  # Navigate to home page after login
                st.rerun()
            else:
                st.error("❌ Login Failed: " + result.get("error", {}).get("message", "Unknown error"))

# Home Page
elif st.session_state["page"] == "home":
    st.title("Welcome to Home Page")
    
    # Display logged-in user's email
    if st.session_state["user"]:
        st.write(f"👋 Welcome, {st.session_state['user']['email']}")
    
    # Retrieve and display the logged-in user's information in the sidebar
    if st.session_state["user"]:
        user_email = st.session_state["user"]["email"]
        # Query the Firestore collection for the current user by email
        user_docs = db.collection("users").where("email", "==", user_email).stream()
        with st.sidebar:
            st.header("Student Profile")
            for doc in user_docs:
                user_info = doc.to_dict()
                st.write(f"**Email:** {user_info.get('email', '')}")
                st.write(f"**Name:** {user_info.get('first_name', '')} {user_info.get('middle_name', '')} {user_info.get('last_name', '')}")
                st.write(f"PRN number: {user_info.get('prn_no', '')}")
                # You can add more fields as needed
        
        # Button to show image uploader
        if st.button("Upload the Image"):
            st.session_state["upload_active"] = True
        
        # If the user has activated image uploading, show the file uploader widget
        if st.session_state.get("upload_active"):
            uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
            if uploaded_file is not None:
                try:
                    # Open the image using PIL
                    image = Image.open(uploaded_file)
                    
                    # Optionally, display the uploaded image
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                    
                    # Process the image and predict the person's name using the imported classifier function.
                    with st.spinner("Processing image and predicting..."):
                        predicted_name = predict_person(image)
                        
                    st.success(f"Predicted Name: {predicted_name}")
                except Exception as e:
                    st.error("An error occurred during processing. Please try again.")
                    st.error(str(e))
        
        # New attendance button to start live video stream
        if st.button("Mark my attendance"):
            st.session_state["mark_attendance_active"] = True
        
        if st.session_state.get("mark_attendance_active"):
            from streamlit_webrtc import webrtc_streamer
            st.write("Live video stream:")
            webrtc_streamer(key="attendance", video_processor_factory=FaceDetectionTransformer)
    # Logout Button
    if st.button("Logout"):
        st.session_state["user"] = None
        st.session_state["page"] = "main"
        st.rerun()
    
#Logic added By Taha Sayyed --------------------------------------------------------------------------

