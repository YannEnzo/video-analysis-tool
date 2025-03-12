# object_detector.py
import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

class ObjectDetector:
    def __init__(self):
        # Load model from TensorFlow Hub
        self.detector = hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2")
        
        # COCO class labels
        self.category_index = {
            1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane',
            6: 'bus', 7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light',
            11: 'fire hydrant', 13: 'stop sign', 14: 'parking meter', 15: 'bench',
            16: 'bird', 17: 'cat', 18: 'dog', 19: 'horse', 20: 'sheep',
            21: 'cow', 22: 'elephant', 23: 'bear', 24: 'zebra', 25: 'giraffe',
            27: 'backpack', 28: 'umbrella', 31: 'handbag', 32: 'tie', 33: 'suitcase',
            34: 'frisbee', 35: 'skis', 36: 'snowboard', 37: 'sports ball', 38: 'kite',
            39: 'baseball bat', 40: 'baseball glove', 41: 'skateboard', 42: 'surfboard',
            43: 'tennis racket', 44: 'bottle', 46: 'wine glass', 47: 'cup', 48: 'fork',
            49: 'knife', 50: 'spoon', 51: 'bowl', 52: 'banana', 53: 'apple',
            54: 'sandwich', 55: 'orange', 56: 'broccoli', 57: 'carrot', 58: 'hot dog',
            59: 'pizza', 60: 'donut', 61: 'cake', 62: 'chair', 63: 'couch',
            64: 'potted plant', 65: 'bed', 67: 'dining table', 70: 'toilet', 72: 'tv',
            73: 'laptop', 74: 'mouse', 75: 'remote', 76: 'keyboard', 77: 'cell phone',
            78: 'microwave', 79: 'oven', 80: 'toaster', 81: 'sink', 82: 'refrigerator',
            84: 'book', 85: 'clock', 86: 'vase', 87: 'scissors', 88: 'teddy bear',
            89: 'hair drier', 90: 'toothbrush'
        }
        
        self.confidence_threshold = 0.5
    
    def detect(self, frame):
        # Convert to RGB (TensorFlow models expect RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to tensor, add batch dimension
        input_tensor = tf.convert_to_tensor(rgb_frame)
        input_tensor = input_tensor[tf.newaxis, ...]
        
        # Run inference
        detections = self.detector(input_tensor)
        
        # Get detection results
        boxes = detections['detection_boxes'][0].numpy()
        classes = detections['detection_classes'][0].numpy().astype(np.int32)
        scores = detections['detection_scores'][0].numpy()
        
        # Create a copy of the frame to draw on
        frame_with_objects = frame.copy()
        h, w, _ = frame.shape
        
        # Store detected objects
        detected_objects = []
        
        # Process detected objects
        for i in range(len(scores)):
            if scores[i] > self.confidence_threshold:
                # Get coordinates
                box = boxes[i]
                y_min, x_min, y_max, x_max = box
                x_min, x_max = int(x_min * w), int(x_max * w)
                y_min, y_max = int(y_min * h), int(y_max * h)
                
                # Get class name
                class_id = classes[i]
                class_name = self.category_index.get(class_id, 'unknown')
                
                # Add to detected objects
                detected_objects.append({
                    'class': class_name,
                    'confidence': float(scores[i]),
                    'box': (x_min, y_min, x_max - x_min, y_max - y_min)
                })
                
                # Draw rectangle and label
                cv2.rectangle(frame_with_objects, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
                label = f"{class_name}: {int(scores[i] * 100)}%"
                cv2.putText(frame_with_objects, label, (x_min, y_min - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return detected_objects, frame_with_objects