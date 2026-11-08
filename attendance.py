import os
import time
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
from zoneinfo import ZoneInfo

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials are missing!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CAMERA_WARMUP_FRAMES = 15
FRAME_SCALE = 0.25
PROCESS_EVERY_N_FRAMES = 4
FACE_MATCH_THRESHOLD = 0.50
DISPLAY_RESULT_FRAMES = 25

COLOR_NAVY_BGR = (110, 74, 44)
COLOR_GOLD_BGR = (106, 199, 231)
COLOR_GREEN_BGR = (35, 130, 75)
COLOR_RED_BGR = (54, 54, 185)
COLOR_WHITE_BGR = (255, 255, 255)


def load_students():
    import numpy as np
    response = supabase.table("students").select("student_id, name, face_encoding").execute()
    students = []
    for row in response.data:
        encoding_text = row.get("face_encoding")
        if not encoding_text: continue
        try:
            values = [float(value.strip()) for value in encoding_text.split(",")]
            if len(values) != 128: continue
            students.append({
                "student_id": row["student_id"],
                "name": row["name"],
                "encoding": np.array(values, dtype=np.float64),
            })
        except Exception:
            continue
    return students


def open_camera(camera_index):
    import cv2
    camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera.release()
        return None
    return camera


def mark_attendance(student, course_id):
    try:
        now = datetime.now(BHUTAN_TZ)
        today = now.date().isoformat()
        current_time = now.time().isoformat()
        attendance_data = {
            "student_id": student["student_id"], "attendance_date": today,
            "attendance_time": current_time, "status": "Present", "course_id": course_id,
        }
        response = supabase.table("attendance").insert(attendance_data).execute()
        if response.data: return True, f"Attendance recorded for {student['name']}."
        return False, "Attendance could not be recorded."
    except Exception as e:
        error_str = str(e).lower()
        if "duplicate key" in error_str or "unique constraint" in error_str:
            return False, f"{student['name']} is already marked Present."
        return False, "Database error while recording attendance."


def take_attendance(course_id, course_code, course_name, camera_index=0):
    # Lazy imports — only loaded when this function actually runs
    import cv2
    import numpy as np
    import face_recognition

    try:
        known_students = load_students()
    except Exception as e:
        return False, f"Could not load students:\n{e}"

    if not known_students:
        return False, "No students with valid face encodings found."

    known_encodings = np.array([student["encoding"] for student in known_students], dtype=np.float64)
    camera = open_camera(camera_index)

    if camera is None:
        return False, f"Could not open Camera {camera_index}.\n\nTry a different camera index using Preview."

    for _ in range(CAMERA_WARMUP_FRAMES):
        success, _ = camera.read()
        if not success: break

    frame_count, result_age = 0, 0
    session_marked_ids, recorded_students = set(), []
    status_message = "Attendance camera ready."
    status_time = time.time()
    last_face_results = []

    try:
        while True:
            success, frame = camera.read()
            if not success or frame is None or frame.size == 0:
                time.sleep(0.01); continue

            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            frame_count += 1

            if frame_count % PROCESS_EVERY_N_FRAMES == 0:
                small_frame = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE, interpolation=cv2.INTER_LINEAR)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                rgb_small_frame = np.ascontiguousarray(rgb_small_frame, dtype=np.uint8)

                face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                new_face_results = []

                if face_locations:
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations, num_jitters=1)

                    for face_encoding, face_location in zip(face_encodings, face_locations):
                        distances = face_recognition.face_distance(known_encodings, face_encoding)
                        best_index = int(np.argmin(distances))
                        best_distance = float(distances[best_index])
                        student = known_students[best_index]

                        top, right, bottom, left = face_location
                        top = int(top / FRAME_SCALE); right = int(right / FRAME_SCALE)
                        bottom = int(bottom / FRAME_SCALE); left = int(left / FRAME_SCALE)

                        if best_distance < FACE_MATCH_THRESHOLD:
                            student_id = student["student_id"]
                            new_face_results.append({
                                "top": top, "right": right, "bottom": bottom, "left": left,
                                "recognized": True, "name": student["name"], "distance": best_distance,
                            })

                            if student_id not in session_marked_ids:
                                success_mark, message = mark_attendance(student, course_id)
                                if success_mark:
                                    session_marked_ids.add(student_id)
                                    recorded_students.append(student["name"])
                                    status_message = f"✓ {student['name']} — Attendance Recorded"
                                else:
                                    if "already marked Present" in message:
                                        session_marked_ids.add(student_id)
                                    status_message = message
                                status_time = time.time()
                        else:
                            new_face_results.append({
                                "top": top, "right": right, "bottom": bottom, "left": left,
                                "recognized": False, "name": "Unknown", "distance": best_distance,
                            })

                if new_face_results:
                    last_face_results = new_face_results
                    result_age = 0
                else:
                    result_age += 1

            if result_age <= DISPLAY_RESULT_FRAMES:
                for result in last_face_results:
                    top, right, bottom, left = result["top"], result["right"], result["bottom"], result["left"]
                    if result["recognized"]:
                        cv2.rectangle(frame, (left, top), (right, bottom), COLOR_GREEN_BGR, 2)
                        label = f"{result['name']} ({result['distance']:.2f})"
                        label_top = max(bottom - 35, 80)
                        cv2.rectangle(frame, (left, label_top), (right, bottom), COLOR_GREEN_BGR, cv2.FILLED)
                        cv2.putText(frame, label, (left + 6, bottom - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_WHITE_BGR, 1, cv2.LINE_AA)
                    else:
                        cv2.rectangle(frame, (left, top), (right, bottom), COLOR_RED_BGR, 2)
                        cv2.putText(frame, "Unknown", (left, max(top - 10, 90)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_RED_BGR, 2, cv2.LINE_AA)

            cv2.rectangle(frame, (0, 0), (frame.shape[1], 80), COLOR_NAVY_BGR, -1)
            cv2.putText(frame, "FACEATTEND", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_GOLD_BGR, 2, cv2.LINE_AA)
            cv2.putText(frame, f"{course_code} | {course_name}", (20, 58),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, COLOR_WHITE_BGR, 1, cv2.LINE_AA)
            cv2.putText(frame, f"Recorded: {len(recorded_students)}", (frame.shape[1] - 180, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_WHITE_BGR, 1, cv2.LINE_AA)

            if time.time() - status_time < 3:
                cv2.rectangle(frame, (20, 95), (min(frame.shape[1] - 20, 650), 135), COLOR_GREEN_BGR, -1)
                cv2.putText(frame, status_message, (30, 122),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_WHITE_BGR, 1, cv2.LINE_AA)

            cv2.putText(frame, "Look at the camera   |   Q = Finish", (20, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_WHITE_BGR, 1, cv2.LINE_AA)

            cv2.imshow("FaceAttend | Attendance", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"): break

    except Exception as e:
        return False, f"Face recognition error:\n{e}"
    finally:
        camera.release()
        cv2.destroyAllWindows()

    if recorded_students:
        return True, (
            f"Attendance completed.\n\n{len(recorded_students)} student(s) recorded:\n"
            + "\n".join(f"• {name}" for name in recorded_students)
        )
    return False, "No new attendance was recorded."