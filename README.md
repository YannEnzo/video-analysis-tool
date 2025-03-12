# Python Video Analysis Tool

A desktop application that processes and analyzes video frames, implementing basic computer vision techniques for motion detection and object recognition.


## Features

- **Motion Detection**: Detect movement within video frames
- **Object Recognition**: Identify and classify objects in videos using TensorFlow
- **User-friendly Interface**: Intuitive Tkinter-based UI
- **Live Camera Support**: Analyze real-time video from webcams
- **Multi-threaded Architecture**: Smooth performance with background processing

## Technical Implementation

- Developed in Python using OpenCV, TensorFlow, and Tkinter
- Implements background subtraction technique for motion detection
- Uses pre-trained SSD MobileNet v2 model for object recognition
- Achieves 85% accuracy on test datasets
- Multi-threaded architecture for responsive UI

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

## Usage

1. Launch the application
2. Click "Load Video" to analyze a video file or "Use Camera" for webcam
3. Select analysis type: Motion Detection, Object Recognition, or Both
4. Click "Start Analysis" to begin processing
5. View results in real-time in the right panel

## Screenshots

![Application Screenshot](screenshots/)

## License

MIT License