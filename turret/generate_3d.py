
import cv2 as cv
import numpy as np
import serial
import time
import pickle
import os   
from collections import deque
import math


def handle_calibration():
    # 1. Get the absolute path to the backend folder
    base_path = os.path.dirname(os.path.abspath(__file__))

    pkl_path = os.path.join(base_path, 'aura_calibration.pkl')
    
    print(f"--- Starting Calibration Process ---")
    print(f"Target path: {pkl_path}")

    # 2. Check if the file exists at the ABSOLUTE path
    if os.path.exists(pkl_path):
        print(f"--- Loading Saved Calibration from {pkl_path} ---")
        with open(pkl_path, 'rb') as f: # Use pkl_path here, NOT filename
            return pickle.load(f)
    else:
        # 3. Handle the missing file case
        print(f"CRITICAL ERROR: Calibration file not found at {pkl_path}")
        # You should either return a default value or raise an error
        return None 

 

# Get your data (either from file OR by running calibration)
data = handle_calibration()

print("Stereo Calibration Data:", data["stereo"])
print("FOV Calibration Data:", data["fov"])


arduino = serial.Serial(port='COM8', baudrate=115200, timeout=0.1)
time.sleep(2)

pan_off = 5
tilt_off = 6
# History buffer: Increase 'maxlen' for smoother (but slower) movement
# 5 is a good balance for 30fps. 10 is very smooth but feels "heavy".
history = deque(maxlen=5)

def get_smoothed_coords(new_x, new_y, new_z):
    history.append((new_x, new_y, new_z))
    
    # Calculate the average of each axis
    avg_x = sum(p[0] for p in history) / len(history)
    avg_y = sum(p[1] for p in history) / len(history)
    avg_z = sum(p[2] for p in history) / len(history)
    
    return avg_x, avg_y, avg_z

def calculate_laser_angles(x, y, z, status  = 0):
    # 1. PAN SERVO (Offset: 5.2, 0, 7.5)
    # Moving in X-Z plane
    dx_pan = x - 5.2
    
    dz_pan = abs(z) - 7.5
    pan_rad = math.atan2(dx_pan, dz_pan)
    pan_deg = math.degrees(pan_rad)

    # 2. TILT SERVO (Offset: 8.4, 5.5, 6.1)
    # Moving in Y-Z plane
    dy_tilt = y - 5.5
    dz_tilt = abs(z) - 6.1
    # We use the horizontal distance from the tilt pivot to the target
    dist_to_target = math.sqrt(dx_pan**2 + dz_pan**2) 
    
    tilt_rad = math.atan2(dy_tilt, dz_tilt)
    tilt_deg = math.degrees(tilt_rad)

    final_pan = pan_deg
    final_tilt = tilt_deg

    
    data = f"{pan_off+90+final_pan:.0f} {tilt_off+90+final_tilt:.0f}\n"

    print(f" Sent to Arduino: {data.strip()}")
    arduino.write(data.encode('utf-8'))

    return pan_deg, tilt_deg

# Example: Camera sees object at 1 meter (1000mm)
# target_x, target_y, target_z = 0, 0, 1000 
# p, t = calculate_laser_angles(target_x, target_y, target_z)


def get_3d_coordinates_1(uL, vL, uR, vR, mtxL,mtxR, baseline):
    """
    Calculates 3D coordinates relative to the Left Camera center.
    
    uL, vL   : Center of face in Left Image (pixels)
    uR, vR   : Center of face in Right Image (pixels)
    mtxL     : The 3x3 Camera Matrix for the Left camera
    baseline : The distance (D) between cameras in mm
    """
    mtxL = np.array(mtxL)
    # 1. Extract parameters from the Left Camera Matrix
    fx = mtxL[0, 0]
    fy = mtxL[1, 1]
    cxL = mtxL[0, 2]
    cyR = mtxL[1, 2]
    cxR = mtxR[0, 2]
    cyR = mtxR[1, 2]

    # 2. Calculate Disparity (d)
    # The horizontal shift of the face between left and right images
    disparity = abs((uL-cxL) - (uR-cxR)) # Ensure it's positive, as disparity is a magnitude
    # print(f"Disparity (pixels): {disparity}")

    # Validation: Disparity must be positive for objects in front of the camera
    if disparity <= 0:
        print("Error: Disparity is zero or negative. Object is too far or detection is wrong.")
        return None

    # 3. Calculate Depth (Z) - This is the distance from the camera plane
    Z = (fx * baseline) / disparity

    # 4. Calculate Horizontal (X) and Vertical (Y) coordinates
    # We use the Left camera's pixel coordinates as the reference
    X = (uL - cx) * Z / fx
    Y = (vL - cy) * Z / fy

    

    return np.array([X, Y, Z])



# --- EXAMPLE DATA ---
# mtxL = np.array([[600, 0, 320], [0, 600, 240], [0, 0, 1]]) # Example Matrix
# D = 60.0 # 60mm baseline
# face_left = (400, 200) # uL, vL
# face_right = (350, 200) # uR, vR

# result = get_3d_coordinates(face_left[0], face_left[1], face_right[0], face_right[1], mtxL, D)
# print(f"3D Position (mm): X={result[0]:.1f}, Y={result[1]:.1f}, Z={result[2]:.1f}")

mtxL,mtxR = data["stereo"][2], data["stereo"][4]
cx = mtxL[0, 2]
cy = mtxL[1, 2]
fovL = data["fov"][0][1:4]
fovR = data["fov"][1][1:4]


D = data["stereo"][0]
# face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
capture1 = cv.VideoCapture(1)
capture2 = cv.VideoCapture(2)

face_detector = cv.FaceDetectorYN.create(
    model='turret/face_detection_yunet_2023mar.onnx',
    config='', 
    input_size=(320, 320), # Initial size, will be updated per frame
    score_threshold=0.8,   # Confidence threshold (0.0 - 1.0)
    nms_threshold=0.3,     # Non-maximum suppression (removes overlapping boxes)
    top_k=5000
)


face1_found = False
face2_found = False

while True:
    ret1, frame1 = capture1.read()
    ret2, frame2 = capture2.read()


    frame1_position = (0, 0)
    frame2_position = (0, 0)


    h, w, _ = frame1.shape
    origin_x, origin_y = cx, cy
    
    # Draw X-axis (Red) - Horizontal line
    cv.line(frame1, (0, int(origin_y)), (640, int(origin_y)), 
                    (0, 0, 255), 1)
    
    
    cv.line(frame1, (int(origin_x), 0), (int(origin_x), 480), 
                    (0, 0, 255), 1)
    
    face_detector.setInputSize((w, h))
    _, faces = face_detector.detect(frame1)
    center1 = (0, 0)
    # 3. Draw Detections
    if faces is not None:
        face1_found = True
        for face in faces:
            # Box coordinates: x, y, width, height
            box1 = face[0:4].astype(np.int32)
            center1 = (box1[0] + box1[2]//2, box1[1] + box1[3]//2)
            frame1_position = center1
            #point center
            cv.circle(frame1, center1, 5, (0,255, 0), -1)
            
            # Draw rectangle
            cv.rectangle(frame1, (box1[0], box1[1]), (box1[0]+box1[2], box1[1]+box1[3]), (0, 255, 0), 2)
            

            face_at_x = abs(320-center1[0])
            face_at_y = abs(240-center1[1])

    else:
        face1_found = False    

    h, w, _ = frame2.shape
    origin_x, origin_y = w // 2, h // 2

    cv.line(frame2, (0, origin_y), (640, origin_y), 
                    (0, 0, 255), 1)
    
    
    cv.line(frame2, (origin_x, 0), (origin_x, 480), 
                    (0, 0, 255), 1)
    face_detector.setInputSize((w, h))
    _, faces = face_detector.detect(frame2)

    center2 = (0, 0)
    if faces is not None:
        face2_found = True
        for face in faces:
            # Box coordinates: x, y, width, height
            box2 = face[0:4].astype(np.int32)
            
            center2 = (box2[0] + box2[2]//2, box2[1] + box2[3]//2)
            frame1_position = center2
            cv.circle(frame2, center2, 5, (0, 255, 0), -1)
            # Draw rectangle
            cv.rectangle(frame2, (box2[0], box2[1]), (box2[0]+box2[2], box2[1]+box2[3]), (0, 255, 0), 2)
            
    
    else:
        face2_found = False
    
    if not ret1 or not ret2:
        print("Failed to grab frames")
        break

    status = 0
    if face1_found and face2_found:
        status = 1
    

    

    final_coordinates = get_3d_coordinates_1(center1[0], center1[1], center2[0], center2[1], mtxL,mtxR, D)
    xx,yy,zz = get_smoothed_coords(int(final_coordinates[0]), int(final_coordinates[1]), int(final_coordinates[2]))
    final_angles = calculate_laser_angles(xx,yy,zz,status)
    



    combined_frame = np.hstack((frame1, frame2))

    cv.imshow('Dual Camera Stream', combined_frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

frame_width = int(capture1.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(capture1.get(cv.CAP_PROP_FRAME_HEIGHT))
print(f"Frame width: {frame_width} pixels and frame height: {frame_height} pixels")
capture1.release()
capture2.release()
cv.destroyAllWindows()







