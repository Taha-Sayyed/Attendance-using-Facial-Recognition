# SIES GST Attendance System

A face recognition-based attendance system built for SIES Graduate School of Technology. This application uses Firebase for authentication and data storage, and TensorFlow for face recognition.

## Project Structure

The project has been organized into a modular structure for better maintainability:

```
Project/
│
├── main.py                  # Main application entry point
├── config.py                # Configuration and initialization
├── utils.py                 # Utility functions
├── auth.py                  # Authentication functions
├── attendance.py            # Attendance recording and retrieval
├── face_recognition.py      # Face detection and recognition
├── video_transform.py       # Video processing for webcam
│
├── pages/                   # UI pages
│   ├── __init__.py
│   ├── main_page.py         # Landing page
│   ├── register_page.py     # Registration page
│   ├── login_page.py        # Login page
│   └── home_page.py         # Home page with attendance functionality
│
├── requirements.txt         # Project dependencies
├── SIESLOGO.PNG             # Logo image
├── best_model.pkl           # Pre-trained classification model
└── face_embeddig_for_12_class.npz  # Face embeddings for recognition
```

## Setup Instructions

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Firebase Setup**

   - Ensure you have `techfusion-firestore-key.json` in the parent directory
   - Create a `.env` file in the parent directory with your Firebase API key:
     ```
     API_KEY=your_firebase_api_key
     ```

3. **Model Files**

   - Make sure `best_model.pkl` and `face_embeddig_for_12_class.npz` are in the Project directory
   - If using FaceNet, ensure `facenet_keras.h5` is available

## Running the Application

Navigate to the Project directory and run:

```bash
streamlit run main.py
```

## Features

- **User Registration**: Students can register with their details and profile image
- **Face Recognition**: Webcam-based face detection and recognition for attendance
- **Attendance Tracking**: Record and view attendance history
- **Data Export**: Download attendance records as CSV

## Troubleshooting

- **Firebase Index Error**: If you encounter index errors when retrieving attendance records, follow the instructions in the application to create a composite index in the Firebase console.
- **Model Loading Issues**: Ensure all model files are in the correct directory and have the correct names.

## Development

- **Adding New Pages**: Create a new module in the `pages/` directory and add it to the routing in `main.py`
- **Modifying Recognition**: Update the `face_recognition.py` file to adjust the face detection and recognition logic

## Contributors

- **Taha Sayyed**: Original developer
- **SIES GST**: Project sponsor

## License

This project is proprietary and owned by SIES Graduate School of Technology. 