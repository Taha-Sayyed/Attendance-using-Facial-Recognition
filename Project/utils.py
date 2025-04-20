"""
Utility functions for the SIES GST Attendance System
Contains helper functions for image processing, data conversion, etc.
"""
import base64
import io
from PIL import Image
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO

def image_to_base64(img):
    """
    Convert a PIL Image to base64 encoded string
    
    Args:
        img (PIL.Image): Image to convert
        
    Returns:
        str: Base64 encoded string of the image
    """
    # Ensure image is in RGB mode (not RGBA) to prevent JPEG encoding issues
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Use BytesIO for in-memory file handling
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)  # Reduce quality to keep size manageable
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def convert_df_to_csv(df):
    """
    Convert a pandas DataFrame to CSV format for download
    
    Args:
        df (pd.DataFrame): DataFrame to convert
        
    Returns:
        bytes: CSV data as UTF-8 encoded bytes
    """
    return df.to_csv(index=False).encode('utf-8')

def format_timestamp(timestamp, timezone_str='Asia/Kolkata'):
    """
    Format a Firestore timestamp into day, date, and time strings
    
    Args:
        timestamp: Firestore timestamp object
        timezone_str (str): Timezone string
        
    Returns:
        tuple: (day, date_str, time_str, local_dt)
    """
    timezone = pytz.timezone(timezone_str)
    
    # Convert to local timezone
    local_dt = timestamp.astimezone(timezone)
    
    # Format day, date and time
    day = local_dt.strftime('%A')
    date_str = local_dt.strftime('%d-%m-%Y')
    time_str = local_dt.strftime('%I:%M:%S %p')
    
    return day, date_str, time_str, local_dt 