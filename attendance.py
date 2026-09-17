import os
import cv2
import numpy as np
import face_recognition

from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials are missing!")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")

# External webcam confirmed by user
CAMERA_INDEX = 0

# Camera resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Smaller frame = much faster face detection
FRAME_SCALE = 0.25

# Process only every Nth frame
PROCESS_EVERY_N_FRAMES = 2

# Face matching threshold
FACE_MATCH_THRESHOLD = 0.50

# How long camera waits for a frame
CAMERA_WARMUP_FRAMES = 5


# ============================================================
# HELPERS
# ============================================================

def bhutan_now():
    return datetime.now(BHUTAN_TZ)


def load_students():
    """
    Load all students and convert face encodings to NumPy arrays
    once before starting recognition.
    """

    try:
        response = (
            supabase
            .table("students")
            .select(
                "student_id, name, class, section, face_encoding"
            )
            .execute()
        )

        students = response.data or []

    except Exception as e:
        raise Exception(
            f"Could not load students from Supabase:\n{e}"
        )

    known_students = []

    for student in students:

        encoding_text = student.get("face_encoding")

        if not encoding_text:
            continue

        try:

            values = [
                float(value.strip())
                for value in str(encoding_text).split(",")
                if value.strip()
            ]

            if len(values) != 128:
                print(
                    f"Skipping {student.get('student_id')}: "
                    f"invalid face encoding."
                )
                continue

            known_students.append({
                "student_id": student.get("student_id"),
                "name": student.get("name", "Unknown"),
                "class": student.get("class", ""),
                "section": student.get("section", ""),
                "encoding": np.array(
                    values,
                    dtype=np.float64
                )
            })

        except (ValueError, TypeError):

            print(
                f"Skipping {student.get('student_id')}: "
                f"invalid face encoding."
            )

    return known_students


# ============================================================
# ATTENDANCE DATABASE
# ============================================================

def mark_attendance(student, course_id):
    """
    Mark attendance only once for the selected course and date.
    """

    student_id = student["student_id"]

    now = bhutan_now()

    today = now.date().isoformat()
    current_time = now.isoformat()

    try:

        # Check whether attendance already exists
        existing = (
            supabase
            .table("attendance")
            .select("student_id")
            .eq("student_id", student_id)
            .eq("course_id", course_id)
            .eq("attendance_date", today)
            .limit(1)
            .execute()
        )

        if existing.data:
            return (
                False,
                f"{student['name']} is already marked "
                f"Present for this course today."
            )

        attendance_data = {
            "student_id": student_id,
            "course_id": course_id,
            "attendance_date": today,
            "status": "Present",
            "check_in_time": current_time
        }

        response = (
            supabase
            .table("attendance")
            .insert(attendance_data)
            .execute()
        )

        if not response.data:
            return (
                False,
                "Attendance could not be recorded."
            )

        return (
            True,
            f"Attendance recorded for {student['name']}."
        )

    except Exception as e:

        return (
            False,
            f"Could not record attendance:\n{e}"
        )


# ============================================================
# CAMERA SETUP
# ============================================================

def open_camera():
    """
    Open external webcam using DirectShow on Windows.
    """

    # CAP_DSHOW usually makes webcam startup faster on Windows.
    camera = cv2.VideoCapture(
        CAMERA_INDEX,
        cv2.CAP_DSHOW
    )

    if not camera.isOpened():

        # Fallback
        camera.release()

        camera = cv2.VideoCapture(
            CAMERA_INDEX
        )

    if not camera.isOpened():
        return None

    # Set resolution
    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )

    # Reduce internal camera buffering
    try:
        camera.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1
        )
    except Exception:
        pass

    return camera


# ============================================================
# FACE RECOGNITION
# ============================================================

def take_attendance(
    course_id,
    course_code,
    course_name
):
    """
    Start optimized face-recognition attendance.
    """

    # --------------------------------------------------------
    # Load students BEFORE opening recognition loop
    # --------------------------------------------------------

    try:

        known_students = load_students()

    except Exception as e:

        return False, str(e)

    if not known_students:

        return (
            False,
            "No students with valid face encodings "
            "were found."
        )

    known_encodings = np.array(
        [
            student["encoding"]
            for student in known_students
        ],
        dtype=np.float64
    )

    # --------------------------------------------------------
    # Open camera
    # --------------------------------------------------------

    camera = open_camera()

    if camera is None:

        return (
            False,
            "Could not open the external camera.\n\n"
            "Please make sure camera 0 is connected "
            "and not being used by another application."
        )

    # --------------------------------------------------------
    # Camera warm-up
    # --------------------------------------------------------

    for _ in range(CAMERA_WARMUP_FRAMES):

        success, _ = camera.read()

        if not success:
            break

    frame_count = 0

    detected_names = []

    try:

        while True:

            success, frame = camera.read()

            if not success:

                continue

            frame_count += 1

            # ------------------------------------------------
            # Process only every Nth frame
            # ------------------------------------------------

            if frame_count % PROCESS_EVERY_N_FRAMES != 0:

                # Still display latest frame
                cv2.imshow(
                    "FaceAttend | Attendance",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):

                    return (
                        False,
                        "Attendance session cancelled."
                    )

                continue

            # ------------------------------------------------
            # Resize for much faster processing
            # ------------------------------------------------

            small_frame = cv2.resize(
                frame,
                (0, 0),
                fx=FRAME_SCALE,
                fy=FRAME_SCALE,
                interpolation=cv2.INTER_LINEAR
            )

            # OpenCV uses BGR
            # face_recognition requires RGB
            rgb_small_frame = cv2.cvtColor(
                small_frame,
                cv2.COLOR_BGR2RGB
            )

            # ------------------------------------------------
            # Detect faces
            # ------------------------------------------------

            face_locations = face_recognition.face_locations(
                rgb_small_frame,
                model="hog"
            )

            if face_locations:

                # ------------------------------------------------
                # Encode detected faces
                # ------------------------------------------------

                face_encodings = face_recognition.face_encodings(
                    rgb_small_frame,
                    face_locations,
                    num_jitters=1
                )

                detected_names = []

                for face_encoding, face_location in zip(
                    face_encodings,
                    face_locations
                ):

                    # ------------------------------------------------
                    # Compare against all registered faces
                    # ------------------------------------------------

                    distances = face_recognition.face_distance(
                        known_encodings,
                        face_encoding
                    )

                    best_index = np.argmin(distances)

                    best_distance = distances[best_index]

                    student = known_students[best_index]

                    if best_distance < FACE_MATCH_THRESHOLD:

                        detected_names.append(
                            student
                        )

                        top, right, bottom, left = face_location

                        # Convert coordinates back to original size
                        top = int(top / FRAME_SCALE)
                        right = int(right / FRAME_SCALE)
                        bottom = int(bottom / FRAME_SCALE)
                        left = int(left / FRAME_SCALE)

                        cv2.rectangle(
                            frame,
                            (left, top),
                            (right, bottom),
                            (35, 130, 75),
                            2
                        )

                        label = (
                            f"{student['name']} "
                            f"({best_distance:.2f})"
                        )

                        cv2.rectangle(
                            frame,
                            (left, bottom - 35),
                            (right, bottom),
                            (35, 130, 75),
                            cv2.FILLED
                        )

                        cv2.putText(
                            frame,
                            label,
                            (left + 6, bottom - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,
                            (255, 255, 255),
                            1,
                            cv2.LINE_AA
                        )

                    else:

                        top, right, bottom, left = face_location

                        top = int(top / FRAME_SCALE)
                        right = int(right / FRAME_SCALE)
                        bottom = int(bottom / FRAME_SCALE)
                        left = int(left / FRAME_SCALE)

                        cv2.rectangle(
                            frame,
                            (left, top),
                            (right, bottom),
                            (54, 54, 185),
                            2
                        )

                        cv2.putText(
                            frame,
                            "Unknown",
                            (left, max(top - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,
                            (54, 54, 185),
                            2,
                            cv2.LINE_AA
                        )

            # ------------------------------------------------
            # Header
            # ------------------------------------------------

            cv2.rectangle(
                frame,
                (0, 0),
                (frame.shape[1], 80),
                (84, 19, 29),
                -1
            )

            cv2.putText(
                frame,
                "FACEATTEND",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (231, 199, 106),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                f"{course_code} | {course_name}",
                (20, 58),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

            # ------------------------------------------------
            # Instructions
            # ------------------------------------------------

            cv2.putText(
                frame,
                "Look at the camera   |   Q = Quit",
                (20, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

            cv2.imshow(
                "FaceAttend | Attendance",
                frame
            )

            # ------------------------------------------------
            # If a student is recognized
            # ------------------------------------------------

            if detected_names:

                # Mark only first recognized student
                student = detected_names[0]

                success_mark, message = mark_attendance(
                    student,
                    course_id
                )

                # Keep camera visible briefly
                cv2.waitKey(700)

                return (
                    success_mark,
                    message
                )

            # ------------------------------------------------
            # Keyboard
            # ------------------------------------------------

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                return (
                    False,
                    "Attendance session cancelled."
                )

    except Exception as e:

        return (
            False,
            f"Face recognition error:\n{e}"
        )

    finally:

        camera.release()

        cv2.destroyAllWindows()

        # Ensure OpenCV windows close
        for _ in range(3):
            cv2.waitKey(1)