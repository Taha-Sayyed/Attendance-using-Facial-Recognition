"""
Face recognition module for the SIES GST Attendance System
Contains the face detection, recognition, and prediction functionality
"""
import numpy as np
import pickle
from PIL import Image, ImageDraw, ImageFont
import cv2
import tensorflow as tf
from mtcnn.mtcnn import MTCNN

# Global variables
detector = MTCNN()
model = None
face_embeddings = None
last_predictions = []

def load_models():
    """Load the face recognition models"""
    global model, face_embeddings
    
    # Load the best model from pickle file
    try:
        with open('best_model.pkl', 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        
    # Load the face embeddings
    try:
        face_embeddings = np.load('face_embeddig_for_12_class.npz')
        print("Face embeddings loaded successfully!")
    except Exception as e:
        print(f"Error loading face embeddings: {e}")
        print("Trying alternate face embeddings file...")
        try:
            face_embeddings = np.load('../face_embeddig_for_8_class.npz')
            print("Alternate face embeddings loaded successfully!")
        except Exception as e2:
            print(f"Error loading alternate face embeddings: {e2}")

# Load FaceNet model
def load_facenet_model():
    """Load the FaceNet model for embedding generation"""
    model = tf.keras.models.load_model('facenet_keras.h5')
    return model

# Preprocess image for FaceNet
def preprocess_image(img):
    """Preprocess an image for FaceNet input"""
    img = img.resize((160, 160))
    img = np.array(img)
    img = np.expand_dims(img, axis=0)
    img = (img - 127.5) / 128  # normalize pixel values
    return img

# Get face embedding using FaceNet
def get_embedding(face_img, facenet_model):
    """Get the embedding vector for a face image"""
    face_img = preprocess_image(face_img)
    embedding = facenet_model.predict(face_img)
    return embedding[0]

# Detect faces in an image
def detect_faces(img):
    """
    Detect faces in an image using MTCNN
    
    Args:
        img (PIL.Image): Image to detect faces in
        
    Returns:
        list: List of detected face bounding boxes
    """
    img_array = np.array(img)
    faces = detector.detect_faces(img_array)
    return faces

# Predict person from face
def predict_person(img):
    """
    Predict the identity of persons in an image
    
    Args:
        img (PIL.Image): Image containing faces to identify
        
    Returns:
        PIL.Image or str: Annotated image with predictions or error message
    """
    global last_predictions, model, face_embeddings
    
    # Load models if not already loaded
    if model is None or face_embeddings is None:
        load_models()
        if model is None or face_embeddings is None:
            return "Error: Could not load models"
    
    # Reset last predictions
    last_predictions = []
    
    # Detect faces
    try:
        faces = detect_faces(img)
        if not faces:
            return "No face detected"
        
        # Create a copy of image for drawing
        draw_img = img.copy()
        draw = ImageDraw.Draw(draw_img)
        
        for face in faces:
            x, y, w, h = face['box']
            # Extract face from image
            face_img = img.crop((x, y, x+w, y+h))
            
            # Convert to RGB if needed
            if face_img.mode != 'RGB':
                face_img = face_img.convert('RGB')
            
            # Resize to match the input size of embeddings
            face_img = face_img.resize((160, 160))
            
            # Convert to numpy array and normalize
            face_array = np.array(face_img)
            face_array = (face_array - face_array.mean()) / face_array.std()
            
            # Reshape for model input
            face_array = face_array.reshape(1, -1)
            
            # Predict using the model
            prediction = model.predict(face_array)
            probability = model.predict_proba(face_array).max()
            
            # Get the name from prediction
            predicted_name = prediction[0]
            last_predictions.append(predicted_name)
            
            # Draw rectangle around face
            draw.rectangle([(x, y), (x+w, y+h)], outline="green", width=2)
            
            # Draw name and probability
            text = f"{predicted_name} ({probability:.2f})"
            draw.text((x, y-15), text, fill="green")
            
        return draw_img
        
    except Exception as e:
        print(f"Error in predict_person: {e}")
        return f"Error: {str(e)}" 