# AURA — Autonomous Unified Response Apparatus

AURA is a real-time face-tracking turret system that uses **stereo vision** (two cameras) to calculate the 3D position of a detected face and automatically aim a laser/servo-based turret at it using an Arduino. A **React + Vite** web frontend provides a live control dashboard with three operating modes.

---

## 🗂️ Project Structure

```
AURA/
├── backend/            # FastAPI Python server (vision + Arduino control)
│   ├── main.py
│   ├── requirements.txt
│   └── aura_calibration.pkl   ← generated after running calibration (NOT in repo)
│
├── frontend/           # React + Vite web UI
│   ├── src/
│   │   ├── App.jsx
│   │   └── modes/
│   │       ├── manualmode.jsx
│   │       ├── AssistedMode.jsx
│   │       └── AutomaticMode.jsx
│   └── package.json
│
└── turret/             # Stereo camera calibration scripts
    ├── camera_calib.py         # Run this FIRST to generate calibration data
    ├── generate_3d.py
    └── gg.py
```

---

## 🛠️ Hardware Requirements

| Component | Details |
|---|---|
| 2× USB Cameras | Stereo pair (left = index 1, right = index 2) |
| Arduino | With 2 servo motors (pan + tilt) |
| Servo Motors | Pan servo + Tilt servo |
| Laser Module | Optional, mounted on the turret |
| USB Cable | Arduino → PC (Serial at 115200 baud) |

---

## ⚙️ Prerequisites

- **Python 3.9+**
- **Node.js 18+** and **npm**
- **Arduino IDE** (to flash servo control sketch onto Arduino)
- **Git**

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Yashwanth-69/AURA.git
cd AURA
```

---

### 2. Backend Setup (Python / FastAPI)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

> **Note:** `opencv-contrib-python` is required for `cv2.FaceDetectorYN`. Make sure it is listed in `requirements.txt`.

---

### 3. Download the ONNX Face Detection Model

The model file `face_detection_yunet_2023mar.onnx` is **not included in the repo** (binary file).

Download it from the official OpenCV Zoo:

```
https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet
```

Place the downloaded file in **both**:
- `backend/face_detection_yunet_2023mar.onnx`
- `turret/face_detection_yunet_2023mar.onnx`

---

### 4. Run Stereo Camera Calibration (ONE-TIME SETUP)

Before the turret can track in 3D, you must calibrate your stereo camera pair.

```bash
cd turret
python camera_calib.py
```

- Follow the on-screen prompts (uses a checkerboard pattern).
- This generates `aura_calibration.pkl` — **copy it to both** `backend/` and `turret/`.

```
turret/aura_calibration.pkl  →  copy to  →  backend/aura_calibration.pkl
```

> ⚠️ Without this file, the backend will crash on startup. You must run calibration once per camera setup.

---

### 5. Arduino Setup

1. Open Arduino IDE and flash the servo control sketch to your Arduino.
2. Connect the Arduino via USB.
3. Check which COM port it is assigned to (e.g., `COM8`).
4. If it's not `COM8`, open `backend/main.py` and change this line:

```python
ser = serial.Serial(
    port='COM8',   # ← Change to your Arduino's COM port
    baudrate=115200,
    ...
)
```

---

### 6. Frontend Setup (React + Vite)

```bash
cd frontend
npm install
```

---

## ▶️ Running the Project

You need **two terminals** running simultaneously.

### Terminal 1 — Backend Server

```bash
cd backend
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

uvicorn main:app --reload --port 8000
```

The API will be live at: `http://localhost:8000`

### Terminal 2 — Frontend Dev Server

```bash
cd frontend
npm run dev
```

The UI will be live at: `http://localhost:5173`

Open your browser and go to **http://localhost:5173**.

---

## 🎮 Operating Modes

| Mode | Description |
|---|---|
| **Manual** | Click anywhere on the camera feed to point the turret at that pixel location |
| **Automatic** | Stereo vision detects a face in both cameras, calculates 3D coordinates, and automatically drives servos to track it |
| **Assisted** | Semi-automatic with manual override capability |

---

## 🔌 API Endpoints (Backend)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/video-feed-1` | MJPEG stream from Left camera |
| `GET` | `/video-feed-2` | MJPEG stream from Right camera |
| `POST` | `/manual-control` | Send `{x, y}` pixel coords to servos |
| `WS` | `/ws/manual` | WebSocket for low-latency manual control |
| `POST` | `/start-automatic` | Begin stereo face tracking loop |
| `POST` | `/stop-automatic` | Stop automatic tracking |
| `GET` | `/Z_D` | Get current depth (Z) of tracked face in mm |

---

## 🗒️ Notes & Troubleshooting

- **Camera index mismatch**: If cameras appear swapped, change `cv2.VideoCapture(1)` / `cv2.VideoCapture(2)` in `main.py` to the correct indices for your system.
- **Arduino not found**: Run `mode` (Windows) or `ls /dev/tty*` (Linux/macOS) to find the correct COM port.
- **Calibration file missing**: Re-run `turret/camera_calib.py` and copy the output `.pkl` to `backend/`.
- **CORS errors**: The backend allows only `http://localhost:5173`. Do not change the default Vite port.

---

## 📦 Dependencies Summary

**Backend (`requirements.txt`)**
- `fastapi`
- `uvicorn`
- `pyserial`
- `opencv-contrib-python`
- `numpy`

**Frontend**
- React 19
- Vite 7

---

## 📄 License

This project is for educational and research purposes.
