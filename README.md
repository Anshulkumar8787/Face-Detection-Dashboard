---
title: Face Detection AI
emoji: 👤
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 👤 Face Detection AI

A Flask web app that detects human faces in a photo (upload or webcam) and draws a box around each one, using OpenCV's YuNet deep-learning face detector (with a Haar Cascade fallback).

## ⚠️ Required setup step: download the AI model

This app uses a small (~230 KB) deep-learning model called **YuNet** for accurate face detection. It is not included in this zip because it's a binary file — download it once:

1. Download this file: https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
2. Place it inside this project at: `models/face_detection_yunet_2023mar.onnx`
   (the `models` folder already exists in this zip — just drop the file in)
3. Run the app. If the file is missing, the app still works using an older, less accurate method (Haar Cascade) as a fallback — but for the best accuracy, always include this file.

When deploying to Render, make sure this file is committed to your GitHub repo (it's small enough to commit directly — no need to .gitignore it).

## 🌐 Live Demo
(add your Render link here after deploying)

## 📂 GitHub Repository
(add your GitHub link here)

## 🚀 Features
- Upload a photo (drag & drop or browse) OR capture one live with your webcam
- Detects every face using a real deep-learning model (YuNet), with confidence scores
- Shows Original vs Detected side-by-side
- Detection History (CSV-based)
- Clear History

## 🛠 Tech Stack
- Python, Flask
- OpenCV (YuNet deep-learning face detector + Haar Cascade fallback)
- HTML, CSS, JavaScript (webcam capture via getUserMedia)

## Project Structure
```
Face-Detection-App/
│── app.py
│── detector.py
│── requirements.txt
│── Procfile
├── models/
│   └── face_detection_yunet_2023mar.onnx   (you download this)
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
├── uploads/
└── history/
    └── history.csv
```

## Installation

```bash
git clone <your-repo-url>
cd Face-Detection-App
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```
Then download the model file (see setup step above) into `models/`, and run:
```bash
python app.py
```

Open http://127.0.0.1:5000

## Author
Anshul Kumar
