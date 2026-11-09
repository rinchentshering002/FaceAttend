import gradio as gr
from datetime import datetime
from zoneinfo import ZoneInfo
import traceback
import numpy as np

from database import get_all_students, get_all_courses, mark_attendance
from face_engine import load_known_faces, recognize_face

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")
FACE_MATCH_THRESHOLD = 0.50

def get_course_choices():
    courses = get_all_courses()
    choices = []
    for course in courses:
        label = f"{course.get('course_code', '')} - {course.get('course_name', '')}".strip(" -")
        choices.append((label, course["course_id"]))
    return choices

def build_html_table(records):
    """Builds a clean HTML table instead of using Gradio's glitchy Dataframe"""
    if not records:
        return """
        <table class="custom-table">
            <thead><tr><th>Student ID</th><th>Student Name</th><th>Status</th><th>Time</th></tr></thead>
            <tbody><tr><td colspan="4" style="text-align:center; color:#6B7280; font-style:italic; padding: 20px;">No records yet. Capture a photo to scan.</td></tr></tbody>
        </table>
        """
    
    html = """
    <table class="custom-table">
        <thead><tr><th>Student ID</th><th>Student Name</th><th>Status</th><th>Time</th></tr></thead>
        <tbody>
    """
    for r in records:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>"
    html += "</tbody></table>"
    return html

def scan_and_mark_attendance(image, course_id, already_marked):
    print("\n--- NEW SCAN INITIATED ---")
    try:
        if image is None: 
            return "⚠ **Please capture a photo first.** (Click the camera icon on the webcam feed before clicking Scan).", build_html_table([]), already_marked
        if course_id is None: 
            return "⚠ **Please select a course.**", build_html_table([]), already_marked
        if not isinstance(image, np.ndarray): 
            return "⚠ **Invalid image format.**", build_html_table([]), already_marked

        students = get_all_students()
        known_encodings, known_students = load_known_faces(students)

        if not known_encodings: 
            return "⚠ **No registered face encodings were found in the database.**", build_html_table([]), already_marked

        results = recognize_face(image, known_encodings, known_students, threshold=FACE_MATCH_THRESHOLD)
        
        if not results: 
            return "❌ **Face detected, but no registered student was confidently recognized.**", build_html_table([]), already_marked

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

            if session_key in already_marked: 
                records.append([student_id, student.get("name", ""), "Already Present", attendance_time])
                messages.append(f"ℹ **{student.get('name', 'Student')} is already marked present today.**")
                continue

            attendance_data = {
                "student_id": student_id, "course_id": course_id,
                "attendance_date": attendance_date, "attendance_time": attendance_time,
                "status": "Present"
            }

            try:
                mark_attendance(attendance_data)
                already_marked.add(session_key)
                records.append([student_id, student.get("name", ""), "Present", attendance_time])
                messages.append(f"✓ **Attendance recorded for {student.get('name', 'Student')}.**")
            except Exception as error:
                error_str = str(error).lower()
                if "duplicate" in error_str or "unique" in error_str:
                    already_marked.add(session_key)
                    records.append([student_id, student.get("name", ""), "Already Present", attendance_time])
                    messages.append(f"ℹ **{student.get('name', 'Student')} is already marked present today.**")
                else:
                    messages.append(f"❌ **DB Error: {error}**")

        message = "All recognized students were already marked in this session." if not messages else "\n\n".join(messages)
        return message, build_html_table(records), already_marked

    except Exception as e:
        traceback.print_exc()
        return f"🚨 **System Error:**\n\n`{str(e)}`", build_html_table([]), already_marked


def build_gradio_interface():
    course_choices = get_course_choices()

    custom_css = """
    /* 1. FORCE ROOT VARIABLES */
    :root, body, .gradio-container {
        --body-background-fill: #F4F7FB !important;
        --background-fill-primary: #FFFFFF !important;
        --background-fill-secondary: #FFFFFF !important;
        --border-color-primary: #D6E0EC !important;
        --body-text-color: #1A202C !important;
    }
    
    /* 2. FORCE EVERYTHING TO LIGHT MODE */
    body, .gradio-container, .main, .wrap, .contain { background-color: #F4F7FB !important; }
    .block, .form, .gr-box, .gr-input, .panel {
        background-color: #FFFFFF !important;
        border: 1px solid #D6E0EC !important;
        box-shadow: none !important;
    }

    /* 3. KILL THE PURPLE/BLUE LABEL PILLS */
    .gradio-container label, .gradio-container label > span,
    .gradio-container .label-wrap, .gradio-container .block-info {
        background-color: transparent !important;
        background: none !important;
        color: #1A202C !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-bottom: 5px !important;
        font-weight: bold !important;
    }

    /* 4. FIX THE DROPDOWN MENU */
    .gradio-container input, .gradio-container .wrap-inner {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
        border: 1px solid #D6E0EC !important;
    }
    ul.options, .options, .dropdown-menu, [role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D6E0EC !important;
    }
    li, .item, [role="option"] {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
    }
    li:hover, .item:hover, [role="option"]:hover {
        background-color: #E8EFF7 !important;
        color: #1A202C !important;
    }

    /* 5. CUSTOM HTML TABLE STYLING */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
        background-color: #FFFFFF;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #D6E0EC;
    }
    .custom-table th {
        background-color: #E8EFF7;
        color: #1A202C;
        text-align: left;
        padding: 12px;
        border-bottom: 2px solid #D6E0EC;
        font-weight: bold;
    }
    .custom-table td {
        background-color: #FFFFFF;
        color: #1A202C;
        padding: 12px;
        border-bottom: 1px solid #D6E0EC;
    }
    
    /* 6. FIX WEBCAM AREA */
    .gradio-container .image-container, .gradio-container [data-testid="image"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #D6E0EC !important;
    }
    .gradio-container .image-container button {
        background-color: #FFFFFF !important; 
        border: 1px solid #D6E0EC !important;
    }
    .gradio-container .image-container button svg {
        fill: #1A202C !important; 
        stroke: #1A202C !important;
    }

    /* 7. HIDE LOADING & FOOTER */
    .gradio-container .pending, .gradio-container .generating, .progress-bar { display: none !important; }
    .footer { display: none !important; }

    .gr-button { background-color: #2C4A6E !important; border: none !important; color: white !important; }
    """

    with gr.Blocks(title="FaceAttend AI", theme=gr.themes.Base(), css=custom_css) as demo:
        
        gr.Markdown(
            """
            # 📷 FaceAttend | Smart Attendance
            ### Bhutan Digital Attendance System
            
            **Instructions:**
            1. Select the correct course from the dropdown.
            2. Look directly at the camera and **CLICK THE CAMERA ICON** to take a photo.
            3. Click **Scan & Mark Attendance**.
            """
        )

        with gr.Row():
            with gr.Column(scale=1, min_width=350):
                course_dropdown = gr.Dropdown(
                    choices=course_choices, label="Select Course",
                    value=(course_choices[0][1] if course_choices else None),
                    interactive=True
                )
                camera = gr.Image(sources=["webcam"], type="numpy", label="Student Camera", height=350)
                scan_button = gr.Button("Scan & Mark Attendance", variant="primary")

            with gr.Column(scale=1, min_width=350):
                status_output = gr.Markdown(value="*Waiting for scan...*", label="Recognition Status")
                
                # Replaced Dataframe with HTML component
                attendance_output = gr.HTML(value=build_html_table([]), label="Attendance Results")

        session_marked = gr.State(set())
        
        scan_button.click(
            fn=scan_and_mark_attendance,
            inputs=[camera, course_dropdown, session_marked],
            outputs=[status_output, attendance_output, session_marked],
            show_progress=False
        )

    return demo