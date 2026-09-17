import os
import cv2
import numpy as np
import face_recognition

from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# 1. CONNECT TO SUPABASE
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


# ============================================================
# 2. REGISTER STUDENT FUNCTION
# ============================================================

def register_student(
    student_id,
    name,
    student_class,
    section
):

    # ========================================================
    # CLEAN INPUT
    # ========================================================

    student_id = str(student_id).strip()
    name = str(name).strip()
    student_class = str(student_class).strip()
    section = str(section).strip()


    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    if not student_id:
        return False, "Student ID cannot be empty."

    if not name:
        return False, "Student name cannot be empty."

    if not student_class:
        return False, "Class cannot be empty."

    if not section:
        return False, "Section cannot be empty."


    # ========================================================
    # CHECK IF STUDENT ALREADY EXISTS
    # ========================================================

    try:

        existing_student = (
            supabase
            .table("students")
            .select("student_id")
            .eq("student_id", student_id)
            .execute()
        )

        if existing_student.data:

            return False, (
                f"Student ID '{student_id}' "
                "already exists!"
            )

    except Exception as e:

        return False, (
            "Could not check student ID.\n\n"
            f"{e}"
        )


    # ========================================================
    # OPEN EXTERNAL WEBCAM
    # ========================================================

    # Camera 0 = external webcam
    camera = cv2.VideoCapture(0)


    if not camera.isOpened():

        return False, (
            "Could not open external webcam.\n\n"
            "Make sure your external webcam is connected."
        )


    # ========================================================
    # REGISTRATION INFORMATION
    # ========================================================

    print("\n==========================================")
    print("        STUDENT REGISTRATION")
    print("==========================================")
    print(f"Student ID : {student_id}")
    print(f"Name       : {name}")
    print(f"Class      : {student_class}")
    print(f"Section    : {section}")
    print("------------------------------------------")
    print("Look directly at the camera.")
    print("Make sure only ONE person is visible.")
    print("CLICK INSIDE THE CAMERA WINDOW.")
    print("Press SPACE to capture.")
    print("Press Q to cancel.")
    print("==========================================\n")


    # ========================================================
    # CAPTURE FACE
    # ========================================================

    face_encoding = None


    try:

        while True:

            ret, frame = camera.read()


            # ------------------------------------------------
            # CAMERA FRAME CHECK
            # ------------------------------------------------

            if not ret:

                return False, (
                    "Could not read from external webcam."
                )


            # ------------------------------------------------
            # Convert BGR → RGB
            # ------------------------------------------------

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )


            # ------------------------------------------------
            # Detect faces
            # ------------------------------------------------

            face_locations = (
                face_recognition.face_locations(
                    rgb_frame
                )
            )


            # ------------------------------------------------
            # Draw face rectangles
            # ------------------------------------------------

            for top, right, bottom, left in face_locations:

                cv2.rectangle(
                    frame,
                    (left, top),
                    (right, bottom),
                    (0, 255, 0),
                    2
                )


            # ------------------------------------------------
            # Display number of detected faces
            # ------------------------------------------------

            face_count = len(face_locations)

            cv2.putText(
                frame,
                f"Faces detected: {face_count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )


            # ------------------------------------------------
            # Instructions
            # ------------------------------------------------

            cv2.putText(
                frame,
                "SPACE = Capture | Q = Cancel",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )


            # ------------------------------------------------
            # Show webcam
            # ------------------------------------------------

            cv2.imshow(
                "FaceAttend - Student Registration",
                frame
            )


            # ------------------------------------------------
            # Read keyboard
            # ------------------------------------------------

            key = cv2.waitKey(30) & 0xFF


            # =================================================
            # SPACE = CAPTURE
            # =================================================

            if key == 32:

                # --------------------------------------------
                # No face
                # --------------------------------------------

                if face_count == 0:

                    print(
                        "No face detected. "
                        "Please position your face clearly."
                    )

                    continue


                # --------------------------------------------
                # Multiple faces
                # --------------------------------------------

                if face_count > 1:

                    print(
                        "Multiple faces detected. "
                        "Please make sure only one "
                        "person is visible."
                    )

                    continue


                # --------------------------------------------
                # Exactly one face
                # --------------------------------------------

                encodings = (
                    face_recognition.face_encodings(
                        rgb_frame,
                        face_locations
                    )
                )


                if len(encodings) != 1:

                    print(
                        "Could not generate a valid "
                        "face encoding."
                    )

                    continue


                # --------------------------------------------
                # Store encoding
                # --------------------------------------------

                face_encoding = encodings[0]


                # --------------------------------------------
                # Validate encoding
                # --------------------------------------------

                if len(face_encoding) != 128:

                    print(
                        "Invalid face encoding generated."
                    )

                    face_encoding = None

                    continue


                print("\nFace captured successfully!")
                print("Face encoding generated.")
                print(
                    "Encoding length:",
                    len(face_encoding)
                )

                break


            # =================================================
            # Q = CANCEL
            # =================================================

            elif key == ord("q"):

                return False, "Registration cancelled."


    finally:

        # ====================================================
        # CLOSE CAMERA SAFELY
        # ====================================================

        camera.release()
        cv2.destroyAllWindows()


    # ========================================================
    # CHECK ENCODING
    # ========================================================

    if face_encoding is None:

        return False, (
            "No face encoding was generated."
        )


    if len(face_encoding) != 128:

        return False, (
            "Invalid face encoding."
        )


    # ========================================================
    # CONVERT ENCODING TO TEXT
    # ========================================================

    encoding_text = ",".join(
        str(float(value))
        for value in face_encoding
    )


    # ========================================================
    # PREPARE STUDENT DATA
    # ========================================================

    student_data = {

        "student_id": student_id,

        "name": name,

        "class": student_class,

        "section": section,

        "face_encoding": encoding_text
    }


    # ========================================================
    # SAVE TO SUPABASE
    # ========================================================

    try:

        response = (
            supabase
            .table("students")
            .insert(student_data)
            .execute()
        )


        # ----------------------------------------------------
        # Verify Supabase response
        # ----------------------------------------------------

        if not response.data:

            return False, (
                "Student registration failed.\n"
                "No record was returned by Supabase."
            )


        print("\n==========================================")
        print("   STUDENT REGISTERED SUCCESSFULLY!")
        print("==========================================")

        print(f"Student ID : {student_id}")
        print(f"Name       : {name}")
        print(f"Class      : {student_class}")
        print(f"Section    : {section}")

        print("\nFace encoding saved to Supabase.")
        print("Registration complete!")


        return True, (
            f"Student {name} registered successfully!"
        )


    except Exception as e:

        return False, (
            f"Registration failed.\n\n{e}"
        )