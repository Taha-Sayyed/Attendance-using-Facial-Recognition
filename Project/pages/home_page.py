"""
Home page module for the SIES GST Attendance System
Contains the home page UI and functionality including attendance marking
"""
import streamlit as st
from streamlit_webrtc import webrtc_streamer

from ..config import navigate
from ..attendance import record_attendance, get_attendance_records, display_attendance_history
from ..video_transform import FaceDetectionTransformer

def render(db):
    """
    Render the home page
    
    Args:
        db: Firestore database instance
    """
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
        
        # Check if we already have user details in session
        if "profile_image" in st.session_state["user"]:
            user_info = st.session_state["user"]
            has_user_info = True
        else:
            # We should already have user_info from login, but just in case
            has_user_info = "first_name" in st.session_state["user"]
            user_info = st.session_state["user"]
        
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
                                # Get the current prediction from the transformer
                                current_prediction = webrtc_ctx.video_processor.current_prediction
                                
                                # Display appropriate message based on the prediction
                                if current_prediction in ["No face detected", "Unknown"]:
                                    st.error("Either no face is detected or the face is unrecognized. Please try again.")
                                else:
                                    st.success(f"{current_prediction} has been marked present!")
                                    
                                    # Record the attendance in Firestore
                                    if st.session_state["user"]:
                                        if record_attendance(user_email, current_prediction, db):
                                            st.info("Attendance recorded successfully in the database.")
                                        
                                    # Reset the mark_attendance_active flag to stop the video stream
                                    st.session_state["mark_attendance_active"] = False
                                    st.rerun()
                    
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
                
                # Get attendance records for the current user
                attendance_records = get_attendance_records(user_email, db)
                
                # Display attendance history
                display_attendance_history(attendance_records)
                
                # Show guidance about fixing the index if needed
                with st.expander("Having issues with attendance records?"):
                    st.info("""
                    If you're seeing index errors, you may need to create a composite index in Firebase.
                    
                    **To fix this:**
                    1. Go to your Firebase console
                    2. Navigate to Firestore Database > Indexes
                    3. Add a composite index for the 'attendance' collection with fields:
                       - user_email (Ascending)
                       - timestamp (Descending)
                    """)
    else:
        st.error("User information not available. Please log in again.") 