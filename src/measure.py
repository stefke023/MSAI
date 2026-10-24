import numpy as np
import cv2
from threshold import load_calibration, undistort, threshold_binary
from perspective import get_transform_matrices, warp
from lane_finder import fit_polynomial

YM_PER_PIX = 30 / 720
XM_PER_PIX = 3.7 / 640


def curvature_radius(fit, y_eval):
    a = fit[0] * XM_PER_PIX / YM_PER_PIX ** 2
    b = fit[1] * XM_PER_PIX / YM_PER_PIX
    y = y_eval * YM_PER_PIX
    return (1 + (2 * a * y + b) ** 2) ** 1.5 / abs(2 * a)


def vehicle_offset(left_fit, right_fit, width, height):
    y = height - 1
    lane_center = (np.polyval(left_fit, y) + np.polyval(right_fit, y)) / 2
    return (width / 2 - lane_center) * XM_PER_PIX


if __name__ == "__main__":
    mtx, dist = load_calibration()
    M, Minv = get_transform_matrices()

    img = undistort(cv2.imread("test_images/test1.jpg"), mtx, dist)
    binary_warped = warp(threshold_binary(img), M)
    h, w = binary_warped.shape

    left_fit, right_fit, _ = fit_polynomial(binary_warped)
    left_r = curvature_radius(left_fit, h - 1)
    right_r = curvature_radius(right_fit, h - 1)

    print(f"Left radius:  {left_r:.0f} m")
    print(f"Right radius: {right_r:.0f} m")
    print(f"Average:      {(left_r + right_r) / 2:.0f} m")
    print(f"Offset:       {vehicle_offset(left_fit, right_fit, w, h):.2f} m")