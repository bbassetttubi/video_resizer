import streamlit as st
import moviepy.editor as mp
import tempfile
import os
from moviepy.video.fx.all import margin
from utils import clean_up_files
import cv2
import numpy as np

def video_uploader():
    uploaded_video = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov", "mkv"])
    if uploaded_video is not None:
        # Save uploaded video to a temporary file
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_video.read())
        tfile.flush()
        input_video_path = tfile.name
        st.video(input_video_path)

        st.write("### Resize Options")

        # Load the video clip to get dimensions
        try:
            clip = mp.VideoFileClip(input_video_path)
            original_width = clip.w
            original_height = clip.h
            original_aspect_ratio = original_width / original_height
        except Exception as e:
            st.error(f"An error occurred while loading the video: {e}")
            clean_up_files([input_video_path])
            return

        # Define platforms and their aspect ratios
        platforms = [
            "Instagram", "Facebook", "YouTube", "Twitter",
            "Snapchat", "LinkedIn", "Pinterest", "Tubi", "Custom"
        ]
        platform = st.selectbox("Select Platform", platforms)

        platform_aspect_ratios = {
            # (Same as your original aspect ratios)
        }

        # (Same as your original code for selecting aspect ratio and target dimensions)

        # Display the determined dimensions to the user
        st.markdown(f"**Target Dimensions:** {target_width} x {target_height} pixels")

        # Resize method (only Crop is available since we're focusing on automatic detection)
        resize_method = "Crop"

        output_format = st.selectbox("Output Format", ["mp4", "avi", "mov", "mkv"])

        # Initialize output_video_path to None
        output_video_path = None

        if st.button("Resize and Convert Video"):
            try:
                # Use target_width and target_height
                target_width = target_width
                target_height = target_height

                # Calculate scaling factor
                scale_factor_w = target_width / clip.w
                scale_factor_h = target_height / clip.h
                scale_factor = max(scale_factor_w, scale_factor_h)

                new_width = int(clip.w * scale_factor)
                new_height = int(clip.h * scale_factor)

                resized_clip = clip.resize(newsize=(new_width, new_height))

                # Automatically detect the optimal cropping region based on face detection
                final_clip = apply_crop(resized_clip, target_width, target_height)

                # Save to a temporary file
                temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.' + output_format)
                output_video_path = temp_video_file.name
                temp_video_file.close()  # Close the file so MoviePy can write to it

                # Determine the audio codec based on the output format
                # (Same as your original code)

                # Use faster encoding preset and other optimizations
                # (Same as your original code)

                # Display the resized video
                # (Same as your original code)

            except Exception as e:
                st.error(f"An error occurred during video processing: {e}")
            finally:
                # Clean up temporary files and release resources
                # (Same as your original code)

def apply_crop(clip, target_width, target_height):
    """
    Apply automatic cropping to the video clip based on face detection.

    Args:
        clip (moviepy.editor.VideoFileClip): The resized video clip.
        target_width (int): The desired width after cropping.
        target_height (int): The desired height after cropping.

    Returns:
        moviepy.editor.VideoFileClip: The cropped video clip.
    """
    new_width, new_height = clip.size

    if new_width < target_width or new_height < target_height:
        # (Same as your original padding code)

    frame_width, frame_height = new_width, new_height
    target_aspect_ratio = target_width / target_height

    # Automatically detect faces in the clip
    x1, y1, x2, y2 = detect_people_regions_in_clip(clip, frame_width, frame_height)
    x1, y1, x2, y2 = adjust_bounding_box_to_aspect_ratio(
        x1, y1, x2, y2, target_aspect_ratio, frame_width, frame_height
    )

    # Apply cropping
    final_clip = clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)

    return final_clip

def detect_people_regions_in_clip(clip, frame_width, frame_height):
    import cv2
    import numpy as np

    # Load pre-trained face detector (DNN model)
    modelFile = "res10_300x300_ssd_iter_140000.caffemodel"
    configFile = "deploy.prototxt"

    # Check if the model files exist
    if not os.path.isfile(modelFile) or not os.path.isfile(configFile):
        st.error("Face detection model files are missing. Please download them and place them in the working directory.")
        return (0, 0, frame_width, frame_height)

    net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

    people_bounding_boxes = []

    total_frames = int(clip.duration * clip.fps)
    frame_indices = np.linspace(0, total_frames - 1, num=min(10, total_frames)).astype(int)

    for idx in frame_indices:
        t = idx / clip.fps
        frame = clip.get_frame(t)
        (h, w) = frame.shape[:2]

        # Prepare the frame for DNN face detection
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0), swapRB=False, crop=False)

        net.setInput(blob)
        detections = net.forward()

        # Loop over the detections
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            # Filter out weak detections
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x_start, y_start, x_end, y_end) = box.astype("int")
                people_bounding_boxes.append((x_start, y_start, x_end, y_end))

    # If no faces detected, use the center of the frame
    if not people_bounding_boxes:
        x_center = frame_width / 2
        y_center = frame_height / 2
        x1 = x_center - target_width / 2
        y1 = y_center - target_height / 2
        x2 = x_center + target_width / 2
        y2 = y_center + target_height / 2
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame_width, x2)
        y2 = min(frame_height, y2)
        return int(x1), int(y1), int(x2), int(y2)

    # Compute the bounding rectangle that covers all faces detected
    x1 = min(box[0] for box in people_bounding_boxes)
    y1 = min(box[1] for box in people_bounding_boxes)
    x2 = max(box[2] for box in people_bounding_boxes)
    y2 = max(box[3] for box in people_bounding_boxes)

    # Expand the bounding box slightly to include shoulders and some background
    box_height = y2 - y1
    y1 = max(0, y1 - int(0.2 * box_height))  # Expand upwards by 20%
    y2 = min(frame_height, y2 + int(0.1 * box_height))  # Expand downwards by 10%

    return x1, y1, x2, y2

def adjust_bounding_box_to_aspect_ratio(x1, y1, x2, y2, target_aspect_ratio, frame_width, frame_height):
    """
    Adjusts the bounding box to match the target aspect ratio while keeping the area of interest in view.

    Args:
        x1, y1, x2, y2: Coordinates of the initial bounding box.
        target_aspect_ratio: Desired aspect ratio (width / height).
        frame_width: Width of the video frame.
        frame_height: Height of the video frame.

    Returns:
        Adjusted bounding box coordinates (x1, y1, x2, y2)
    """
    import math

    # Calculate current bounding box width and height
    box_width = x2 - x1
    box_height = y2 - y1
    box_aspect_ratio = box_width / box_height

    # Center coordinates
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2

    if box_aspect_ratio > target_aspect_ratio:
        # Need to increase height
        new_box_height = box_width / target_aspect_ratio
        y1 = y_center - new_box_height / 2
        y2 = y_center + new_box_height / 2
    else:
        # Need to increase width
        new_box_width = box_height * target_aspect_ratio
        x1 = x_center - new_box_width / 2
        x2 = x_center + new_box_width / 2

    # Ensure coordinates are within frame boundaries
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(frame_width, x2)
    y2 = min(frame_height, y2)

    # Adjust in case the box is still not matching aspect ratio due to frame boundaries
    box_width = x2 - x1
    box_height = y2 - y1
    box_aspect_ratio = box_width / box_height

    if not math.isclose(box_aspect_ratio, target_aspect_ratio, rel_tol=0.01):
        if box_aspect_ratio > target_aspect_ratio:
            # Crop width
            new_box_width = box_height * target_aspect_ratio
            x1 = x_center - new_box_width / 2
            x2 = x_center + new_box_width / 2
        else:
            # Crop height
            new_box_height = box_width / target_aspect_ratio
            y1 = y_center - new_box_height / 2
            y2 = y_center + new_box_height / 2

        # Ensure coordinates are within frame boundaries
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame_width, x2)
        y2 = min(frame_height, y2)

    return int(x1), int(y1), int(x2), int(y2)
