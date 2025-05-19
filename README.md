# Sign Language Recognition Backend

This is a FastAPI-based backend service for real-time sign language recognition using LSTM neural networks. The service processes keypoints data from MediaPipe and predicts sign language gestures.

## Features

- Real-time sign language recognition using WebSocket
- LSTM-based neural network model
- Support for 12 different sign language gestures
- Confidence-based prediction system
- Sentence formation from recognized gestures

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

- WebSocket endpoint: `/ws/predict`
  - Accepts keypoints data in JSON format
  - Returns predictions and confidence scores

## Supported Gestures

- nice
- thankyou
- meet
- fine
- how
- what
- cool
- name
- hello
- you
- me
- your
# mediapipe-client
