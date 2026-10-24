import glob
import pickle
import numpy as np
import cv2


def calibrate_camera(images_path="camera_cal/calibration*.jpg", nx=9, ny=6):
    objp = np.zeros((nx * ny, 3), np.float32)
    objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2)

    objpoints = []
    imgpoints = []
    img_size = None

    for fname in glob.glob(images_path):
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_size = gray.shape[::-1]

        found, corners = cv2.findChessboardCorners(gray, (nx, ny), None)
        if found:
            objpoints.append(objp)
            imgpoints.append(corners)

    _, mtx, dist, _, _ = cv2.calibrateCamera(objpoints, imgpoints, img_size, None, None)

    with open("coefficients/calibration.p", "wb") as f:
        pickle.dump({"mtx": mtx, "dist": dist}, f)

    return mtx, dist


if __name__ == "__main__":
    mtx, dist = calibrate_camera()
    img = cv2.imread("camera_cal/calibration1.jpg")
    undist = cv2.undistort(img, mtx, dist, None, mtx)
    cv2.imwrite("output_images/undistort_output.png", np.hstack((img, undist)))