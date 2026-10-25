import os
import numpy as np
import cv2
from threshold import load_calibration, undistort, threshold_binary
from perspective import get_transform_matrices, warp
from lane_finder import fit_polynomial
from measure import curvature_radius, vehicle_offset


def draw_lane(undist, binary_warped, left_fit, right_fit, Minv, radius, offset):
    h, w = binary_warped.shape
    ploty = np.arange(h)
    left_x = np.polyval(left_fit, ploty)
    right_x = np.polyval(right_fit, ploty)

    lane = np.zeros((h, w, 3), np.uint8)
    left_pts = np.column_stack((left_x, ploty))
    right_pts = np.flipud(np.column_stack((right_x, ploty)))
    cv2.fillPoly(lane, [np.int32(np.vstack((left_pts, right_pts)))], (0, 255, 0))

    unwarped = cv2.warpPerspective(lane, Minv, (undist.shape[1], undist.shape[0]))
    result = cv2.addWeighted(undist, 1, unwarped, 0.3, 0)

    side = "right" if offset > 0 else "left"
    cv2.putText(result, f"Radius of curvature: {radius:.0f} m", (40, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
    cv2.putText(result, f"Vehicle is {abs(offset):.2f} m {side} of center", (40, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
    return result


if __name__ == "__main__":
    os.makedirs("output_images", exist_ok=True)
    mtx, dist = load_calibration()
    M, Minv = get_transform_matrices()

    undist = undistort(cv2.imread("test_images/test1.jpg"), mtx, dist)
    binary_warped = warp(threshold_binary(undist), M)
    h, w = binary_warped.shape

    left_fit, right_fit, _ = fit_polynomial(binary_warped)
    radius = (curvature_radius(left_fit, h - 1) + curvature_radius(right_fit, h - 1)) / 2
    offset = vehicle_offset(left_fit, right_fit, w, h)

    result = draw_lane(undist, binary_warped, left_fit, right_fit, Minv, radius, offset)
    cv2.imwrite("output_images/example_output.jpg", result)