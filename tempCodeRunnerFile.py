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