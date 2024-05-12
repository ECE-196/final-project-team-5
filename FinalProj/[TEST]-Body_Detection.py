import cv2
import pathlib 

# Load the pre-trained Haar cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(str(pathlib.Path(__file__).resolve().parent)+'\\'+'haarcascade_fullbody.xml')

# Open the default camera (usually the first camera connected to the computer)
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Convert the frame to grayscale (required by the face detector)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.8, minNeighbors=1, minSize=(30, 30))
    # Draw rectangles around the detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    print(f'people detected: {len(faces)}')

    # Display the frame with rectangles around the detected faces
    cv2.imshow('Face Detection', frame)

    # Check if the user pressed 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()