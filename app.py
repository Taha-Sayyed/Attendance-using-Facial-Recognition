import streamlit as st
from streamlit_webrtc import webrtc_streamer,VideoTransformerBase
import cv2 as cv
import numpy
import av
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import date, datetime
from dotenv import load_dotenv
import os
import requests
import json
import time
import base64
import io
import pandas as pd
import pytz
import csv

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
        self.all_predictions = []
    
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
            self.all_predictions = []
            return img
        
        # Otherwise, the result is an annotated image
        # Convert annotated PIL image back to BGR numpy array
        annotated_np = cv.cvtColor(np.array(result), cv.COLOR_RGB2BGR)
        
        # Import the last_predictions variable from the classifier module
        from classifier_model_for_testing import last_predictions
        
        # Update our predictions
        if last_predictions:
            self.all_predictions = last_predictions  # Store all recognized faces
            self.current_prediction = last_predictions[0] if last_predictions else "Unknown"  # Default to first face
        else:
            self.all_predictions = []
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
    st.markdown("<div style='text-align: center; margin-top: 50px; color: gray;'>© 2025 SIES Graduate School of Technology</div>", unsafe_allow_html=True)

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
    
    # Get user's name for personalized welcome
    if st.session_state["user"]:
        user_name = st.session_state["user"].get("first_name", "")
        if user_name:
            st.markdown(f"""
            <div style="background-color: #f0f7fa; padding: 15px; border-radius: 10px; margin-bottom: 25px; border-left: 5px solid #1e88e5;">
                <h1 style="color: #1e88e5; margin-bottom: 0;">Welcome, {user_name}!</h1>
                <p style="color: #555; font-size: 18px;">Attendance System Dashboard</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.title("Welcome to Attendance System")
    
    # Create a container for main content
    main_container = st.container()
    
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
            user_docs = db.collection("users").where(field_path="email", op_string="==", value=user_email).limit(1).stream()
            user_info = None
            for doc in user_docs:
                user_info = doc.to_dict()
                # Update session state with user details for future use
                st.session_state["user"].update(user_info)
                break
                
            has_user_info = user_info is not None
        
        # Display user profile in sidebar with improved styling
        with st.sidebar:
            st.markdown("""
            <style>
            .profile-header {
                text-align: center; 
                background-color: #1e88e5; 
                color: white; 
                padding: 10px; 
                border-radius: 8px 8px 0 0;
                margin-bottom: 0;
            }
            </style>
            <h2 class="profile-header">Student Profile</h2>
            """, unsafe_allow_html=True)
            
            # Profile card container
            st.markdown('<div style="background-color: #f0f7fa; padding: 15px; border-radius: 0 0 8px 8px; margin-bottom: 20px;">', unsafe_allow_html=True)
            
            # Display profile image at the top of sidebar if available
            if has_user_info and "profile_image" in user_info:
                try:
                    # Decode the base64 string to display the image
                    img_data = user_info["profile_image"]
                    # Use HTML for reliable image display from base64
                    st.markdown(f"""
                    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                        <img src="data:image/jpeg;base64,{img_data}" 
                            style="max-width: 100%; border-radius: 50%; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 150px; height: 150px; object-fit: cover;">
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error displaying profile image: {str(e)}")
            
            # Display user details with improved styling
            if has_user_info:
                name = f"{user_info.get('first_name', '')} {user_info.get('middle_name', '')} {user_info.get('last_name', '')}"
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 20px; font-weight: bold; color: #333;">{name}</div>
                </div>
                <div style="margin-top: 15px;">
                    <p><strong>Email:</strong> {user_info.get('email', '')}</p>
                    <p><strong>PRN Number:</strong> {user_info.get('prn_no', '')}</p>
                    <p><strong>Batch:</strong> {user_info.get('year_of_admission', '')}-{user_info.get('year_of_graduation', '')}</p>
                    <p><strong>Branch:</strong> {user_info.get('branch', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Close profile card container
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Logout button with styling
            if st.button("Logout", type="primary"):
                st.session_state["user"] = None
                st.session_state["page"] = "main"
                st.rerun()
        
        # Main content area
        with main_container:
            # Create tabs for different functionality
            tab1, tab2 = st.tabs(["Mark Attendance", "Attendance History"])
            
            with tab1:
                st.markdown("""
                <div style="background-color: #f0f7fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: #1e88e5;">Mark Your Attendance</h3>
                    <p>Click the button below to start the attendance process using facial recognition.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mark attendance button with better placement and styling
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("Mark my attendance", use_container_width=True):     
                        st.session_state["mark_attendance_active"] = True
                
                # Only show video stream if the mark_attendance_active flag is set
                if st.session_state.get("mark_attendance_active"):
                    st.markdown("""
                    <div style="background-color: #f0f7fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="color: #1e88e5;">Live Video Stream</h3>
                        <p>Please position your face clearly in the camera frame.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    from streamlit_webrtc import webrtc_streamer
                    
                    # Create a shared variable to store the current prediction
                    if "current_face" not in st.session_state:
                        st.session_state["current_face"] = "No face detected"
                    
                    # Create the video streamer
                    webrtc_ctx = webrtc_streamer(
                        key="attendance", 
                        video_processor_factory=FaceDetectionTransformer
                    )
                    
                    # Add the submit attendance button with better styling
                    if webrtc_ctx.video_processor:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button("Submit Attendance", use_container_width=True, type="primary"):
                                # Get all predictions from the transformer
                                all_predictions = webrtc_ctx.video_processor.all_predictions
                                
                                # Create the full name of the logged-in user
                                if st.session_state["user"]:
                                    user_first_name = st.session_state["user"].get("first_name", "")
                                    user_middle_name = st.session_state["user"].get("middle_name", "")
                                    user_last_name = st.session_state["user"].get("last_name", "")
                                    user_full_name = f"{user_first_name} {user_middle_name} {user_last_name}".strip()
                                    
                                    # Check if no faces were detected or the user's face is not among them
                                    if not all_predictions or all_predictions[0] == "No face detected":
                                        st.error("No face detected. Please ensure your face is clearly visible in the camera.")
                                    elif user_full_name not in all_predictions:
                                        st.error(f"Your face was not recognized. Only {user_full_name} can mark attendance with this account.")
                                    else:
                                        # User's face is recognized - mark attendance
                                        st.success(f"{user_full_name} has been marked present!")
                                        
                                        try:
                                            # Add attendance record to Firestore
                                            attendance_data = {
                                                "user_email": st.session_state["user"]["email"],
                                                "name": user_full_name,
                                                "timestamp": firestore.SERVER_TIMESTAMP
                                            }
                                            db.collection("attendance").add(attendance_data)
                                            st.info("Attendance recorded successfully in the database.")
                                        except Exception as e:
                                            st.warning(f"Could not record attendance in database: {e}")
                                        
                                        # Reset the mark_attendance_active flag to stop the video stream
                                        st.session_state["mark_attendance_active"] = False
                                        st.rerun()
                                else:
                                    st.error("User information not available. Please log in again.")
                    
                    # Add a button to close the webcam
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("Cancel", use_container_width=True):
                            st.session_state["mark_attendance_active"] = False
                            st.rerun()
            
            with tab2:
                st.markdown("""
                <div style="background-color: #f0f7fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: #1e88e5;">Attendance History</h3>
                    <p>View your attendance records and download as CSV file.</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state["user"]:
                    user_email = st.session_state["user"]["email"]
                    
                    # Create a query to get attendance records for the current user
                    # Removed the order_by to avoid requiring composite index
                    attendance_query = db.collection("attendance").where(field_path="user_email", op_string="==", value=user_email)
                    
                    try:
                        # Execute the query
                        attendance_docs = attendance_query.stream()
                        
                        # Convert to a list to check if there are any records
                        attendance_records = []
                        timezone = pytz.timezone('Asia/Kolkata')
                        
                        for doc in attendance_docs:
                            record = doc.to_dict()
                            # Convert Firestore timestamp to datetime
                            if record.get('timestamp'):
                                # The timestamp from Firestore is already a datetime-like object
                                timestamp = record['timestamp']
                                
                                # Convert to regular Python datetime
                                # DatetimeWithNanoseconds doesn't have datetime attribute,
                                # it's already a datetime-like object
                                dt = timestamp
                                
                                # Convert to local timezone
                                local_dt = dt.astimezone(timezone)
                                
                                # Format day, date and time
                                day = local_dt.strftime('%A')
                                date_str = local_dt.strftime('%d-%m-%Y')
                                time_str = local_dt.strftime('%I:%M:%S %p')
                                
                                # Add to record
                                record['day'] = day
                                record['date'] = date_str
                                record['time'] = time_str
                                record['datetime'] = local_dt
                                
                                # Include record only if it has valid timestamp data
                                attendance_records.append(record)
                            else:
                                # Skip records without timestamps
                                st.warning(f"Found record without timestamp data, skipping.")
                        
                        if attendance_records:
                            # Sort records by timestamp (descending) in Python
                            attendance_records.sort(key=lambda x: x.get('datetime', datetime.min), reverse=True)
                            
                            # Display attendance records in a nice table
                            st.subheader("Your Attendance Records")
                            
                            # Convert to DataFrame for better display
                            df = pd.DataFrame(attendance_records)
                            
                            # Display in a table with selected columns and formatting
                            if 'day' in df.columns and 'date' in df.columns and 'time' in df.columns:
                                display_df = df[['day', 'date', 'time', 'name']].rename(
                                    columns={
                                        'day': 'Day',
                                        'date': 'Date',
                                        'time': 'Time',
                                        'name': 'Recognized As'
                                    }
                                )
                                st.dataframe(display_df, use_container_width=True)
                                
                                # Function to convert DataFrame to CSV
                                def convert_df_to_csv(df):
                                    return df.to_csv(index=False).encode('utf-8')
                                
                                # Add CSV download button
                                csv_data = convert_df_to_csv(display_df)
                                
                                st.download_button(
                                    label="Download Attendance Records as CSV",
                                    data=csv_data,
                                    file_name=f"attendance_records_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv",
                                    help="Download your attendance history as a CSV file",
                                    use_container_width=True
                                )
                                
                                # Display attendance statistics
                                st.subheader("Attendance Statistics")
                                
                                # Calculate statistics
                                total_records = len(df)
                                current_month = datetime.now().month
                                current_year = datetime.now().year
                                
                                # Count records for current month
                                month_records = df[df['datetime'].dt.month == current_month]
                                month_count = len(month_records)
                                
                                # Create columns for statistics display
                                stat_col1, stat_col2 = st.columns(2)
                                
                                with stat_col1:
                                    st.metric("Total Attendance Records", total_records)
                                
                                with stat_col2:
                                    st.metric(f"Attendance in {datetime.now().strftime('%B %Y')}", month_count)
                                
                            else:
                                st.info("Attendance records are available but missing some timestamp information.")
                        else:
                            st.info("You haven't marked any attendance yet.")
                            
                    except Exception as e:
                        st.error(f"Error retrieving attendance records: {e}")
                        st.exception(e)  # Display the full traceback for debugging
                        
                        # Show guidance about fixing the index
                        st.info("""
                        If you're seeing an index error, you'll need to create a composite index in Firebase.
                        
                        **To fix this:**
                        1. Go to your Firebase console
                        2. Navigate to Firestore Database > Indexes
                        3. Add a composite index for the 'attendance' collection with fields:
                           - user_email (Ascending)
                           - timestamp (Descending)
                        """)
                else:
                    st.error("User information not available. Please log in again.")
#Logic added By Taha Sayyed --------------------------------------------------------------------------