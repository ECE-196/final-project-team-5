import cv2

# Initialize the HOG descriptor with the default people detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Open a video file or webcam
video = cv2.VideoCapture(0)  # Use 0 for webcam

while True:
    ret, frame = video.read()
    if not ret:
        break  # End of video stream

    # Detect people in the frame
    boxes, _ = hog.detectMultiScale(frame, winStride=(8, 8), padding=(3, 3), scale=1.05)

    # Get the number of people detected in this frame
    num_people = len(boxes)

    print("Number of people detected:", num_people)

    # Draw bounding boxes around detected people
    for (x, y, w, h) in boxes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("People Detection", frame)

    # Break loop with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()