import cv2

for camera_index in range(5):

    print(f"Testing camera index {camera_index}...")

    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        print(f"❌ Camera {camera_index} not available")
        camera.release()
        continue

    print(f"✅ Camera {camera_index} opened")

    while True:
        ret, frame = camera.read()

        if not ret:
            print("❌ Could not read camera")
            break

        cv2.imshow(
            f"Camera Index {camera_index}",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        # Press Q to close this camera
        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

print("Camera testing finished.")