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
[image5]: ./examples/color_fit_lines.jpg "Fit Visual"
[image6]: ./examples/example_output.jpg "Output"
[video1]: ./project_video.mp4 "Video"

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

TODO: Add your text here!!!

#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

TODO: Add your text here!!!

#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

TODO: Add your text here!!!

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

TODO: Add your text here!!!

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

TODO: Add your text here!!!

