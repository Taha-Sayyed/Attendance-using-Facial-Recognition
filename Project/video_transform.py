"""
Video transform module for the SIES GST Attendance System
Contains the video transformer for webcam-based face detection
"""
import streamlit as st
from streamlit_webrtc import VideoTransformerBase
import av
import cv2 as cv
import numpy as np
from PIL import Image

# Import face recognition functions
from .face_recognition import predict_person, last_predictions

class FaceDetectionTransformer(VideoTransformerBase):
    """
    Video transformer for face detection and recognition
    
    This class processes video frames from the webcam to detect and recognize faces
    """
    def __init__(self):
        """Initialize the transformer"""
        self.current_prediction = "No face detected"
    
    def transform(self, frame: av.VideoFrame) -> np.ndarray:
        """
        Transform a video frame to detect and recognize faces
        
        Args:
            frame (av.VideoFrame): Video frame from webcam
            
        Returns:
            np.ndarray: Processed frame with face detection
        """
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
        
        # Update our current prediction
        if last_predictions:
            self.current_prediction = last_predictions[0]  # Get the first prediction if multiple faces
        else:
            self.current_prediction = "Unknown"
            
        return annotated_np 