import os
import numpy as np
import cv2
from threshold import load_calibration, undistort

SRC = np.float32([[585, 460], [203, 720], [1127, 720], [695, 460]])
SRC_540P = np.float32([[567, 460], [208, 720], [1134, 720], [727, 460]])
DST = np.float32([[320, 0], [320, 720], [960, 720], [960, 0]])


def get_transform_matrices(src=SRC):
    M = cv2.getPerspectiveTransform(src, DST)
    Minv = cv2.getPerspectiveTransform(DST, src)
    return M, Minv


def warp(img, M):
    h, w = img.shape[:2]
    return cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)


if __name__ == "__main__":
    os.makedirs("output_images", exist_ok=True)
    mtx, dist = load_calibration()
    M, Minv = get_transform_matrices()

    img = undistort(cv2.imread("test_images/straight_lines1.jpg"), mtx, dist)
    warped = warp(img, M)

    cv2.polylines(img, [SRC.astype(np.int32)], True, (0, 0, 255), 3)
    cv2.polylines(warped, [DST.astype(np.int32)], True, (0, 0, 255), 3)
    cv2.imwrite("output_images/warped_straight_lines.jpg", np.hstack((img, warped)))