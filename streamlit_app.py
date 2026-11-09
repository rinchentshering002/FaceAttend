import streamlit as st
import pandas as pd
import face_recognition
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

from database import (
    get_all_students, get_all_courses, get_all_attendance,
    register_student, add_course, delete_course
)

# PAGE CONFIGURATION
st.set_page_config(
    page_title="FaceAttend | Bhutan Digital Attendance",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")

# PROFESSIONAL CUSTOM DESIGN
st.markdown("""
<style>
/* Main Background */
[data-testid="stAppViewContainer"], .main, .stApp { background-color: #F4F7FB !important; }
.main h1, .main h2, .main h3, .main h4, .main p, .main span, .main div, .main label { color: #1A202C !important; }

/* Sidebar Background */
[data-testid="stSidebar"] { background-color: #1E3652 !important; }
[data-testid="stSidebar"] * { color: white !important; }

/* --- PROFESSIONAL SIDEBAR NAVIGATION --- */
[data-testid="stSidebar"] div[role="radiogroup"] { gap: 5px; }
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 10px 15px;
    border-radius: 8px;
    transition: background-color 0.2s ease;
    cursor: pointer;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #2C4A6E;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none; /* Hides the default radio circle */
}
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
    background-color: #2C4A6E;
    font-weight: bold;
}

/* Hero Banner */
.hero { background: linear-gradient(120deg, #1E3652, #4A6D96); padding: 28px; border-radius: 14px; margin-bottom: 25px; }
.hero h1 { color: white !important; margin-bottom: 5px; }
.hero p { color: #E7C76A !important; margin-bottom: 0; }

/* Metric Cards */
.metric-card { background: white !important; border: 1px solid #D6E0EC; border-radius: 12px; padding: 20px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.metric-title { color: #6B7280 !important; font-size: 14px; }
.metric-value { color: #2C4A6E !important; font-size: 28px; font-weight: bold; }

/* Custom Feature Cards (Home Page) */
.feature-card {
    background: #FFFFFF;
    border: 1px solid #D6E0EC;
    border-left: 4px solid #2C4A6E;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    height: 100%;
    margin-bottom: 15px;
}
.feature-card h4 { color: #2C4A6E !important; margin-top: 0; margin-bottom: 10px; font-size: 16px; }
.feature-card p { color: #4A5568 !important; font-size: 14px; margin-bottom: 0; line-height: 1.5; }

/* Timeline Steps (Home Page) */
.step-box {
    text-align: center;
    padding: 15px;
    background: #FFFFFF;
    border-radius: 8px;
    border: 1px dashed #2C4A6E;
    height: 100%;
}
.step-number {
    background: #2C4A6E;
    color: white;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-bottom: 10px;
}

/* Buttons & Inputs */
.stButton > button { background-color: #2C4A6E !important; color: white !important; border-radius: 8px; border: none; padding: 10px 24px !important; font-weight: bold !important; }
.stButton > button:hover { background-color: #4A6D96 !important; color: white !important; }
div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #1A202C !important; }
div[data-baseweb="input"] input { color: #1A202C !important; }
[data-testid="stDataFrame"] * { color: #1A202C !important; border-color: #D6E0EC !important; }
</style>
""", unsafe_allow_html=True)

def bhutan_now(): return datetime.now(BHUTAN_TZ)

def metric_card(title, value):
    st.markdown(f'<div class="metric-card"><div class="metric-title">{title}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

def load_data():
    return get_all_students(), get_all_courses(), get_all_attendance()

# SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("# ༺ FACEATTEND ༻")
    st.markdown("### PROJECT DOCUMENTATION")
    st.divider()
    page = st.radio("NAVIGATION", [
        "Home / Overview",
        "Documentation & Setup",
        "Informative Resources",
        "Live Dashboard",
        "Students",
        "Attendance (Live Demo)",
        "Courses",
        "Reports"
    ])
    st.divider()
    st.caption("Bhutan Digital System")
    st.caption("Powered by Streamlit & Gradio")

try:
    students, courses, attendance = load_data()
except Exception as error:
    st.error(f"Unable to connect to Supabase: {error}")
    st.stop()

# ==========================================
# 1. HOME / OVERVIEW (COMPLETE RUBRIC DETAILS)
# ==========================================
if page == "Home / Overview":
    st.markdown('<div class="hero"><h1>System Overview</h1><p>Bhutan Digital Attendance Management System</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Background & Problem Statement
    In traditional classroom settings at the Royal University of Bhutan, taking attendance for large cohorts often consumes valuable teaching time. Paper registers and manual roll calls are not only slow but are also vulnerable to proxy attendance and human error during data entry. Furthermore, converting physical registers into digital spreadsheets introduces another layer of potential mistakes.
    
    **FaceAttend** was developed to solve this exact issue. By utilizing a camera-assisted approach with Artificial Intelligence, we eliminate manual data entry. The system detects a student's face, generates a 128-dimensional encoding, and compares it against a secure cloud database to log attendance instantly with accurate Bhutan timestamps.
    """)

    st.markdown("---")

    # KEY FEATURES (Custom Cards)
    st.markdown("### Core Capabilities")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>AI Face Matching</h4>
            <p>Uses Dlib's HOG detector and Euclidean distance matching (Threshold: 0.50) to ensure accurate student identification.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>Cloud Synchronization</h4>
            <p>All student data and attendance records are securely synchronized in real-time with a Supabase PostgreSQL database.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>Automated Reporting</h4>
            <p>Generates accurate daily reports with Bhutan Time timestamps. Administrators can filter data and export directly to CSV.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # HOW IT WORKS (Visual Timeline)
    st.markdown("### System Workflow")
    w_col1, w_col2, w_col3, w_col4 = st.columns(4)
    
    with w_col1:
        st.markdown('<div class="step-box"><div class="step-number">1</div><h5>Registration</h5><p style="font-size:12px; color:#6B7280;">Student face is captured via webcam.</p></div>', unsafe_allow_html=True)
    with w_col2:
        st.markdown('<div class="step-box"><div class="step-number">2</div><h5>Encoding</h5><p style="font-size:12px; color:#6B7280;">AI extracts a 128-D facial embedding.</p></div>', unsafe_allow_html=True)
    with w_col3:
        st.markdown('<div class="step-box"><div class="step-number">3</div><h5>Recognition</h5><p style="font-size:12px; color:#6B7280;">Live camera scans and compares faces.</p></div>', unsafe_allow_html=True)
    with w_col4:
        st.markdown('<div class="step-box"><div class="step-number">4</div><h5>Logging</h5><p style="font-size:12px; color:#6B7280;">Attendance is securely saved to the cloud.</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # TECH STACK & TEAM ROLES (Addresses Criteria 6: Teamwork)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Development Stack")
        st.markdown("""
        * **Frontend Interfaces:** Tkinter (Desktop), Streamlit (Web), Gradio (AI Demo)
        * **Computer Vision:** OpenCV, Dlib, face_recognition
        * **Backend & Database:** Python 3.13, Supabase (PostgreSQL)
        * **Data Processing:** NumPy, pandas
        """)
        
    with col2:
        st.markdown("#### Project Team & Roles")
        st.markdown("""
        **B.Ed. IT (D) - Samtse College of Education**
        
        * **Rinchen Tshering** — Lead Developer (Database & AI Integration)
        * **Tandin Penjor** — Backend Developer (Supabase & Python Logic)
        * **Pema Yangki** — UI/UX Designer (Tkinter & Streamlit Interfaces)
        * **Tashi Lhamo** — QA & Documentation (Testing & Project Report)
        * **Sangay Choden** — Web Developer (Gradio Interface & CSV Exports)
        """)

# ==========================================
# 2. DOCUMENTATION & SETUP
# ==========================================
elif page == "Documentation & Setup":
    st.markdown("## Documentation & Setup")
    
    st.markdown("### 1. Configuration Requirements")
    st.write("FaceAttend loads its connection information using `python-dotenv`. Create a `.env` file in the root directory:")
    st.code("""
    SUPABASE_URL=your_supabase_project_url
    SUPABASE_KEY=your_supabase_anon_key
    """, language="env")
    
    st.markdown("### 2. Database Design & Duplicate Prevention")
    st.write("Duplicate attendance is prevented at the database level, which keeps the recognition loop fast. A unique index is applied in Supabase:")
    st.code("""
    CREATE UNIQUE INDEX attendance_unique_idx 
    ON attendance (student_id, course_id, attendance_date);
    """, language="sql")

    st.divider()
    st.markdown("### 3. Face Recognition Implementation")
    st.write("""
    1. A 128-dimensional facial encoding is generated during registration and saved.
    2. During attendance, frames are continuously captured.
    3. Every 4th frame is scaled down to 25% size to optimise processing speed.
    4. Detected faces are converted to RGB and encoded.
    5. The Euclidean distance between the live encoding and all registered encodings is calculated.
    6. If the smallest distance is below `FACE_MATCH_THRESHOLD` (0.50), it is considered a match.
    """)

    st.divider()
    # Addresses Criteria 3: Technical Understanding & Challenges
    st.markdown("### 4. Technical Challenges Overcome")
    
    with st.expander("Challenge 1: Dlib Memory Alignment Bug on Windows"):
        st.write("""
        **Problem:** The standard `dlib` wheel for Python 3.12 on Windows threw a C++ memory error when attempting to encode faces directly from OpenCV frames.
        
        **Solution:** We utilized `dlib-bin` (a pre-compiled PyPI package) and implemented a temporary file workaround. The captured frame is saved to disk (`temp_registration.jpg`) and loaded using `face_recognition.load_image_file()`, which ensures reliable encoding generation.
        """)
        
    with st.expander("Challenge 2: Browser Camera Permissions in Web Apps"):
        st.write("""
        **Problem:** When embedding the Gradio AI interface inside Streamlit via an iframe, modern browsers blocked camera access (`getUserMedia` error) due to security policies.
        
        **Solution:** We utilized Streamlit's HTML component to manually construct the iframe, explicitly adding the `allow="camera; microphone"` attribute to grant the necessary hardware permissions.
        """)

# ==========================================
# 3. INFORMATIVE RESOURCES
# ==========================================
elif page == "Informative Resources":
    st.markdown("## Credible Informative Resources")
    st.write("These are the official documentation websites used during development to ensure industry-standard implementation:")
    st.markdown("""
    * **[Gradio Official Documentation](https://www.gradio.app/docs/)** - For the AI camera interface and web components.
    * **[Streamlit Official Documentation](https://docs.streamlit.io/)** - For the web dashboard, dataframes, and layout configuration.
    * **[Face Recognition Library (GitHub)](https://github.com/ageitgey/face_recognition)** - For the Dlib HOG AI models and distance calculations.
    * **[Supabase Python Client Docs](https://supabase.com/docs/reference/python/introduction)** - For database integration, inserts, and row-level queries.
    * **[OpenCV Documentation](https://docs.opencv.org/4.x/)** - For real-time camera frame processing and color conversions.
    * **[Python 3.13 Docs](https://docs.python.org/3.13/)** - Core programming language reference.
    """)

# ==========================================
# 4. LIVE DASHBOARD
# ==========================================
elif page == "Live Dashboard":
    st.markdown('<div class="hero"><h1>Welcome to FaceAttend</h1><p>Bhutan Digital Attendance Management System</p></div>', unsafe_allow_html=True)
    today = bhutan_now().date().isoformat()
    today_records = [r for r in attendance if r.get("attendance_date") == today]
    present_today = sum(1 for r in today_records if r.get("status") == "Present")

    col1, col2, col3, col4 = st.columns(4)
    with col1: metric_card("Total Students", len(students))
    with col2: metric_card("Total Courses", len(courses))
    with col3: metric_card("Today's Attendance", len(today_records))
    with col4: metric_card("Present Today", present_today)

    st.markdown("### Recent Attendance")
    if attendance:
        student_map = {str(s["student_id"]): s.get("name", "") for s in students}
        course_map = {str(c["course_id"]): c.get("course_name", "") for c in courses}
        recent = sorted(attendance, key=lambda i: (str(i.get("attendance_date", "")), str(i.get("attendance_time", ""))), reverse=True)[:10]
        rows = [{"Student ID": r.get("student_id"), "Student Name": student_map.get(str(r.get("student_id")), "Unknown"), "Course": course_map.get(str(r.get("course_id")), "Unknown"), "Date": r.get("attendance_date"), "Time": r.get("attendance_time"), "Status": r.get("status")} for r in recent]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No attendance records available yet.")

# ==========================================
# 5. STUDENTS
# ==========================================
elif page == "Students":
    st.markdown("## Student Management")
    tab1, tab2 = st.tabs(["Registered Students", "Register Student"])

    with tab1:
        if students:
            student_rows = [{"Student ID": s.get("student_id"), "Name": s.get("name"), "Class": s.get("class"), "Section": s.get("section"), "Year": s.get("year")} for s in students]
            st.dataframe(pd.DataFrame(student_rows), use_container_width=True, hide_index=True)
            st.download_button("Download Student List", pd.DataFrame(student_rows).to_csv(index=False), file_name="faceattend_students.csv", mime="text/csv")
        else:
            st.info("No students registered yet.")

    with tab2:
        st.markdown("### Register a New Student")
        with st.form("student_registration"):
            student_id = st.text_input("Student ID")
            name = st.text_input("Full Name")
            class_name = st.selectbox("Programme", ["B.Ed IT", "B.Ed Geo/Eng", "B.Ed His/Eng", "B.Ed Bio/Chem", "B.Ed Phy/Math"])
            section = st.text_input("Section")
            year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
            face_image = st.camera_input("Capture Student Face")
            submitted = st.form_submit_button("Register Student")

            if submitted:
                if not student_id or not name or not section:
                    st.error("Please complete all student details.")
                elif face_image is None:
                    st.error("Please capture a student face image.")
                elif any(str(s.get("student_id")) == student_id.strip() for s in students):
                    st.error("This student ID is already registered.")
                else:
                    try:
                        image = face_recognition.load_image_file(face_image)
                        locations = face_recognition.face_locations(image, model="hog")
                        encodings = face_recognition.face_encodings(image, locations)
                        if len(encodings) != 1:
                            st.error("Please capture an image containing exactly one detectable face.")
                        else:
                            encoding_string = ",".join(map(str, encodings[0].tolist()))
                            student_data = {"student_id": student_id.strip(), "name": name.strip(), "class": class_name, "section": section.strip(), "year": year, "face_encoding": encoding_string}
                            register_student(student_data)
                            st.success(f"{name} has been registered successfully.")
                            st.rerun()
                    except Exception as error:
                        st.error(f"Registration failed: {error}")

# ==========================================
# 6. ATTENDANCE (LIVE DEMO - GRADIO IFRAME FIX)
# ==========================================
elif page == "Attendance (Live Demo)":
    st.markdown("## Face Recognition Attendance")
    st.info("The camera interface runs through Gradio. Ensure you have clicked 'Allow' when the browser asks for camera permissions.")
    
    # Custom iframe with explicit camera permission to fix 'getUserMedia' error
    components.html(
        """
        <iframe 
            src="http://127.0.0.1:7860" 
            width="100%" 
            height="750" 
            style="border:none; border-radius: 8px;"
            allow="camera; microphone; display-capture; autoplay"
        ></iframe>
        """,
        height=770,
    )

# ==========================================
# 7. COURSES
# ==========================================
elif page == "Courses":
    st.markdown("## Course Management")
    tab1, tab2 = st.tabs(["Course List & Delete", "Add Course"])

    with tab1:
        if courses:
            course_rows = [{"Course ID": c.get("course_id"), "Course Code": c.get("course_code"), "Course Name": c.get("course_name"), "Teacher": c.get("teacher")} for c in courses]
            st.dataframe(pd.DataFrame(course_rows), use_container_width=True, hide_index=True)
            st.markdown("---")
            st.markdown("### Delete Course")
            st.warning("Deleting a course may affect existing attendance records.")
            del_options = {f"{c['course_code']} - {c['course_name']}": c['course_id'] for c in courses}
            selected_del = st.selectbox("Select a course to delete", list(del_options.keys()))
            
            if st.button("Delete Selected Course"):
                try:
                    delete_course(del_options[selected_del])
                    st.success("Course deleted successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not delete course: {e}")
        else:
            st.info("No courses available.")

    with tab2:
        with st.form("add_course_form"):
            course_code = st.text_input("Course Code")
            course_name = st.text_input("Course Name")
            teacher = st.text_input("Teacher Name")
            submitted = st.form_submit_button("Add Course")
            if submitted:
                if not course_code or not course_name or not teacher:
                    st.error("Please complete all course details.")
                else:
                    try:
                        add_course({"course_code": course_code.strip(), "course_name": course_name.strip(), "teacher": teacher.strip()})
                        st.success("Course added successfully.")
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not add course: {error}")

# ==========================================
# 8. REPORTS
# ==========================================
elif page == "Reports":
    st.markdown("## Attendance Reports")
    student_map = {str(s["student_id"]): s.get("name", "") for s in students}
    course_map = {str(c["course_id"]): c.get("course_name", "") for c in courses}

    col1, col2 = st.columns(2)
    with col1: selected_date = st.date_input("Attendance Date", value=bhutan_now().date())
    with col2:
        course_options = ["All Courses"] + [str(c["course_id"]) for c in courses]
        selected_course = st.selectbox("Course", course_options, format_func=lambda v: "All Courses" if v == "All Courses" else course_map.get(v, v))

    search = st.text_input("Search by Student ID, Name or Course").strip().lower()
    filtered = []

    for record in attendance:
        if record.get("attendance_date") != selected_date.isoformat(): continue
        if selected_course != "All Courses" and str(record.get("course_id")) != selected_course: continue

        student_id = str(record.get("student_id", ""))
        student_name = student_map.get(student_id, "")
        course_name = course_map.get(str(record.get("course_id")), "Unknown")
        searchable = (student_id + " " + student_name + " " + course_name).lower()
        if search and search not in searchable: continue

        filtered.append({"Attendance ID": record.get("attendance_id"), "Student ID": student_id, "Student Name": student_name, "Course": course_name, "Date": record.get("attendance_date"), "Time": record.get("attendance_time"), "Status": record.get("status")})

    total = len(filtered)
    present = sum(1 for r in filtered if r["Status"] == "Present")

    col1, col2, col3 = st.columns(3)
    with col1: metric_card("Total Records", total)
    with col2: metric_card("Present", present)
    with col3:
        if selected_course == "All Courses" and not search:
            present_ids = {str(r.get("student_id")) for r in attendance if r.get("attendance_date") == selected_date.isoformat() and r.get("status") == "Present"}
            absent = sum(1 for s in students if str(s.get("student_id")) not in present_ids)
            metric_card("Not Recorded Present", absent)
        else:
            metric_card("Not Recorded Present", "—")

    if filtered:
        report_df = pd.DataFrame(filtered)
        st.dataframe(report_df, use_container_width=True, hide_index=True)
        st.download_button("Export Attendance Report (CSV)", report_df.to_csv(index=False), file_name=f"attendance_{selected_date}.csv", mime="text/csv")
    else:
        st.info("No matching attendance records found.")