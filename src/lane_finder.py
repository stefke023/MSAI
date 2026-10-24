import os
import numpy as np
import cv2
from threshold import load_calibration, undistort, threshold_binary
from perspective import get_transform_matrices, warp


def find_lane_pixels(binary_warped, nwindows=9, margin=100, minpix=50):
    h, w = binary_warped.shape
    histogram = np.sum(binary_warped, axis=0)
    midpoint = w // 2
    margin_x = w // 8
    leftx_current = int(np.argmax(histogram[margin_x:midpoint]) + margin_x)
    rightx_current = int(np.argmax(histogram[midpoint:w - margin_x]) + midpoint)

    window_height = h // nwindows
    nonzeroy, nonzerox = binary_warped.nonzero()
    out_img = np.dstack((binary_warped, binary_warped, binary_warped)) * 255
    left_inds, right_inds = [], []

    for window in range(nwindows):
        y_low = h - (window + 1) * window_height
        y_high = h - window * window_height
        xl_low, xl_high = leftx_current - margin, leftx_current + margin
        xr_low, xr_high = rightx_current - margin, rightx_current + margin

        cv2.rectangle(out_img, (xl_low, y_low), (xl_high, y_high), (0, 255, 0), 2)
        cv2.rectangle(out_img, (xr_low, y_low), (xr_high, y_high), (0, 255, 0), 2)

        in_y = (nonzeroy >= y_low) & (nonzeroy < y_high)
        good_left = (in_y & (nonzerox >= xl_low) & (nonzerox < xl_high)).nonzero()[0]
        good_right = (in_y & (nonzerox >= xr_low) & (nonzerox < xr_high)).nonzero()[0]
        left_inds.append(good_left)
        right_inds.append(good_right)

        if len(good_left) > minpix:
            leftx_current = int(np.mean(nonzerox[good_left]))
        if len(good_right) > minpix:
            rightx_current = int(np.mean(nonzerox[good_right]))

    left_inds = np.concatenate(left_inds)
    right_inds = np.concatenate(right_inds)
    return nonzerox[left_inds], nonzeroy[left_inds], nonzerox[right_inds], nonzeroy[right_inds], out_img


def fit_polynomial(binary_warped):
    leftx, lefty, rightx, righty, out_img = find_lane_pixels(binary_warped)
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    out_img[lefty, leftx] = [0, 0, 255]
    out_img[righty, rightx] = [255, 0, 0]

    ploty = np.arange(binary_warped.shape[0])
    for fit in (left_fit, right_fit):
        fitx = fit[0] * ploty ** 2 + fit[1] * ploty + fit[2]
        pts = np.int32(np.column_stack((fitx, ploty)))
        cv2.polylines(out_img, [pts], False, (0, 255, 255), 3)

    return left_fit, right_fit, out_img


def search_around_poly(binary_warped, left_fit, right_fit, margin=100):
    nonzeroy, nonzerox = binary_warped.nonzero()
    left_x = left_fit[0] * nonzeroy ** 2 + left_fit[1] * nonzeroy + left_fit[2]
    right_x = right_fit[0] * nonzeroy ** 2 + right_fit[1] * nonzeroy + right_fit[2]

    left_inds = np.abs(nonzerox - left_x) < margin
    right_inds = np.abs(nonzerox - right_x) < margin

    new_left = np.polyfit(nonzeroy[left_inds], nonzerox[left_inds], 2)
    new_right = np.polyfit(nonzeroy[right_inds], nonzerox[right_inds], 2)
    return new_left, new_right


if __name__ == "__main__":
    os.makedirs("output_images", exist_ok=True)
    mtx, dist = load_calibration()
    M, Minv = get_transform_matrices()

    img = undistort(cv2.imread("test_images/test1.jpg"), mtx, dist)
    binary_warped = warp(threshold_binary(img), M)

    left_fit, right_fit, out_img = fit_polynomial(binary_warped)
    cv2.imwrite("output_images/color_fit_lines.jpg", out_img)