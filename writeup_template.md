## Writeup Template

### You use this file as a template for your writeup.

---

**Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./output_images/undistort_output.png "Undistorted"
[image2]: ./output_images/undistorted_test1.jpg "Road Transformed"
[image3]: ./output_images/binary_combo_example.jpg "Binary Example"
[image4]: ./output_images/warped_straight_lines.jpg "Warp Example"
[image5]: ./output_images/color_fit_lines.jpg "Fit Visual"
[image6]: ./output_images/example_output.jpg  "Output"

---

### Writeup / README

#### 1. Provide a Writeup that includes all the rubric points and how you addressed each one.

You're reading it!

### Camera Calibration

#### 1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

I wrote the `calibrate_camera()` function in `src/calibration.py`.
My input was 20 chessboard images with 9x6 inner corners.
I created an ideal grid of corner points with perfectly even spacing.
After that, I found all the corners in each photo with `cv2.findChessboardCorners()`,
compared them to the ideal grid, and `cv2.calibrateCamera()` computed the camera matrix
and distortion coefficients.

Before and after undistortion:

![Undistorted][image1]


### Pipeline (single images)

#### 1. Provide an example of a distortion-corrected image.

I load the camera matrix and distortion coefficients from `calibration.p` and apply `cv2.undistort()` in the `undistort()` function in 
`src/thresholds.py`. The left side is the original image, and the right side is the corrected image:

![Road Transformed][image2]

#### 2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

The code is in `threshold_binary()` in `src/thresholds.py`. I convert the image to HLS and combine two thresholds:
- Sobel gradient in the x direction on the L channel (20–100), which detects vertical edges of the lane lines.
- S channel threshold (170–255), which detects yellow and white lines, even in shadow.

A pixel is set to 1 if either condition is true:

![Binary Example][image3]

#### 3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

For this step I wrote `src/perspective.py`.
On the `straight_lines1.jpg` image I picked four points on the road that form a trapezoid around the lane: (585, 460), (203, 720), (1127, 720) and (695, 460).
These map to a rectangle: (320, 0), (320, 720), (960, 720) and (960, 0).
With these points, `cv2.getPerspectiveTransform()` gives me the matrix `M` for the bird's-eye view, and `Minv` for going back to the normal view later.
Then `cv2.warpPerspective()` does the actual warping.
To check if the points are good, I drew them on the image. On the straight road, the lane lines came out vertical and parallel, so the transform works:

![Warp Example][image4]

#### 4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

The code for this step is in `src/lane_finder.py`.
First I take a histogram of the whole warped binary image, ignoring the outer edges where the barrier and other lanes are.
The highest peak on each side shows where the left and right lines are.
Then `find_lane_pixels()` uses 9 sliding windows for each line. Each window collects the white pixels inside it and moves up,
and if it finds more than 50 pixels it re-centers on their mean x position.
In `fit_polynomial()` I fit a second order polynomial x = Ay² + By + C to the pixels of each line with `np.polyfit()`.
For video frames I also wrote `search_around_poly()`, which searches only around the previous fit, so the sliding windows don't have to run every time.

![Fit Visual][image5]

#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

The code for this step is in `src/measure.py`.
First I convert the polynomial from pixels to meters, using 3.7 m for the lane width (640 px in the warped image) and 30 m for the visible lane length (720 px).
In `curvature_radius()` I calculate the radius with R = (1 + (2Ay + B)²)^1.5 / |2A|, at the bottom of the image, right in front of the car.
In `vehicle_offset()` I find the lane center as the middle point between the two lines at the bottom of the image, and compare it with the image center, where the camera is.
For `test1.jpg` I got a radius of about 927 m and an offset of -0.14 m, which means the car is 14 cm left of the lane center.

#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

The code for this step is in `draw_lane()` in `src/draw.py`.
I fill the area between the two fitted lines with green on an empty image in the bird's-eye view.
Then I warp it back to the camera view with `Minv` and blend it with the undistorted image using `cv2.addWeighted()`.
At the end I write the radius of curvature and the vehicle position on the image:

![Output][image6]

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

The code for the video is in `process_video()` in `src/pipeline.py`.
The videos are 960x540, so I first resize each frame to 1280x720, the size my calibration and perspective points were made for.
Then I run the same steps as for single images.
A new fit is used only if the lane width makes sense at the top, middle and bottom of the warped image.
The drawn lane is the average of the last 8 good fits, so the lines don't wobble between frames.

Here are my results: [video 1](./output_images/project_video01_output.mp4), [video 2](./output_images/project_video02_output.mp4), [video 3](./output_images/project_video03_output.mp4).

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

The hardest part was choosing the perspective points. At first my trapezoid followed the road edges instead of the lane lines, so the warped image was full of noise.
The right line is dashed, so its fit is less reliable than the left one.
The pipeline will likely fail in sharp curves, strong shadows, with worn out lines, and at night or in rain. It also depends on a fixed camera position.
To make it more robust, I could use more color spaces, force the lines to be parallel when one has too few pixels, or use a Kalman filter for smoothing.

