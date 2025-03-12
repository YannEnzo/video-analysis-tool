# ui.py
import tkinter as tk
from tkinter import filedialog, ttk
import cv2
from PIL import Image, ImageTk

class VideoAnalysisUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Analysis Tool")
        self.root.geometry("1200x700")  # Wider window with better proportions
        self.root.minsize(900, 600)  # Set minimum size
        
        # Set theme colors
        self.bg_color = "#f0f0f0"
        self.accent_color = "#3498db"
        self.text_color = "#2c3e50"
        self.root.configure(bg=self.bg_color)
        
        # Video source
        self.video_source = None
        self.vid = None
        self.display_width = 800  # Control display width
        self.display_height = 500  # Control display height
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame to hold everything
    # Main frame to hold everything
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for controls
        self.top_frame = tk.Frame(main_frame, bg=self.bg_color)  # Use self.top_frame instead of top_frame
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Style the buttons
        button_style = {"font": ("Arial", 10), "bg": self.accent_color, "fg": "white", 
                        "relief": tk.RAISED, "padx": 10, "pady": 5}
        
        # Button to load video
        self.btn_load = tk.Button(self.top_frame, text="Load Video", command=self.load_video, **button_style)
        self.btn_load.pack(side=tk.LEFT, padx=5)
        
        # Dropdown for analysis type
        self.analysis_type = tk.StringVar()
        self.analysis_type.set("Motion Detection")
        analysis_options = ["Motion Detection", "Object Recognition", "Both"]
        
        # Style the dropdown
        style = ttk.Style()
        style.configure("TCombobox", padding=5)
        
        self.dropdown = ttk.Combobox(self.top_frame, textvariable=self.analysis_type, 
                             values=analysis_options, width=15, style="TCombobox")
        self.dropdown.pack(side=tk.LEFT, padx=5)
        
        # Start/Stop button
        self.btn_start = tk.Button(self.top_frame, text="Start Analysis", 
                          command=self.start_analysis, state=tk.DISABLED, **button_style)
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        # Middle frame to hold video and results
        middle_frame = tk.Frame(main_frame, bg=self.bg_color)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Video frame - fixed size to prevent stretching
        video_frame = tk.Frame(middle_frame, bg="black", width=self.display_width, height=self.display_height)
        video_frame.pack(side=tk.LEFT, padx=5, pady=5)
        video_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Canvas for video display
        self.canvas = tk.Canvas(video_frame, bg="black", width=self.display_width, height=self.display_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right panel for results
        right_panel = tk.Frame(middle_frame, bg=self.bg_color, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        right_panel.pack_propagate(False)  # Prevent frame from shrinking
        
        # Results header
        results_header = tk.Label(right_panel, text="Analysis Results", 
                                 font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.text_color)
        results_header.pack(pady=(0, 10))
        
        # Motion status with better styling
        motion_frame = tk.Frame(right_panel, bg=self.bg_color)
        motion_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(motion_frame, text="Motion:", font=("Arial", 11), 
                bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        self.motion_status = tk.Label(motion_frame, text="Not Detected", 
                                     font=("Arial", 11), bg=self.bg_color, fg="red")
        self.motion_status.pack(side=tk.LEFT, padx=5)
        
        # Objects list with better styling
        tk.Label(right_panel, text="Detected Objects:", font=("Arial", 11), 
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W, pady=(10, 5))
        
        # Frame for listbox with scrollbar
        list_frame = tk.Frame(right_panel, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.objects_listbox = tk.Listbox(list_frame, height=15, width=30, 
                                        font=("Arial", 10), bg="white", fg=self.text_color,
                                        selectbackground=self.accent_color)
        self.objects_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Connect scrollbar to listbox
        self.objects_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.objects_listbox.yview)
        
        # Bottom frame for status
        bottom_frame = tk.Frame(main_frame, bg=self.bg_color)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Status label
        self.status_label = tk.Label(bottom_frame, text="Ready", font=("Arial", 10), 
                                   bg=self.bg_color, fg=self.text_color, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X)
    
    def load_video(self):
        self.video_source = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
        if self.video_source:
            self.status_label.config(text=f"Loaded: {self.video_source}")
            self.btn_start.config(state=tk.NORMAL)
            
            # Preview first frame
            self.vid = cv2.VideoCapture(self.video_source)
            ret, frame = self.vid.read()
            if ret:
                self.display_frame(frame)
    
    def display_frame(self, frame):
        # Convert frame to PhotoImage format for Tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize while maintaining aspect ratio
        h, w = frame.shape[:2]
        aspect_ratio = w / h
        
        if aspect_ratio > (self.display_width / self.display_height):  # Width limited
            new_width = self.display_width
            new_height = int(new_width / aspect_ratio)
        else:  # Height limited
            new_height = self.display_height
            new_width = int(new_height * aspect_ratio)
        
        # Resize the frame
        frame = cv2.resize(frame, (new_width, new_height))
        
        # Create image and display
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Calculate center position
        x_center = (self.display_width - new_width) // 2
        y_center = (self.display_height - new_height) // 2
        
        # Clear canvas and update with new image
        self.canvas.delete("all")
        self.canvas.create_image(x_center, y_center, anchor=tk.NW, image=imgtk)
        self.canvas.image = imgtk  # Keep reference to prevent garbage collection
    
    def start_analysis(self):
        # This will be implemented in the main application class
        pass