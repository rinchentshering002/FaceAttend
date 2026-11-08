import os
from dotenv import load_dotenv
from supabase import create_client

CAMERA_WARMUP_FRAMES = 15
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials are missing!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def register_student(student_id, name, student_class, section, year, camera_index=0):
    # Lazy imports — only loaded when this function actually runs
    import cv2
    import numpy as np
    import face_recognition

    student_id = str(student_id).strip()
    name = str(name).strip()
    student_class = str(student_class).strip()
    section = str(section).strip()
    year = str(year).strip()

    if not all([student_id, name, student_class, section, year]):
        return False, "All fields are required."

    try:
        existing = supabase.table("students").select("student_id").eq("student_id", student_id).execute()
        if existing.data:
            return False, f"Student ID '{student_id}' already exists!"
    except Exception as e:
        return False, f"Could not check student ID.\n\n{e}"

    camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not camera.isOpened():
        return False, f"Could not open Camera {camera_index}.\n\nTry a different camera index."

    for _ in range(CAMERA_WARMUP_FRAMES):
        success, _ = camera.read()
        if not success: break

    face_encoding = None
    temp_img_path = "temp_registration.jpg"

    try:
        while True:
            ret, frame = camera.read()
            if not ret or frame is None or frame.size == 0: continue

            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame = np.ascontiguousarray(rgb_frame, dtype=np.uint8)

            face_locations = face_recognition.face_locations(rgb_frame)
            for top, right, bottom, left in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            face_count = len(face_locations)
            cv2.putText(frame, f"Faces detected: {face_count}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, "SPACE = Capture | Q = Cancel", (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow("FaceAttend - Student Registration", frame)
            key = cv2.waitKey(30) & 0xFF

            if key == 32:
                if face_count == 0: continue
                if face_count > 1: continue

                cv2.imwrite(temp_img_path, frame)
                loaded_image = face_recognition.load_image_file(temp_img_path)
                encodings = face_recognition.face_encodings(loaded_image)

                if len(encodings) != 1: continue
                face_encoding = encodings[0]
                break
            elif key == ord("q"):
                return False, "Registration cancelled."

    finally:
        camera.release()
        cv2.destroyAllWindows()
        if os.path.exists(temp_img_path): os.remove(temp_img_path)

    if face_encoding is None:
        return False, "No face encoding was generated."

    encoding_text = ",".join(str(float(value)) for value in face_encoding)
    student_data = {
        "student_id": student_id, "name": name, "class": student_class,
        "section": section, "year": year, "face_encoding": encoding_text,
    }

    try:
        response = supabase.table("students").insert(student_data).execute()
        if not response.data: return False, "Student registration failed."
        return True, f"Student {name} registered successfully!"
    except Exception as e:
        return False, f"Registration failed.\n\n{e}"