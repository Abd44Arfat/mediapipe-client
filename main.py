from fastapi import FastAPI, WebSocket
import numpy as np
import tensorflow as tf
import uvicorn
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# Load LSTM model
model = tf.keras.models.load_model("LSTM_model.h5")

# Constants
SEQUENCE_LENGTH = 30
KEYPOINTS_DIM = 126
actions = ["nice", "thankyou", "meet", "fine", "how", "what", "cool", "name", "hello", "you", "me", "your"]

@app.websocket("/ws/predict")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    sequence = []
    sentence = []
    predictions = []

    while True:
        try:
            data = await websocket.receive_json()

            if "keypoints" not in data:
                await websocket.send_json({"error": "keypoints not found in data"})
                continue

            keypoints = np.array(data["keypoints"])

            # تأكد ان ال keypoints بالشكل الصحيح
            if keypoints.shape[0] != KEYPOINTS_DIM:
                await websocket.send_json({"error": f"keypoints length must be {KEYPOINTS_DIM}"})
                continue

            sequence.append(keypoints)
            sequence = sequence[-SEQUENCE_LENGTH:]

            if len(sequence) == SEQUENCE_LENGTH:
                input_seq = np.expand_dims(np.array(sequence), axis=0)
                res = model.predict(input_seq)[0]
                predicted_index = int(np.argmax(res))
                confidence = float(np.max(res))
                action = actions[predicted_index]
                predictions.append(predicted_index)

                # شرط الثبات على نفس التوقع لزيادة الثقة
                if len(predictions) >= 15 and np.unique(predictions[-15:])[0] == predicted_index:
                    if confidence > 0.8:
                        if len(sentence) == 0 or action != sentence[-1]:
                            sentence.append(action)
                            sentence = sentence[-5:]

                await websocket.send_json({
                    "predicted_index": predicted_index,
                    "action": action,
                    "confidence": confidence,
                    "sentence": sentence
                })

        except Exception as e:
            await websocket.send_json({"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
