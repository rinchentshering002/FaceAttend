import os
import time

import cv2
import numpy as np
import face_recognition

from dotenv import load_dotenv
from supabase import create_client

from datetime import datetime
from zoneinfo import ZoneInfo

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials are missing!")


# ============================================================
# SUPABASE
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# CAMERA / RECOGNITION SETTINGS
# ============================================================

CAMERA_INDEX = 0

CAMERA_WARMUP_FRAMES = 15

FRAME_SCALE = 0.25

# Recognition happens every 4th frame.
PROCESS_EVERY_N_FRAMES = 4

FACE_MATCH_THRESHOLD = 0.50

# Keep the last recognition result visible.
DISPLAY_RESULT_FRAMES = 12


# ============================================================
# LOAD STUDENTS WITH FACE ENCODINGS
# ============================================================

def load_students():

    response = (
        supabase
        .table("students")
        .select(
            "student_id, name, face_encoding"
        )
        .execute()
    )

    students = []

    for row in response.data:

        encoding_text = row.get("face_encoding")

        if not encoding_text:
            continue

        try:

            values = [
                float(value.strip())
                for value in encoding_text.split(",")
            ]

            if len(values) != 128:
                continue

            students.append({
                "student_id": row["student_id"],
                "name": row["name"],
                "encoding": np.array(
                    values,
                    dtype=np.float64
                )
            })

        except Exception:

            continue

    return students


# ============================================================
# OPEN CAMERA
# ============================================================

def open_camera():

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():

        camera.release()

        return None

    return camera


# ============================================================
# RECORD ATTENDANCE
# ============================================================

def mark_attendance(student, course_id=None):
    """Record attendance once per student, course and day."""

    try:
        now = datetime.now(BHUTAN_TZ)
        today = now.date().isoformat()
        current_time = now.time().isoformat()

        # Check whether attendance already exists today
        query = (
            supabase
            .table("attendance")
            .select("attendance_id")
            .eq("student_id", student["student_id"])
            .eq("attendance_date", today)
        )

        if course_id is not None:
            query = query.eq("course_id", course_id)

        existing = query.limit(1).execute()

        if existing.data:
            return False, f"{student['name']} is already marked Present."

        attendance_data = {
            "student_id": student["student_id"],
            "attendance_date": today,
            "attendance_time": current_time,
            "status": "Present",
        }

        if course_id is not None:
            attendance_data["course_id"] = course_id

        response = (
            supabase
            .table("attendance")
            .insert(attendance_data)
            .execute()
        )

        if response.data:
            return True, f"Attendance recorded for {student['name']}."

        return False, "Attendance could not be recorded."

    except Exception as e:
        print(f"Attendance error: {e}")
        return False, "Database error while recording attendance."

# ============================================================
# FACE RECOGNITION ATTENDANCE
# ============================================================

def take_attendance(
    course_id,
    course_code,
    course_name
):

    """
    Start face-recognition attendance.

    Multiple students can be recorded in one session.

    Press Q to finish.
    """

    # ========================================================
    # LOAD STUDENTS
    # ========================================================

    try:

        known_students = load_students()

    except Exception as e:

        return (
            False,
            f"Could not load students:\n{e}"
        )

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

    print(
        f"Loaded {len(known_students)} students "
        "with valid face encodings."
    )


    # ========================================================
    # OPEN CAMERA
    # ========================================================

    camera = open_camera()

    if camera is None:

        return (
            False,
            "Could not open the external camera.\n\n"
            "Please make sure camera 0 is connected "
            "and not being used by another application."
        )


    # ========================================================
    # CAMERA WARM-UP
    # ========================================================

    for _ in range(CAMERA_WARMUP_FRAMES):

        success, _ = camera.read()

        if not success:
            break


    # ========================================================
    # SESSION VARIABLES
    # ========================================================

    frame_count = 0

    session_marked_ids = set()

    recorded_students = []

    status_message = "Attendance camera ready."

    status_time = time.time()

    # --------------------------------------------------------
    # LAST FACE RECOGNITION RESULTS
    #
    # These stay visible between recognition cycles.
    # --------------------------------------------------------

    last_face_results = []

    result_age = 0


    # ========================================================
    # CAMERA LOOP
    # ========================================================

    try:

        while True:

            # ------------------------------------------------
            # READ FRAME
            # ------------------------------------------------

            success, frame = camera.read()

            if not success:

                time.sleep(0.01)

                continue

            frame_count += 1


            # =================================================
            # FACE RECOGNITION
            # =================================================

            if frame_count % PROCESS_EVERY_N_FRAMES == 0:

                small_frame = cv2.resize(
                    frame,
                    (0, 0),
                    fx=FRAME_SCALE,
                    fy=FRAME_SCALE,
                    interpolation=cv2.INTER_LINEAR
                )

                rgb_small_frame = cv2.cvtColor(
                    small_frame,
                    cv2.COLOR_BGR2RGB
                )

                face_locations = (
                    face_recognition.face_locations(
                        rgb_small_frame,
                        model="hog"
                    )
                )

                new_face_results = []


                # =================================================
                # DETECTED FACES
                # =================================================

                if face_locations:

                    face_encodings = (
                        face_recognition.face_encodings(
                            rgb_small_frame,
                            face_locations,
                            num_jitters=1
                        )
                    )


                    for face_encoding, face_location in zip(
                        face_encodings,
                        face_locations
                    ):

                        # -----------------------------------------
                        # FACE DISTANCE
                        # -----------------------------------------

                        distances = (
                            face_recognition.face_distance(
                                known_encodings,
                                face_encoding
                            )
                        )

                        best_index = int(
                            np.argmin(distances)
                        )

                        best_distance = float(
                            distances[best_index]
                        )

                        student = known_students[best_index]


                        # -----------------------------------------
                        # COORDINATES
                        # -----------------------------------------

                        top, right, bottom, left = face_location

                        top = int(
                            top / FRAME_SCALE
                        )

                        right = int(
                            right / FRAME_SCALE
                        )

                        bottom = int(
                            bottom / FRAME_SCALE
                        )

                        left = int(
                            left / FRAME_SCALE
                        )


                        # -----------------------------------------
                        # RECOGNIZED
                        # -----------------------------------------

                        if best_distance < FACE_MATCH_THRESHOLD:

                            student_id = student["student_id"]

                            new_face_results.append({
                                "top": top,
                                "right": right,
                                "bottom": bottom,
                                "left": left,
                                "recognized": True,
                                "name": student["name"],
                                "distance": best_distance
                            })


                            # ---------------------------------
                            # RECORD ATTENDANCE
                            # ---------------------------------

                            if student_id not in session_marked_ids:

                                success_mark, message = (
                                    mark_attendance(
                                        student,
                                        course_id
                                    )
                                )

                                if success_mark:

                                    session_marked_ids.add(
                                        student_id
                                    )

                                    recorded_students.append(
                                        student["name"]
                                    )

                                    status_message = (
                                        f"✓ {student['name']} "
                                        f"— Attendance Recorded"
                                    )

                                else:

                                    # Prevent repeated database checks for students
                                    # who are already marked present today.
                                    if "already marked Present" in message:
                                        session_marked_ids.add(student_id)

                                    status_message = message

                                status_time = time.time()


                        # -----------------------------------------
                        # UNKNOWN
                        # -----------------------------------------

                        else:

                            new_face_results.append({
                                "top": top,
                                "right": right,
                                "bottom": bottom,
                                "left": left,
                                "recognized": False,
                                "name": "Unknown",
                                "distance": best_distance
                            })


                # ------------------------------------------------
                # UPDATE LAST RESULT
                # ------------------------------------------------

                if new_face_results:

                    last_face_results = new_face_results

                    result_age = 0

                else:

                    # If no face is detected, keep the previous
                    # result briefly instead of making it blink.
                    result_age += 1


            else:

                result_age += 1


            # =================================================
            # DRAW LAST RECOGNITION RESULT
            # =================================================

            if result_age <= DISPLAY_RESULT_FRAMES:

                for result in last_face_results:

                    top = result["top"]
                    right = result["right"]
                    bottom = result["bottom"]
                    left = result["left"]


                    # =================================================
                    # RECOGNIZED FACE
                    # =================================================

                    if result["recognized"]:

                        cv2.rectangle(
                            frame,
                            (left, top),
                            (right, bottom),
                            (35, 130, 75),
                            2
                        )

                        label = (
                            f"{result['name']} "
                            f"({result['distance']:.2f})"
                        )

                        # Keep label inside the frame.
                        label_top = max(
                            bottom - 35,
                            80
                        )

                        cv2.rectangle(
                            frame,
                            (left, label_top),
                            (right, bottom),
                            (35, 130, 75),
                            cv2.FILLED
                        )

                        cv2.putText(
                            frame,
                            label,
                            (
                                left + 6,
                                bottom - 10
                            ),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,
                            (255, 255, 255),
                            1,
                            cv2.LINE_AA
                        )


                    # =================================================
                    # UNKNOWN FACE
                    # =================================================

                    else:

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
                            (
                                left,
                                max(top - 10, 90)
                            ),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,
                            (54, 54, 185),
                            2,
                            cv2.LINE_AA
                        )


            # =================================================
            # HEADER
            # =================================================

            cv2.rectangle(
                frame,
                (0, 0),
                (
                    frame.shape[1],
                    80
                ),
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


            # =================================================
            # COUNTER
            # =================================================

            cv2.putText(
                frame,
                f"Recorded: {len(recorded_students)}",
                (
                    frame.shape[1] - 180,
                    35
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )


            # =================================================
            # STATUS
            # =================================================

            if time.time() - status_time < 3:

                cv2.rectangle(
                    frame,
                    (20, 95),
                    (
                        min(
                            frame.shape[1] - 20,
                            650
                        ),
                        135
                    ),
                    (35, 130, 75),
                    -1
                )

                cv2.putText(
                    frame,
                    status_message,
                    (30, 122),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )


            # =================================================
            # INSTRUCTIONS
            # =================================================

            cv2.putText(
                frame,
                "Look at the camera   |   Q = Finish",
                (
                    20,
                    frame.shape[0] - 20
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )


            # =================================================
            # DISPLAY
            # =================================================

            cv2.imshow(
                "FaceAttend | Attendance",
                frame
            )


            # =================================================
            # KEYBOARD
            # =================================================

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                break


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        return (
            False,
            f"Face recognition error:\n{e}"
        )


    # ========================================================
    # CLEANUP
    # ========================================================

    finally:

        camera.release()

        cv2.destroyAllWindows()

        for _ in range(3):

            cv2.waitKey(1)


    # ========================================================
    # SESSION COMPLETE
    # ========================================================

    if recorded_students:

        return (
            True,
            f"Attendance session completed.\n\n"
            f"{len(recorded_students)} student(s) recorded:\n"
            + "\n".join(
                f"• {name}"
                for name in recorded_students
            )
        )


    return (
        False,
        "Attendance session ended.\n\n"
        "No new attendance was recorded."
    )