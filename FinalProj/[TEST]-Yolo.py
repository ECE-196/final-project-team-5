from ultralytics import YOLO
import cv2 
import pandas as pd

# Load yolov8 model
model = YOLO('yolov8n.pt')

# Load video
cap = cv2.VideoCapture(0)

detection_list=[]

# Read frames
while True:
    ret, frame = cap.read()

    if ret:
        # Detect objects
        results = model(frame)

        # Get detected objects 
        
        detections=pd.Series(sorted(results[0].boxes.cls)).value_counts() 
        
        detections.index  = detections.index.map(results[0].names)
        detections.index = detections.index.astype(str)

        # Update the index of the series with the new index
   
        print(detections)

        
        detection_list.append(detections)

        print(f'people in frame: {detections}')

        # Initialize counter for "person" labels


        # Visualize the frame with bounding boxes
        frame_ = results[0].plot()
        cv2.imshow('frame', frame_)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

# Release the video capture device and close all OpenCV windows
cap.release()
cv2.destroyAllWindows() 

for d in detection_list: 
    print(d)