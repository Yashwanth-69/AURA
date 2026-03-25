#!/usr/bin/env python

import cv2
import numpy as np
import os
import glob
import math


def cam_fov_calib():
    cam_matrices = []
    for dir in ['./turret/fov_calc_images/left', './turret/fov_calc_images/right']:
        if not os.path.exists(dir):
            print(f"Directory '{dir}' not found. Please run pairwise_calib() first to capture images.")
            return None, None, None
    # Defining the dimensions of checkerboard
        CHECKERBOARD = (6,9)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Creating vector to store vectors of 3D points for each checkerboard image
        objpoints = []
        # Creating vector to store vectors of 2D points for each checkerboard image
        imgpoints = [] 


        # Defining the world coordinates for 3D points
        objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
        objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
        prev_img_shape = None

        # Extracting path of individual image stored in a given directory

        images = glob.glob(dir + '/*.jpg')
        for fname in images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            # Find the chess board corners
            # If desired number of corners are found in the image then ret = true
            ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+
                cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
            
            """
            If desired number of corner are detected,
            we refine the pixel coordinates and display 
            them on the images of checker board
            """
            if ret == True:
                objpoints.append(objp)
                # refining pixel coordinates for given 2d points.
                corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
                
                imgpoints.append(corners2)

                # Draw and display the corners
                img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2,ret)
            
            
        

        h,w = img.shape[:2]

        """
        Performing camera calibration by 
        passing the value of known 3D points (objpoints)
        and corresponding pixel coordinates of the 
        detected corners (imgpoints)
        """
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

        print("Camera matrix : \n")
        print(mtx)
        print("dist : \n")
        print(dist)
        print("rvecs : \n")
        print(rvecs)
        print("tvecs : \n")
        print(tvecs)


        # --- FOV Calculation ---

        # Extract focal lengths in pixels from the camera matrix
        fx = mtx[0, 0]
        fy = mtx[1, 1]

        # You already have h and w from your code: h, w = img.shape[:2]

        # Calculate Horizontal FOV
        hfov_rad = 2 * math.atan(w / (2 * fx))
        hfov_deg = math.degrees(hfov_rad)

        # Calculate Vertical FOV
        vfov_rad = 2 * math.atan(h / (2 * fy))
        vfov_deg = math.degrees(vfov_rad)

        # Calculate Diagonal FOV (using Pythagoras for the diagonal resolution)
        diag_pixel = math.sqrt(w**2 + h**2)
        dfov_rad = 2 * math.atan(diag_pixel / (2 * fx)) # Assuming square pixels, fx is used
        dfov_deg = math.degrees(dfov_rad)

        print("-" * 30)
        print(f"Resolution: {w}x{h}")
        print(f"Horizontal FOV: {hfov_deg:.2f}°")
        print(f"Vertical FOV: {vfov_deg:.2f}°")
        print(f"Diagonal FOV: {dfov_deg:.2f}°")
        print("-" * 30)

        cam_matrices.append([mtx,hfov_deg,vfov_deg,dfov_deg,dist])

    return cam_matrices[0], cam_matrices[1]




def single_cam_capture(cam_index, side_name):
    cap = cv2.VideoCapture(cam_index)
    path = f'./turret/fov_calc_images/{side_name}'
    
    if not os.path.exists(path):
        os.makedirs(path)

    print(f"\n--- CALIBRATING {side_name.upper()} CAMERA ---")
    print("Goal: Get close-ups, tilts, and corners. Press 'S' to save, 'Q' to finish.")
    
    count = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        cv2.putText(frame, f"Saved: {count}", (10, 30), 1, 1, (0, 255, 0), 2)
        cv2.imshow(f'Calibrate {side_name}', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            cv2.imwrite(f'{path}/img_{count}.jpg', frame)
            print(f"Saved {side_name} {count}")
            count += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def pairwise_calib():

    import cv2
    import os

    # Create directories to save the images if they don't exist
    if not os.path.exists('./turret/distance_calc_images/left'): 
        print("Creating directory for left camera images...")
        os.makedirs('./turret/distance_calc_images/left')
    if not os.path.exists('./turret/distance_calc_images/right'): 
        print("Creating directory for right camera images...")
        os.makedirs('./turret/distance_calc_images/right')

    # Initialize two cameras (0 is usually the internal webcam, 1 & 2 are external)
    cam_left = cv2.VideoCapture(1)
    cam_right = cv2.VideoCapture(2)

    # Set resolution (optional, must be the same for both)
    # cam_left.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cam_left.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    count = 0
    print("Press 'S' to save a pair, 'Q' to quit.")

    while True:
        # Grab frames from both cameras
        retL, frameL = cam_left.read()
        retR, frameR = cam_right.read()

        if not retL or not retR:
            print("Error: Could not read from one or both cameras.")
            break

        # Concatenate images horizontally for a side-by-side preview
        preview = cv2.hconcat([frameL, frameR])
        cv2.imshow('Stereo Calibration Capture', preview)

        key = cv2.waitKey(1) & 0xFF
        
        # Save images on 'S' key
        if key == ord('s'):
            cv2.imwrite(f'./turret/distance_calc_images/left/image_{count}.jpg', frameL)
            cv2.imwrite(f'./turret/distance_calc_images/right/image_{count}.jpg', frameR)
            print(f"Saved pair {count}")
            count += 1

        # Exit on 'Q' key
        elif key == ord('q'):
            break

    # Release resources
    cam_left.release()
    cam_right.release()
    cv2.destroyAllWindows()






def baseline_calib():
    import cv2
    import numpy as np
    import glob


    # SETTINGS
    CHECKERBOARD = (6, 9)
    SQUARE_SIZE = 23.5  # Set this to your square size in mm (e.g., 25mm)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Coordinates of 3D points in real world space (using mm)
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE




    objpoints = [] # 3d points in real world space
    imgpointsL = [] # 2d points in image plane for left camera
    imgpointsR = [] # 2d points in image plane for right camera

    images_left = sorted(glob.glob('distance_calc_images\left\*.jpg'))
    images_right = sorted(glob.glob('distance_calc_images\/right\*.jpg'))

    print(f"Found {len(images_left)} left images and {len(images_right)} right images for calibration.")



    for imgL_path, imgR_path in zip(images_left, images_right):
        imgL = cv2.imread(imgL_path)
        imgR = cv2.imread(imgR_path)
        grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
        grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

        retL, cornersL = cv2.findChessboardCorners(grayL, CHECKERBOARD, None)
        retR, cornersR = cv2.findChessboardCorners(grayR, CHECKERBOARD, None)

        if retL and retR:
            objpoints.append(objp)
            cornersL2 = cv2.cornerSubPix(grayL, cornersL, (11, 11), (-1, -1), criteria)
            imgpointsL.append(cornersL2)
            cornersR2 = cv2.cornerSubPix(grayR, cornersR, (11, 11), (-1, -1), criteria)
            imgpointsR.append(cornersR2)

    # 1. Calibrate cameras individually first
    retL, mtxL, distL, rvecsL, tvecsL = cv2.calibrateCamera(objpoints, imgpointsL, grayL.shape[::-1], None, None)
    retR, mtxR, distR, rvecsR, tvecsR = cv2.calibrateCamera(objpoints, imgpointsR, grayR.shape[::-1], None, None)

    # 2. Stereo Calibration
    flags = cv2.CALIB_FIX_INTRINSIC # Use the mtx and dist we just calculated
    ret, mtxL, distL, mtxR, distR, R, T, E, F = cv2.stereoCalibrate(
        objpoints, imgpointsL, imgpointsR,
        mtxL, distL, mtxR, distR,
        grayL.shape[::-1], criteria=criteria, flags=flags)

    # 3. Calculate the distance (Baseline)
    # T is the vector from the Left camera center to the Right camera center
    distance = np.linalg.norm(T)

    print(f"\n--- Stereo Results ---")
    print(f"Translation Vector T (x, y, z) in mm:\n{T}")
    print(f"Total Distance (Baseline): {distance:.2f} mm")
    print(f"Horizontal Offset (X): {abs(T[0][0]):.2f} mm")

    return [T[0][0], ret, mtxL, distL, mtxR, distR, R, T, E, F]






