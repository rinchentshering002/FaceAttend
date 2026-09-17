import cv2

camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Could not open external webcam.")
    exit()

print("Camera opened.")
print("CLICK INSIDE THE CAMERA WINDOW FIRST.")
print("Then press SPACE to capture.")
print("Press Q to quit.")

while True:
    ret, frame = camera.read()

    if not ret:
        print("Failed to read camera.")
        break

    cv2.putText(
        frame,
        "CLICK WINDOW - SPACE = Capture | Q = Quit",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Keyboard Camera Test", frame)

    key = cv2.waitKey(30) & 0xFF

    if key == 32:
        print("SPACE DETECTED!")
        cv2.imwrite("test_capture.jpg", frame)
        break

    if key == ord("q"):
        print("Q DETECTED!")
        break

camera.release()
cv2.destroyAllWindows()