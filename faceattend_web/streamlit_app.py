import streamlit as st
import pandas as pd
import face_recognition
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit.components.v1 as components

from database import (
    get_all_students,
    get_all_courses,
    get_all_attendance,
    register_student,
    add_course,
    delete_course
)

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="FaceAttend | Bhutan Digital Attendance",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

BHUTAN_TZ = ZoneInfo("Asia/Thimphu")

# --------------------------------
# CUSTOM DESIGN (FORCED LIGHT MODE)
# --------------------------------

st.markdown("""
<style>
/* Force main background to be light */
[data-testid="stAppViewContainer"], .main, .stApp {
    background-color: #F4F7FB !important;
}

/* FORCE ALL HEADINGS AND TEXT TO BE DARK so they are visible */
.main h1, .main h2, .main h3, .main h4, .main p, .main span, .main div, .main label {
    color: #1A202C !important;
}

/* Sidebar Background */
[data-testid="stSidebar"] {
    background-color: #1E3652 !important;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Hero Banner */
.hero {
    background: linear-gradient(120deg, #1E3652, #4A6D96);
    padding: 28px;
    border-radius: 14px;
    margin-bottom: 25px;
}
.hero h1 {
    color: white !important;
    margin-bottom: 5px;
}
.hero p {
    color: #E7C76A !important;
    margin-bottom: 0;
}

/* Metric Cards */
.metric-card {
    background: white !important;
    border: 1px solid #D6E0EC;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.metric-title {
    color: #6B7280 !important;
    font-size: 14px;
}
.metric-value {
    color: #2C4A6E !important;
    font-size: 28px;
    font-weight: bold;
}

/* Buttons */
.stButton > button {
    background-color: #2C4A6E !important;
    color: white !important;
    border-radius: 8px;
    border: none;
    padding: 10px 24px !important;
    font-weight: bold !important;
}
.stButton > button:hover {
    background-color: #4A6D96 !important;
    color: white !important;
}

/* Tables & Inputs */
div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #1A202C !important; }
div[data-baseweb="popover"] > div, ul[data-testid="stSelectboxVirtualDropdown"] { background-color: #FFFFFF !important; }
ul[data-testid="stSelectboxVirtualDropdown"] li { background-color: #FFFFFF !important; color: #1A202C !important; }
div[data-baseweb="input"] { background-color: #FFFFFF !important; }
div[data-baseweb="input"] input { color: #1A202C !important; }
[data-testid="stDataFrame"] { background-color: #FFFFFF !important; }
[data-testid="stDataFrame"] * { color: #1A202C !important; border-color: #D6E0EC !important; }
</style>
""", unsafe_allow_html=True)


# --------------------------------
# HELPER FUNCTIONS
# --------------------------------

def bhutan_now():
    return datetime.now(BHUTAN_TZ)


def metric_card(title, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def load_data():
    """Load current records from Supabase."""
    students = get_all_students()
    courses = get_all_courses()
    attendance = get_all_attendance()
    return students, courses, attendance


# --------------------------------
# SIDEBAR NAVIGATION
# --------------------------------

with st.sidebar:
    st.markdown("# ༺ FACEATTEND ༻")
    st.markdown("### DIGITAL ATTENDANCE SYSTEM")
    st.markdown("འབྲུག • BHUTAN")
    st.divider()
    page = st.radio("NAVIGATION", ["Dashboard", "Students", "Attendance", "Courses", "Reports"])
    st.divider()
    st.caption("FaceAttend | Bhutan Digital System")
    st.caption("Powered by Streamlit, Gradio & Supabase")


# --------------------------------
# LOAD DATABASE RECORDS
# --------------------------------

try:
    students, courses, attendance = load_data()
except Exception as error:
    st.error(f"Unable to connect to Supabase: {error}")
    st.stop()


# --------------------------------
# DASHBOARD
# --------------------------------

if page == "Dashboard":
    st.markdown("""
    <div class="hero">
        <h1>Welcome to FaceAttend</h1>
        <p>Bhutan Digital Attendance Management System</p>
    </div>
    """, unsafe_allow_html=True)

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
        
        rows = [{
            "Student ID": r.get("student_id"),
            "Student Name": student_map.get(str(r.get("student_id")), "Unknown"),
            "Course": course_map.get(str(r.get("course_id")), "Unknown"),
            "Date": r.get("attendance_date"),
            "Time": r.get("attendance_time"),
            "Status": r.get("status")
        } for r in recent]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No attendance records available yet.")
    st.caption(f"Last viewed: {bhutan_now().strftime('%d %B %Y, %I:%M %p')}")


# --------------------------------
# STUDENTS
# --------------------------------

elif page == "Students":
    st.markdown("## Student Management")
    tab1, tab2 = st.tabs(["Registered Students", "Register Student"])

    with tab1:
        if students:
            student_rows = [{
                "Student ID": s.get("student_id"), "Name": s.get("name"),
                "Class": s.get("class"), "Section": s.get("section"), "Year": s.get("year")
            } for s in students]
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
                            student_data = {
                                "student_id": student_id.strip(), "name": name.strip(),
                                "class": class_name, "section": section.strip(), "year": year,
                                "face_encoding": encoding_string
                            }
                            register_student(student_data)
                            st.success(f"{name} has been registered successfully.")
                            st.rerun()
                    except Exception as error:
                        st.error(f"Registration failed: {error}")


# --------------------------------
# ATTENDANCE
# --------------------------------

elif page == "Attendance":
    st.markdown("## Face Recognition Attendance")
    st.info("The camera interface runs through Gradio. Make sure its service is running before using this page.")
    
    # Gradio iframe
    components.iframe("http://127.0.0.1:7860", height=750, scrolling=True)


# --------------------------------
# COURSES
# --------------------------------

elif page == "Courses":
    st.markdown("## Course Management")
    tab1, tab2 = st.tabs(["Course List & Delete", "Add Course"])

    with tab1:
        if courses:
            course_rows = [{
                "Course ID": c.get("course_id"), "Course Code": c.get("course_code"),
                "Course Name": c.get("course_name"), "Teacher": c.get("teacher")
            } for c in courses]
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
                        add_course({
                            "course_code": course_code.strip(),
                            "course_name": course_name.strip(),
                            "teacher": teacher.strip()
                        })
                        st.success("Course added successfully.")
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not add course: {error}")


# --------------------------------
# REPORTS
# --------------------------------

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

        filtered.append({
            "Attendance ID": record.get("attendance_id"), "Student ID": student_id,
            "Student Name": student_name, "Course": course_name,
            "Date": record.get("attendance_date"), "Time": record.get("attendance_time"),
            "Status": record.get("status")
        })

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