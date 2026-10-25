import sys
from collections import deque
import numpy as np
import cv2
from threshold import load_calibration, undistort, threshold_binary
from perspective import SRC, SRC_540P, get_transform_matrices, warp
from lane_finder import fit_polynomial
from measure import curvature_radius, vehicle_offset
from draw import draw_lane


def is_sane(left_fit, right_fit, h):
    widths = [np.polyval(right_fit, y) - np.polyval(left_fit, y) for y in (0, h // 2, h - 1)]
    return all(450 < wd < 850 for wd in widths)


def process_video(in_path, out_path="output_images/project_video_output.mp4"):
    mtx, dist = load_calibration()
    lefts, rights = deque(maxlen=8), deque(maxlen=8)

    cap = cv2.VideoCapture(in_path)
    M, Minv = get_transform_matrices(SRC_540P if cap.get(cv2.CAP_PROP_FRAME_HEIGHT) == 540 else SRC)
    size = (1280, 720)
    writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), cap.get(cv2.CAP_PROP_FPS), size)

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        undist = undistort(cv2.resize(frame, size), mtx, dist)
        binary_warped = warp(threshold_binary(undist), M)
        h, w = binary_warped.shape

        try:
            left_fit, right_fit, _ = fit_polynomial(binary_warped)
            if is_sane(left_fit, right_fit, h) or not lefts:
                lefts.append(left_fit)
                rights.append(right_fit)
        except (TypeError, np.linalg.LinAlgError):
            pass

        if not lefts:
            writer.write(undist)
            continue

        left_fit, right_fit = np.mean(lefts, axis=0), np.mean(rights, axis=0)
        radius = (curvature_radius(left_fit, h - 1) + curvature_radius(right_fit, h - 1)) / 2
        offset = vehicle_offset(left_fit, right_fit, w, h)
        writer.write(draw_lane(undist, binary_warped, left_fit, right_fit, Minv, radius, offset))

    cap.release()
    writer.release()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    process_video(sys.argv[1], sys.argv[2])