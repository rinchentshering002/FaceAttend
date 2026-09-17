import cv2

camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Could not open the webcam.")
    exit()

print("External webcam opened successfully!")
print("Look at the webcam and press SPACE to capture.")
print("Press ESC to cancel.")

while True:
    ret, frame = camera.read()

    if not ret:
        print("Failed to read from webcam.")
        break

    cv2.imshow("FaceAttend - External Webcam", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 32:
        cv2.imwrite("test_capture.jpg", frame)
        print("Photo captured successfully!")
        break

    if key == 27:
        print("Camera test cancelled.")
        break

camera.release()
cv2.destroyAllWindows()
