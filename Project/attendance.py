"""
Attendance module for the SIES GST Attendance System
Contains functions for recording and viewing attendance
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from firebase_admin import firestore
from .utils import format_timestamp, convert_df_to_csv

def record_attendance(user_email, recognized_name, db):
    """
    Record attendance in Firestore
    
    Args:
        user_email (str): User's email
        recognized_name (str): Recognized name from face recognition
        db (firestore.Client): Firestore client instance
        
    Returns:
        bool: Success status
    """
    try:
        # Add attendance record to Firestore
        attendance_data = {
            "user_email": user_email,
            "name": recognized_name,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        db.collection("attendance").add(attendance_data)
        return True
    except Exception as e:
        st.warning(f"Could not record attendance in database: {e}")
        return False

def get_attendance_records(user_email, db, timezone_str='Asia/Kolkata'):
    """
    Retrieve attendance records for a user
    
    Args:
        user_email (str): User's email
        db (firestore.Client): Firestore client instance
        timezone_str (str): Timezone string
        
    Returns:
        list: Attendance records or empty list on error
    """
    try:
        # Query without order_by to avoid composite index requirement
        attendance_query = db.collection("attendance").where("user_email", "==", user_email)
        attendance_docs = attendance_query.stream()
        
        # Process records
        attendance_records = []
        timezone = pytz.timezone(timezone_str)
        
        for doc in attendance_docs:
            record = doc.to_dict()
            # Convert Firestore timestamp to datetime
            if record.get('timestamp'):
                timestamp = record['timestamp']
                
                # Format the timestamp
                day, date_str, time_str, local_dt = format_timestamp(timestamp, timezone_str)
                
                # Add to record
                record['day'] = day
                record['date'] = date_str
                record['time'] = time_str
                record['datetime'] = local_dt
                
                # Include record only if it has valid timestamp data
                attendance_records.append(record)
                
        # Sort records by timestamp (descending) in Python
        attendance_records.sort(key=lambda x: x.get('datetime', datetime.min), reverse=True)
        
        return attendance_records
        
    except Exception as e:
        st.error(f"Error retrieving attendance records: {e}")
        return []

def display_attendance_history(attendance_records):
    """
    Display attendance history in a Streamlit interface
    
    Args:
        attendance_records (list): List of attendance records
        
    Returns:
        None
    """
    if not attendance_records:
        st.info("You haven't marked any attendance yet.")
        return
    
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