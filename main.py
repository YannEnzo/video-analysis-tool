# main.py
import tkinter as tk
import cv2
import threading
import time
import queue
from ui import VideoAnalysisUI
from motion_detector import MotionDetector
from object_detector import ObjectDetector

class VideoAnalysisApp(VideoAnalysisUI):
    def __init__(self, root):
        super().__init__(root)
        
        # Initialize detectors
        self.motion_detector = MotionDetector()
        self.object_detector = None  # Will initialize on demand
        
        # Analysis state
        self.analyzing = False
        self.analysis_thread = None
        self.display_thread = None
        self.detection_thread = None
        self.current_analysis_type = None
        
        # Video source
        self.video_source = None
        self.vid = None
        self.using_camera = False
        self.camera_id = 0  # Default camera ID
        
        # Results tracking
        self.detected_objects = []
        self.motion_detected = False
        
        # Thread communication
        self.frame_queue = queue.Queue(maxsize=1)  # For frames to display
        self.detection_queue = queue.Queue(maxsize=1)  # For frames to detect objects
        
        # Add observer for dropdown changes
        self.dropdown.bind("<<ComboboxSelected>>", self.on_analysis_type_change)
        
        # Frame processing rate control
        self.skip_frames = 5  # Process every 6th frame for object detection
        
        # Update UI to include camera option
        self.add_camera_button()
        
    def add_camera_button(self):
        """Add a button to use webcam instead of video file"""
        button_style = {"font": ("Arial", 10), "bg": self.accent_color, "fg": "white", 
                       "relief": tk.RAISED, "padx": 10, "pady": 5}
        
        self.btn_camera = tk.Button(self.top_frame, text="Use Camera", 
                                  command=self.use_camera, **button_style)
        self.btn_camera.pack(side=tk.LEFT, padx=5)
        
# Add this method to your VideoAnalysisApp class in main.py
    def use_camera(self):
        """Switch to using the webcam as input source"""
        # Disable button while trying to connect
        self.btn_camera.config(state=tk.DISABLED, text="Connecting...")
        self.status_label.config(text="Connecting to camera...")
        self.root.update()
        
        # Start camera connection in a separate thread
        threading.Thread(target=self._connect_camera, daemon=True).start()

    def _connect_camera(self):
        """Connect to camera in a background thread"""
        # Close any existing video
        if self.vid is not None:
            self.vid.release()
            self.vid = None
        
        # Try to open the camera
        try:
            # Set camera properties for faster opening
            self.vid = cv2.VideoCapture(self.camera_id)
            self.vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Use minimal buffer
            
            if not self.vid.isOpened():
                self.root.after(0, lambda: self.status_label.config(text="Error: Could not open camera"))
                self.root.after(0, lambda: self.btn_camera.config(state=tk.NORMAL, text="Use Camera"))
                return
                
            # Update state
            self.using_camera = True
            self.video_source = None
            
            # Enable the start button and update UI
            self.root.after(0, lambda: self.status_label.config(text="Using camera as input"))
            self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.btn_camera.config(text="Camera Active", state=tk.NORMAL))
            self.root.after(0, lambda: self.btn_load.config(state=tk.DISABLED))
            
            # Preview first frame
            ret, frame = self.vid.read()
            if ret:
                self.root.after(0, lambda f=frame: self.display_frame(f))
                
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.status_label.config(text=f"Camera error: {err}"))
            self.root.after(0, lambda: self.btn_camera.config(state=tk.NORMAL, text="Use Camera"))
    
    def load_video(self):
        """Override to handle switching back from camera"""
        # Close camera if it was being used
        if self.using_camera and self.vid is not None:
            self.vid.release()
            self.vid = None
            self.using_camera = False
            self.btn_camera.config(text="Use Camera")
        
        # Continue with normal video loading
        super().load_video()
        
        # Re-enable camera button if video is loaded
        if self.video_source:
            self.btn_camera.config(state=tk.NORMAL)
    
    def on_analysis_type_change(self, event):
        """Handle changes to analysis type dropdown while running"""
        if self.analyzing:
            # Update the analysis type without restarting
            new_type = self.analysis_type.get()
            
            # Initialize object detector if needed
            if new_type in ["Object Recognition", "Both"] and self.object_detector is None:
                try:
                    self.status_label.config(text="Loading object detection model...")
                    self.root.update()
                    self.object_detector = ObjectDetector()
                    self.status_label.config(text="Model loaded successfully")
                except Exception as e:
                    self.status_label.config(text=f"Error loading model: {str(e)}")
                    return
                    
            # Clear results if changing modes
            if self.current_analysis_type != new_type:
                self.objects_listbox.delete(0, tk.END)
                self.current_analysis_type = new_type
    
    def start_analysis(self):
        if not self.analyzing:
            # Make sure we have a video source
            if self.vid is None:
                if self.using_camera:
                    # Try to reopen the camera
                    self.use_camera()
                    if self.vid is None:
                        return
                else:
                    self.status_label.config(text="Please load a video or enable camera first")
                    return
            
            # Update UI
            self.btn_start.config(text="Stop Analysis")
            self.analyzing = True
            
            # Clear previous results
            self.objects_listbox.delete(0, tk.END)
            
            # Save current analysis type
            self.current_analysis_type = self.analysis_type.get()
            
            # Initialize object detector if needed
            if self.current_analysis_type in ["Object Recognition", "Both"]:
                try:
                    if self.object_detector is None:
                        self.status_label.config(text="Loading object detection model...")
                        self.root.update()
                        self.object_detector = ObjectDetector()
                        self.status_label.config(text="Model loaded successfully")
                except Exception as e:
                    self.status_label.config(text=f"Error loading model: {str(e)}")
                    self.analyzing = False
                    self.btn_start.config(text="Start Analysis")
                    return
            
            # Start threads for video processing, display, and object detection
            self.display_thread = threading.Thread(target=self.display_frames)
            self.display_thread.daemon = True
            self.display_thread.start()
            
            self.analysis_thread = threading.Thread(target=self.process_video)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            
            if self.current_analysis_type in ["Object Recognition", "Both"]:
                self.detection_thread = threading.Thread(target=self.detect_objects)
                self.detection_thread.daemon = True
                self.detection_thread.start()
                
            # Disable source switching while analyzing
            self.btn_load.config(state=tk.DISABLED)
            self.btn_camera.config(state=tk.DISABLED)
        else:
            # Stop analysis
            self.analyzing = False
            self.btn_start.config(text="Start Analysis")
            
            # Re-enable source switching
            self.btn_load.config(state=tk.NORMAL)
            self.btn_camera.config(state=tk.NORMAL)
            
            # Clear queues to avoid deadlocks
            try:
                while True:
                    self.frame_queue.get_nowait()
            except queue.Empty:
                pass
                
            try:
                while True:
                    self.detection_queue.get_nowait()
            except queue.Empty:
                pass
    
    def process_video(self):
        """Thread for video processing and motion detection"""
        if not self.vid.isOpened():
            self.status_label.config(text="Error: Video source not open")
            self.analyzing = False
            self.btn_start.config(text="Start Analysis")
            return
        
        # Don't reset position for camera
        if not self.using_camera and self.video_source:
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # For camera, set smaller buffer to reduce latency
        if self.using_camera:
            self.vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        frame_count = 0
        
        # Process video frames
        while self.analyzing:
            # Get current analysis type (may have changed)
            analysis_type = self.analysis_type.get()
            
            ret, frame = self.vid.read()
            
            if not ret:
                if self.using_camera:
                    # For camera, try to reconnect or wait
                    time.sleep(0.1)
                    continue
                else:
                    # For video file, loop back
                    self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
            
            result_frame = frame.copy()
            frame_count += 1
            
            # Apply motion detection if selected
            if analysis_type in ["Motion Detection", "Both"]:
                self.motion_detected, motion_frame, _ = self.motion_detector.detect(frame)
                result_frame = motion_frame
                
                # Update motion status
                status_text = "Detected" if self.motion_detected else "Not Detected"
                status_color = "green" if self.motion_detected else "red"
                self.root.after(0, lambda t=status_text, c=status_color: 
                            self.motion_status.config(text=t, fg=c))
            
            # Send frame for display
            try:
                self.frame_queue.put(result_frame, block=False)
            except queue.Full:
                # Skip frame if queue is full (display is slower than processing)
                pass
                
            # Send frame for object detection (only every few frames)
            if analysis_type in ["Object Recognition", "Both"] and frame_count % (self.skip_frames + 1) == 0:
                try:
                    # Resize for faster processing
                    h, w = result_frame.shape[:2]
                    scale = 480.0 / w if w > 480 else 1.0
                    small_frame = cv2.resize(result_frame, (0, 0), fx=scale, fy=scale)
                    
                    # Add scale information along with the frame
                    self.detection_queue.put((small_frame, scale, result_frame.shape[:2]), block=False)
                except queue.Full:
                    # Skip detection if queue is full
                    pass
            
            # Control frame rate - slower for camera to prevent lag
            time.sleep(0.03 if self.using_camera else 0.01)
    
    def detect_objects(self):
        """Thread dedicated to object detection"""
        last_objects = []
        
        while self.analyzing:
            try:
                # Get a frame for detection
                frame, scale, original_shape = self.detection_queue.get(timeout=0.1)
                
                # Perform detection
                detected_objects, _ = self.object_detector.detect(frame)
                
                # Scale back bounding boxes to original size if needed
                if scale != 1.0:
                    for obj in detected_objects:
                        x, y, width, height = obj['box']
                        obj['box'] = (
                            int(x / scale),
                            int(y / scale),
                            int(width / scale),
                            int(height / scale)
                        )
                
                # Update results
                self.detected_objects = detected_objects
                last_objects = detected_objects
                
                # Update objects list
                self.root.after(0, self.update_objects_list)
            except queue.Empty:
                # No frame available for detection
                pass
            except Exception as e:
                self.status_label.config(text=f"Detection error: {str(e)}")
    
    def display_frames(self):
        """Thread dedicated to displaying frames"""
        last_objects = []
        
        while self.analyzing:
            try:
                # Get the next frame to display
                frame = self.frame_queue.get(timeout=0.1)
                
                # Get current analysis type
                analysis_type = self.analysis_type.get()
                
                # Draw detected objects on the frame if applicable
                if analysis_type in ["Object Recognition", "Both"]:
                    # Use the latest detection results
                    for obj in self.detected_objects:
                        x, y, width, height = obj['box']
                        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), 2)
                        label = f"{obj['class']}: {int(obj['confidence'] * 100)}%"
                        cv2.putText(frame, label, (x, y - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                # Display the frame
                self.root.after(0, lambda f=frame: self.display_frame(f))
            except queue.Empty:
                # No frame available to display, wait a bit
                time.sleep(0.01)
            except Exception as e:
                print(f"Display error: {e}")
    
    def update_objects_list(self):
        self.objects_listbox.delete(0, tk.END)
        for obj in self.detected_objects:
            confidence = int(obj['confidence'] * 100)
            self.objects_listbox.insert(tk.END, f"{obj['class']}: {confidence}%")
            
    def on_closing(self):
        """Clean up resources when the application is closed"""
        self.analyzing = False
        if self.vid:
            self.vid.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnalysisApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()