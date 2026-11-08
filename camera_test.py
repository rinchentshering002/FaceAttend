import cv2

print("Testing cameras... (Look for a window to pop up)")

for index in range(4):
    print(f"Testing camera index {index}...")
    
    # Use CAP_DSHOW for Windows
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"-> SUCCESS! Camera {index} is working.")
            cv2.imshow(f"Camera Index {index} - Press Q to close", frame)
            cv2.waitKey(3000) # Shows the camera for 3 seconds
            cv2.destroyAllWindows()
        cap.release()
    else:
        print(f"-> Camera {index} not found or in use.\n")

print("Test complete.")