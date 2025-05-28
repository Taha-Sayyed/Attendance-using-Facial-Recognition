# Attendance-using-Facial-Recognition

# 🧠 Smart Attendance System 🎥📋

This project proposes a **smart attendance system** that marks attendance in **one shot** using **live video**.  
Users can effortlessly **create**, **train**, and **test** datasets using an intuitive interface. 🚀

- The software processes **live video** to detect faces using the advanced face detection technique:  
  **Multi-Task Cascade Convolutional Neural Network (MTCNN)** 🧑‍💻

- The **FaceNet** module is then used to recognize the detected faces with high accuracy. 🧠✨

- Attendance for all recognized students is **automatically marked** and stored in a spreadsheet. 📑✅

---

✅ Say goodbye to manual errors and delays—this system ensures **seamless**, **accurate**, and **efficient** attendance management.

## 🚀 Approach

The proposed end-to-end attendance system consists of three main components:  
**📁 Dataset Creation & Training**, **🧠 Face Recognition**, and **📋 Attendance Manipulation**.

---

### 1. 📁 Dataset Creation & Training

- The user records a **5–10 second video** of each student and saves them with respective names in a dataset folder.
- The software processes each video by:
  - 🎞️ Segmenting it into frames.
  - 🖼️ Padding and resizing the frames.
  - 🧑‍💻 Detecting faces using **MTCNN**, cropping them, and performing **data augmentation**:
    - Flipping, blurring, adding noise (Gaussian, salt & pepper), brightness shifting, etc.
  - 🗂️ Saving the processed **160×160** face images in corresponding folders.
- The software allows splitting the dataset into **training and testing sets**.
- **FaceNet** with **Inception ResNetV1** (pre-trained on **VGGFace2**) is re-trained until accuracy exceeds **99%**.
- ✅ The trained model is saved for future recognition tasks.

---

### 2. 🧠 Face Recognition

- Input video is segmented into frames and passed through **MTCNN** to detect face bounding boxes.
- Detected faces are:
  - Cropped 🖼️
  - Resized 📏
  - Passed to the trained **FaceNet classifier**
- FaceNet outputs **confidence scores**, and the highest scoring class (student name) is assigned.
- 🎯 All frames are processed in sequence, and recognized names are stored in a list.

---

### 3. 📋 Attendance Manipulation

- The attendance manipulator extracts **unique names** from the recognition list.
- Loads the **subject-wise attendance sheet** 🗃️
- Appends a new column for the **current date** 🗓️
- ✅ Marks attendance for all recognized students automatically.

---
