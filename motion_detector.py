# motion_detector.py
import cv2
import numpy as np

class MotionDetector:
    def __init__(self, sensitivity=20):
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50)
        self.sensitivity = sensitivity
        self.min_contour_area = 500  # Minimum area to be considered motion
    
    def detect(self, frame):
        # Apply background subtraction
        fg_mask = self.background_subtractor.apply(frame)
        
        # Apply threshold to remove shadows
        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create a copy of the frame to draw on
        frame_with_motion = frame.copy()
        
        motion_detected = False
        motion_regions = []
        
        # Process each contour
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter small contours
            if area > self.min_contour_area:
                motion_detected = True
                x, y, w, h = cv2.boundingRect(contour)
                motion_regions.append((x, y, w, h))
                cv2.rectangle(frame_with_motion, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        return motion_detected, frame_with_motion, motion_regions