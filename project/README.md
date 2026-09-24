# Smart Classroom & Student Engagement AI Suite (Kaggle Dataset Edition)

A full-stack artificial intelligence application integrating **Computer Vision (Kaggle 8-class student behavior detection & live webcam)**, **Machine Learning (Decision Trees & Regression)**, **Natural Language Processing (TextBlob & NLTK)**, a **SQLite Database**, a **FastAPI REST Backend**, and an **Ultra-Modern Glassmorphic Web Dashboard**.

---

## 📌 Architecture Overview

```
                      +------------------------------------+
                      |    Ultra Modern Glassmorphic UI    |
                      |  (HTML5 / Vanilla CSS / JavaScript)|
                      +-----------------+------------------+
                                        |  HTTP / REST / Base64 frames
                                        v
                      +------------------------------------+
                      |       FastAPI Backend Server       |
                      |        [project/server.py]         |
                      +----+-------------+--------------+--+
                           |             |              |
         +-----------------+             |              +-----------------+
         v                               v                                v
+-------------------+          +-------------------+            +-------------------+
|  Computer Vision  |          | Machine Learning  |            |   NLP Sentiment   |
| Kaggle 8-Class Det|          | Decision Tree/Reg |            | TextBlob Polarity |
| 90.97% Classifier |          |  K-Means Personas |            |  NLTK WordCloud   |
|  Live Headcount   |          | Outcome Predictor |            | Theme Extraction  |
+-------------------+          +-------------------+            +-------------------+
         |                               |                                |
         +-------------------------------+--------------------------------+
                                         |
                                         v
                      +------------------------------------+
                      |          SQLite Database           |
                      |  [project/database/classroom.db]   |
                      | - students (60+ records)           |
                      | - attendance_sessions              |
                      | - classroom_behavior_logs          |
                      | - feedback                         |
                      | - prediction_logs                  |
                      +------------------------------------+
```

---

## 🧠 Kaggle Dataset Analysis & Model Training

### 1. Dataset Overview (`project/DATASET FROM KAGEL`)
- **Total Images:** 8,884 classroom images (7,995 train, 889 val)
- **Total Bounding Boxes:** 267,888 annotated instances
- **8 Classroom Action Classes:**
  1. `handrise` (27.1%) - Active participation & questioning
  2. `look_forward` (22.0%) - Attentive listening
  3. `read` (43.8%) - Reading course material
  4. `sleep` (2.0%) - Drowsiness / Inattention alert ⚠️
  5. `stand` (1.6%) - Answering / Standing up
  6. `turn_head` (1.5%) - Looking away / Distracted
  7. `using_device` (1.7%) - Mobile phone / Device alert 🚨
  8. `write` (0.3%) - Taking notes

### 2. Trained Models
- **Kaggle Action Classifier (`models/classroom_action_classifier.joblib`):**
  - Architecture: Multi-scale spatial gradient & color feature extraction + ExtraTrees Ensemble
  - Test Accuracy: **90.97%**
  - Latency: <1ms inference per student
- **Fine-Tuned YOLOv8 (`models/classroom_behavior_yolov8.pt`):**
  - Transfer learning on Kaggle classroom images
  - Output: 8-class bounding box regression & action localization
- **Two-Stage Vision Suite:** Combines YOLOv8 person detector + Kaggle Action Classifier for maximum recall and accurate behavior classification.

---

## 🌟 Key Application Capabilities

### 1. 📷 Real-Time Vision & Kaggle Behavior Analysis
- **Live Webcam Stream:** Direct camera capture with real-time bounding boxes drawn on canvas with neon corners.
- **8 Live Behavior Chips:** Real-time counters for Attentive, Hand Raised, Reading, Writing, Standing, Turned Head, Sleeping, and Using Device.
- **Classroom Engagement Index:** Real-time percentage (0-100%) dynamically scoring overall classroom attentiveness.
- **Safety & Inattention Alerts:** Immediate pulsing banner triggers when sleeping or unauthorized device usage is detected.
- **Kaggle Benchmark Gallery:** Clickable carousel of real Kaggle dataset scenes to test the trained model with 1 click.
- **Photo Upload:** Drag-and-drop or upload any classroom photo for instant analysis.

### 2. ⚡ Machine Learning Outcome Predictor
- **Interactive Multi-Parameter Sliders:** Weekly Study Hours, Attendance %, Assignments Completed.
- **Dual Inference:** Evaluates Decision Tree (Pass/Fail) and Linear Regression (Exam Score).
- **Dynamic Circular SVG Gauge:** Pass probability animation with color transitions.
- **K-Means Behavioral Clustering:** Maps student to *High Achiever*, *Consistent Performer*, or *Needs Support*.
- **Database Audit:** Automatically logs predictions to SQLite `prediction_logs`.

### 3. 💬 Real-Time NLP Sentiment Engine
- **Live Typing Meter:** Analyzes polarity and subjectivity dynamically as feedback is typed.
- **Sentiment Classification:** Positive, Neutral, Negative tags.
- **Dynamic NLTK WordCloud:** Generated on-demand via `GET /api/feedback/wordcloud`.

### 4. 🗄️ SQLite Classroom Student Directory
- **Persistent Records:** 60 pre-seeded cleaned records in `classroom.db`.
- **Search & Filters:** Search by name/ID, filter by risk level and outcome.
- **Modal Add Student:** Insert records with automated scoring.
- **"Predict ML" Action:** Instantly loads a student's attributes into the predictor tab.

---

## 🚀 How to Run the Application

### 1. Launch the Web Application (Recommended)
The server is already running, or you can start it manually:
```bash
cd "c:\Users\Shashwat Bhatt\Desktop\bootcamp\project"
..\.venv\Scripts\python.exe server.py
```
Open your browser at:
👉 **[http://localhost:8000](http://localhost:8000)**

### 2. Run the Complete Automated Pipeline
```bash
..\.venv\Scripts\python.exe project/main.py
```

### 3. Desktop Webcam Feed
```bash
..\.venv\Scripts\python.exe project/main.py --webcam
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /` | `GET` | Serves the web application (`index.html`) |
| `GET /api/stats` | `GET` | Aggregated classroom KPIs, pass rate, and average engagement |
| `GET /api/dataset/sample-images` | `GET` | Returns list of test scenes from the Kaggle dataset |
| `GET /api/dataset/image/{file}` | `GET` | Serves a sample classroom image from Kaggle dataset |
| `POST /api/dataset/analyze-sample`| `POST` | Evaluates a Kaggle dataset image with the trained model |
| `POST /api/vision/analyze-frame` | `POST` | Evaluates base64 webcam frame for headcount & 8 behaviors |
| `GET /api/behavior/stats` | `GET` | Aggregated counts of all 8 behaviors from past sessions |
| `GET /api/attendance/sessions` | `GET` | Retrieves logged attendance & engagement ledger |
| `GET /api/students` | `GET` | Retrieves student database records with search/filters |
| `POST /api/students` | `POST` | Adds a new student record to SQLite |
| `POST /api/predict` | `POST` | Runs ML inference and logs prediction |
| `POST /api/feedback/submit` | `POST` | Runs NLP sentiment and logs feedback |
| `GET /api/feedback/wordcloud` | `GET` | Dynamically streams PNG word cloud |
