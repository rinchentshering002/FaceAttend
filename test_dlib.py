import cv2
import face_recognition
import numpy as np

print("Opening Camera Index 1...")
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Camera 1 won't open. Try changing 1 to 0.")
    exit()

print("Camera opened. Press SPACE to capture a face.")

while True:
    ret, frame = cap.read()
    if not ret: continue

    cv2.imshow("Test - Press SPACE", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 32: # SPACE
        print("Capturing...")
        
        # The exact conversion we use in the app
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame = np.ascontiguousarray(rgb_frame, dtype=np.uint8)
        
        print(f"Image type: {type(rgb_frame)}")
        print(f"Image dtype: {rgb_frame.dtype}")
        print(f"Image shape: {rgb_frame.shape}")

        try:
            print("Finding faces...")
            locs = face_recognition.face_locations(rgb_frame)
            print(f"Found {len(locs)} face(s).")
            
            print("Encoding faces...")
            encodings = face_recognition.face_encodings(rgb_frame, locs)
            print("SUCCESS! Dlib encoded the face perfectly.")
            print(encodings[0][:5]) # Print first 5 numbers
        except Exception as e:
            print(f"FAILED WITH ERROR: {e}")

        break
        
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()