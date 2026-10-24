import os
import pickle
import numpy as np
import cv2


def load_calibration(path="coefficients/calibration.p"):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data["mtx"], data["dist"]


def undistort(img, mtx, dist):
    return cv2.undistort(img, mtx, dist, None, mtx)


if __name__ == "__main__":
    os.makedirs("output_images", exist_ok=True)
    mtx, dist = load_calibration()
    img = cv2.imread("test_images/test1.jpg")
    undist = undistort(img, mtx, dist)
    cv2.imwrite("output_images/undistorted_test1.jpg", np.hstack((img, undist)))