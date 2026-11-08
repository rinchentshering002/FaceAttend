import cv2
import face_recognition

print("Opening Camera 1...")
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Cannot open camera.")
    exit()

print("Press SPACE to capture...")
while True:
    ret, frame = cap.read()
    if not ret: continue

    cv2.imshow("Diagnostic - Press SPACE", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 32: # SPACE
        print("\n--- CAPTURING ---")
        
        # 1. Save to file
        cv2.imwrite("test_face.jpg", frame)
        print("Image saved to disk.")
        
        # 2. Let face_recognition load it directly from the file path
        print("Loading via face_recognition...")
        img = face_recognition.load_image_file("test_face.jpg")
        
        # 3. Try to find and encode
        print("Finding and encoding faces...")
        try:
            locs = face_recognition.face_locations(img)
            encodings = face_recognition.face_encodings(img, locs)
            print(f"SUCCESS! Found {len(locs)} faces and encoded them.")
        except Exception as e:
            print(f"FAILED WITH ERROR: {e}")
        break
        
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()