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

def threshold_binary(img, sx_thresh=(20, 100), s_thresh=(170, 255)):
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    l_channel = hls[:, :, 1]
    s_channel = hls[:, :, 2]

    sobelx = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0)
    abs_sobelx = np.absolute(sobelx)
    scaled_sobel = np.uint8(255 * abs_sobelx / np.max(abs_sobelx))

    sx_binary = (scaled_sobel >= sx_thresh[0]) & (scaled_sobel <= sx_thresh[1])
    s_binary = (s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1])

    binary = np.zeros_like(l_channel, dtype=np.uint8)
    binary[sx_binary | s_binary] = 1
    return binary


if __name__ == "__main__":
    os.makedirs("output_images", exist_ok=True)
    mtx, dist = load_calibration()
    img = cv2.imread("test_images/test1.jpg")
    undist = undistort(img, mtx, dist)
    cv2.imwrite("output_images/undistorted_test1.jpg", np.hstack((img, undist)))
    binary = threshold_binary(undist)
    cv2.imwrite("output_images/binary_combo_example.jpg", binary * 255)