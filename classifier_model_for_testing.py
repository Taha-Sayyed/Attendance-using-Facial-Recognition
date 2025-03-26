import pickle
import numpy as np
import cv2 as cv
from mtcnn.mtcnn import MTCNN
from keras_facenet import FaceNet
from PIL import Image
from sklearn.preprocessing import LabelEncoder

# ----------------------------
# Load the Classifier Model
# ----------------------------
model_path = "best_model_2.pkl"  # Adjust path as necessary
with open(model_path, 'rb') as f:
    model = pickle.load(f)
print("Model loaded successfully!")

# ----------------------------
# Load Embeddings from .npz File
# ----------------------------
embedding_file = "face_embeddig_for_8_class.npz"  # Path to your .npz file containing the embeddings
embedding_data = np.load(embedding_file)
encoder=LabelEncoder()

# Assuming that the .npz file contains two arrays: 'X' (the embeddings) and 'y' (the corresponding labels)
X_train = embedding_data['arr_0']  # This would be the stored embeddings
y_train = embedding_data['arr_1']  # These would be the corresponding names/labels
print("Embeddings loaded successfully!")
encoder.fit(y_train)
y_train=encoder.transform(y_train)
print(y_train)

# ---------------------------

def inverse_transform(final_predictions):
    Y_pred_name = []
    for pred in final_predictions:
        if pred == "Unknown":
            Y_pred_name.append("Unknown")
        else:
            Y_pred_name.append(str(encoder.inverse_transform([pred])[0]))
    return Y_pred_name
    # print(Y_pred_name)



# ----------------------------
# Initialize Face Detector and Embedder
# ----------------------------
detector = MTCNN()
embedder = FaceNet()

# ----------------------------
# Define the get_embedding Function
# ----------------------------
def get_embedding(face_img):
    """
    Given a face image (as a NumPy array of shape 160x160x3), convert it to float32,
    expand dimensions, and compute the 512D embedding using the FaceNet embedder.
    """
    face_img = face_img.astype('float32')
    face_img = np.expand_dims(face_img, axis=0)  # Shape becomes (1, 160, 160, 3)
    yhat = embedder.embeddings(face_img)
    return yhat[0]  # Return the embedding vector (512D)

# ----------------------------
# Prediction Function
# ----------------------------
def predict_person(pil_image):
    """
    Accepts a PIL image, detects faces using MTCNN, and for each face with confidence > 0.95,
    crops and resizes the face to 160x160, obtains its embedding, and uses the classifier model
    to predict the identity. If multiple faces are detected, returns a comma-separated string of predictions.
    """
    # Convert PIL image to a NumPy array (RGB format)
    image_np = np.array(pil_image)
    
    # If the image is not in RGB (e.g. grayscale), convert it
    if image_np.ndim == 2 or (image_np.ndim == 3 and image_np.shape[2] != 3):
        image_np = cv.cvtColor(image_np, cv.COLOR_GRAY2RGB)
    
    # Detect faces in the image
    faces = detector.detect_faces(image_np)
    
    if len(faces) == 0:
        return "No face detected"
    
    test_embeddings = []
    final_predictions = []
    face_boxes=[]
    threshold = 0.80  # Define threshold for classification confidence

    # Loop over detected faces
    for face in faces:
        if face['confidence'] > 0.95:
            x, y, w, h = face['box']
            x, y = abs(x), abs(y)  # Ensure positive coordinates
            face_boxes.append((x,y,w,h))
            # Crop the face region
            face_crop = image_np[y:y+h, x:x+w]
            # Resize the cropped face to 160x160
            face_resized = cv.resize(face_crop, (160, 160))
            # Get the embedding for the face
            embedding = get_embedding(face_resized)
            test_embeddings.append(embedding)
    
    # If no face met the confidence threshold
    if not test_embeddings:
        return "No high-confidence face detected"
    
    # Convert list of embeddings to a NumPy array
    test_embeddings = np.array(test_embeddings)
    
    # Get prediction probabilities and predicted labels from the classifier
    predictions_proba = model.predict_proba(test_embeddings)
    print(predictions_proba)
    predictions = model.predict(test_embeddings)
    print(predictions)
    
    # Apply threshold logic for each face
    for i, probs in enumerate(predictions_proba):
        max_prob = np.max(probs)  # Maximum probability for the face
        if max_prob < threshold:
            final_predictions.append("Unknown")
        else:
            # print(y_train[predictions[i]])
            final_predictions.append(predictions[i])  # Use the label from the embeddings
    print(final_predictions)
    final_predictions=inverse_transform(final_predictions)
    # # Return predictions as a comma-separated string if multiple faces were detected
    # return ", ".join(final_predictions)

    #logic added by Taha Sayyed ----------------------------------
    
    # Draw bounding boxes and labels on the image
    for (x, y, w, h), label in zip(face_boxes, final_predictions):
        cv.rectangle(image_np, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv.putText(image_np, label, (x, y-10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    annotated_image = Image.fromarray(image_np)
    return annotated_image

    #logic added by Taha Sayyed ----------------------------------


