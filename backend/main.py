from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import WebSocket

# Create FastAPI app
app = FastAPI()

# Allow React frontend (Vite runs on 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Home Route (Test Endpoint)
# -------------------------------
@app.get("/")
def home():
    return {"message": "AURA Backend Running Successfully"}

# -------------------------------
# Data Model for Coordinates
# -------------------------------
class Coordinates(BaseModel):
    x: int
    y: int

# -------------------------------
# Manual Mode Endpoint
# -------------------------------
@app.post("/manual-control")
def manual_control(coords: Coordinates):
    x = coords.x
    y = coords.y

    print(f"Received Coordinates → X: {x}, Y: {y}")

    # TODO:
    # Convert pixels to servo angles here
    # Send to hardware (Arduino / ESP32 / etc)

    return {
        "status": "received",
        "x": x,
        "y": y
    }

@app.websocket("/ws/manual")
async def websocket_manual(websocket: WebSocket):
    await websocket.accept()
    print("Manual Mode WebSocket Connected")

    try:
        while True:
            data = await websocket.receive_json()
            x = data.get("x")
            y = data.get("y")

            print(f"WS Received → X: {x}, Y: {y}")

            # TODO:
            # Convert pixels to servo angles
            # Send to hardware here

    except Exception as e:
        print("WebSocket Disconnected")

import cv2
from fastapi.responses import StreamingResponse

camera1 = cv2.VideoCapture(0)
camera2 = cv2.VideoCapture(1)
def generate_frames_cam1():
    while True:
        success, frame = camera1.read()
        if not success:
            break

        frame = cv2.resize(frame, (640, 480))
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video-feed-1")
def video_feed_1():
    return StreamingResponse(
        generate_frames_cam1(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )

def generate_frames_cam2():
    while True:
        success, frame = camera2.read()
        if not success:
            break

        frame = cv2.resize(frame, (640, 480))
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video-feed-2")
def video_feed_2():
    return StreamingResponse(
        generate_frames_cam2(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )
