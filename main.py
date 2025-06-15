from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse 
import numpy as np
import tensorflow as tf
import uvicorn

app = FastAPI()

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load LSTM model
model = tf.keras.models.load_model("LSTM_model.h5")

# Constants
SEQUENCE_LENGTH = 30
KEYPOINTS_DIM = 126
actions = ["nice", "thankyou", "meet", "fine", "how", "what", "cool", "name", "hello", "you", "me", "your"]

# endpoint to Serve index.html
@app.get("/ai", response_class=HTMLResponse)
async def read_ai_interface():
    """
    Serves the main AI interface page (index.html).
    """
    return FileResponse("static/index.html")

@app.websocket("/ws/predict")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    sequence = []
    sentence = []
    predictions = []
    idle_count = 0

    while True:
        try:
            data = await websocket.receive_json()

            if "keypoints" not in data:
                await websocket.send_json({"error": "keypoints not found in data"})
                continue

            keypoints = np.array(data["keypoints"])

            if keypoints.shape[0] != KEYPOINTS_DIM:
                await websocket.send_json({"error": f"keypoints length must be {KEYPOINTS_DIM}"})
                continue

            sequence.append(keypoints)
            sequence = sequence[-SEQUENCE_LENGTH:]

            if len(sequence) == SEQUENCE_LENGTH:
                input_seq = np.expand_dims(np.array(sequence), axis=0)
                res = model.predict(input_seq, verbose=0)[0]
                predicted_index = int(np.argmax(res))
                confidence = float(np.max(res))
                action = actions[predicted_index]
                predictions.append(predicted_index)

                if confidence < 0.5:
                    idle_count += 1
                else:
                    idle_count = 0

                if idle_count > 20:
                    sentence = []
                    predictions = []
                    idle_count = 0

                if len(predictions) >= 15 and predictions[-15:].count(predicted_index) > 12:
                    if confidence > 0.8:
                        if len(sentence) == 0 or action != sentence[-1]:
                            sentence.append(action)
                            sentence = sentence[-7:]

                readable_sentence = " ".join(sentence)

                await websocket.send_json({
                    "predicted_index": predicted_index,
                    "action": action,
                    "confidence": confidence,
                    "sentence": sentence,
                    "readable_sentence": readable_sentence
                })

        except Exception as e:
            await websocket.send_json({"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)