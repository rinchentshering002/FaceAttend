import gradio as gr
from datetime import datetime
from zoneinfo import ZoneInfo
import traceback
import numpy as np

from database import (
    get_all_students,
    get_all_courses,
    mark_attendance
)

from face_engine import (
    load_known_faces,
    recognize_face
)

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")
FACE_MATCH_THRESHOLD = 0.50


def get_course_choices():
    courses = get_all_courses()
    choices = []
    for course in courses:
        label = f"{course.get('course_code', '')} - {course.get('course_name', '')}".strip(" -")
        choices.append((label, course["course_id"]))
    return choices


def scan_and_mark_attendance(image, course_id, already_marked):
    try:
        if image is None: return "⚠ Please capture an image first.", [], already_marked
        if course_id is None: return "⚠ Please select a course.", [], already_marked
        if not isinstance(image, np.ndarray): return "⚠ Invalid image format.", [], already_marked

        students = get_all_students()
        known_encodings, known_students = load_known_faces(students)

        if not known_encodings: return "⚠ No registered face encodings were found.", [], already_marked

        results = recognize_face(image, known_encodings, known_students, threshold=FACE_MATCH_THRESHOLD)
        if not results: return "❌ No registered student was confidently recognized.", [], already_marked

        if already_marked is None: already_marked = set()
        already_marked = set(already_marked)

        now = datetime.now(BHUTAN_TZ)
        attendance_date = now.strftime("%Y-%m-%d")
        attendance_time = now.strftime("%H:%M:%S")

        records = []
        messages = []

        for result in results:
            student = result["student"]
            student_id = student["student_id"]
            session_key = (str(student_id), str(course_id), attendance_date)

            if session_key in already_marked: continue

            attendance_data = {
                "student_id": student_id, "course_id": course_id,
                "attendance_date": attendance_date, "attendance_time": attendance_time,
                "status": "Present"
            }

            try:
                mark_attendance(attendance_data)
                already_marked.add(session_key)
                records.append([student_id, student.get("name", ""), "Present", attendance_time])
                messages.append(f"✓ Attendance recorded for {student.get('name', 'Student')}.")
            except Exception as error:
                error_str = str(error).lower()
                if "duplicate" in error_str or "unique" in error_str:
                    already_marked.add(session_key)
                    messages.append(f"ℹ {student.get('name', 'Student')} is already marked present for this course today.")
                else:
                    messages.append(f"❌ DB Error: {error}")

        message = "All recognized students were already marked in this session." if not messages else "\n".join(messages)
        return message, records, already_marked

    except Exception as e:
        traceback.print_exc()
        return f"🚨 System Error: {str(e)}", [], already_marked


def build_gradio_interface():
    course_choices = get_course_choices()

    # AGGRESSIVE CSS TO FORCE LIGHT MODE INSIDE GRADIO
    custom_css = """
    body, .gradio-container, .main, .wrap { 
        background-color: #F4F7FB !important; 
        color: #1A202C !important;
    }
    .gradio-container * { 
        color: #1A202C !important; 
    }
    .gr-box, .gr-input, .gr-form, input, textarea { 
        background-color: #FFFFFF !important; 
        border: 1px solid #D6E0EC !important; 
    }
    .gr-button { 
        background-color: #2C4A6E !important; 
        border: none !important; 
    }
    .gr-button * { 
        color: white !important; 
    }
    /* Force Markdown Headings to be dark */
    h1, h2, h3, p, span { color: #1A202C !important; }
    """

    with gr.Blocks(
        title="FaceAttend - Smart Attendance",
        theme=gr.themes.Default(), # Default theme is easier to force to light mode
        css=custom_css
    ) as demo:

        gr.Markdown(
            """
            # 📷 FaceAttend | Smart Attendance
            ### Bhutan Digital Attendance System
            Capture a student image to recognize registered students and record attendance.
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                course_dropdown = gr.Dropdown(
                    choices=course_choices, label="Select Course",
                    value=(course_choices[0][1] if course_choices else None),
                    interactive=True
                )
                camera = gr.Image(sources=["webcam"], type="numpy", label="Student Camera", height=350)
                scan_button = gr.Button("Scan & Mark Attendance", variant="primary")

            with gr.Column(scale=1):
                status_output = gr.Textbox(label="Recognition Status", lines=8, interactive=False)
                attendance_output = gr.Dataframe(
                    headers=["Student ID", "Student Name", "Status", "Time"],
                    datatype=["str", "str", "str", "str"],
                    label="Attendance Results", interactive=False
                )

        session_marked = gr.State(set())
        scan_button.click(
            fn=scan_and_mark_attendance,
            inputs=[camera, course_dropdown, session_marked],
            outputs=[status_output, attendance_output, session_marked]
        )

    return demo