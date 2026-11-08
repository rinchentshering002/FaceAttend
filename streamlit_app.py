"""
FaceAttend — Streamlit version (Fixed UI, Light Mode, & Working Navigation)
Run:  streamlit run streamlit_app.py
"""
import os
import numpy as np
import pandas as pd
import streamlit as st
import face_recognition
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from supabase import create_client

# ---------------- CONFIG ----------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase credentials missing in .env"); st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BHUTAN_TZ = ZoneInfo("Asia/Thimphu")
FACE_MATCH_THRESHOLD = 0.50

st.set_page_config(page_title="FaceAttend | Bhutan Digital Attendance System", page_icon="📷", layout="wide", initial_sidebar_state="expanded")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* Hide Streamlit default header/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main background */
.stApp { background-color: #F4F7FB; }

/* Sidebar Background */
[data-testid="stSidebar"] {
    background-color: #1E3652 !important;
    width: 260px !important;
    border-right: 1px solid #2C4A6E;
}

/* Sidebar Radio Navigation */
[data-testid="stSidebar"] .stRadio > div { gap: 0px; }
[data-testid="stSidebar"] .stRadio label {
    padding: 12px 20px !important;
    color: #DCE6F0 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    border-left: 4px solid transparent !important;
    transition: all 0.2s;
    cursor: pointer;
    border-radius: 0 !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #2C4A6E !important;
    color: white !important;
}
[data-testid="stSidebar"] .stRadio label > div:first-child { display: none !important; }
[data-testid="stSidebar"] .stRadio label[data-checked="true"],
[data-testid="stSidebar"] .stRadio label[aria-checked="true"] {
    background-color: #2C4A6E !important;
    color: white !important;
    border-left: 4px solid #E7C76A !important;
}

/* Top Bar */
.top-bar {
    background-color: #FFFFFF;
    padding: 15px 30px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    font-weight: bold;
    color: #2C4A6E;
    font-size: 14px;
    border-bottom: 1px solid #D6E0EC;
    margin-bottom: 20px;
    border-radius: 4px;
}

/* Hero Banner */
.hero-banner {
    background-color: #2C4A6E;
    padding: 25px 30px;
    border-radius: 4px;
    position: relative;
    color: white;
    margin-bottom: 25px;
}
.hero-pattern { color: #E7C76A; font-size: 14px; letter-spacing: 8px; margin-bottom: 15px; }
.hero-title { font-size: 32px; font-weight: bold; margin-bottom: 5px; }
.hero-subtitle { color: #DCE6F0; font-size: 15px; }
.hero-date { position: absolute; right: 30px; top: 30px; text-align: right; color: #E7C76A; font-weight: bold; font-size: 16px; line-height: 1.4; }

/* Custom Cards */
.custom-card {
    background-color: #FFFFFF;
    border: 1px solid #D6E0EC;
    border-radius: 6px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* Stat Cards */
.stat-card { background-color: #FFFFFF; border: 1px solid #D6E0EC; border-radius: 6px; padding: 20px; }
.stat-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.stat-title { color: #6B7280; font-size: 13px; font-weight: bold; letter-spacing: 0.5px; }
.stat-value { color: #1A202C; font-size: 36px; font-weight: bold; margin-bottom: 5px; }
.stat-subtitle { color: #6B7280; font-size: 13px; }
.stat-icon { padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 14px; }

/* Main Buttons */
.stButton>button {
    background-color: #2C4A6E !important;
    color: white !important;
    border-radius: 4px !important;
    border: none !important;
    padding: 10px 24px !important;
    font-weight: bold !important;
    width: 100%;
}
.stButton>button:hover { background-color: #1E3652 !important; }

/* --- FIX TEXT AND DROPDOWN COLORS --- */
h1, h2, h3, h4, p, span, div, label { color: #1A202C !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] div { color: white !important; }
[data-testid="stSidebar"] .stRadio label div { color: inherit !important; }

/* Force selectbox to be white with dark text */
div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #1A202C !important; border: 1px solid #D6E0EC !important; }
div[data-baseweb="popover"] div, ul[role="listbox"], li { background-color: #FFFFFF !important; color: #1A202C !important; }
li:hover { background-color: #F4F7FB !important; }

/* Fix date input */
div[data-testid="stDateInput"] input { color: #1A202C !important; background-color: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- NAVIGATION LOGIC ----------------
nav_options = ["◈ Dashboard", "◉ Students", "◎ Attendance", "▣ Courses", "◫ Reports", "⚙ Settings"]
if "page_idx" not in st.session_state: st.session_state.page_idx = 0
def go_to_page(page_name):
    st.session_state.page_idx = nav_options.index(page_name)
    st.rerun()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown('<div style="text-align: center; padding: 20px 0 10px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="color: #E7C76A; font-size: 22px; font-weight: bold; letter-spacing: 2px;">༺ FACEATTEND ༻</div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #DCE6F0; font-size: 10px; font-weight: bold; margin-top: 5px;">DIGITAL ATTENDANCE SYSTEM</div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #E7C76A; font-size: 14px; font-weight: bold; margin-top: 10px;">འབྲུག • BHUTAN</div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #C99A2E; font-size: 12px; letter-spacing: 5px; margin-top: 15px;">◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    selected_page = st.radio("", nav_options, index=st.session_state.page_idx, label_visibility="collapsed")
    st.session_state.page_idx = nav_options.index(selected_page)

# ---------------- HELPERS ----------------
@st.cache_data(ttl=10, show_spinner=False)
def load_students():
    resp = supabase.table("students").select("student_id, name, face_encoding").execute()
    students = []
    for row in resp.data or []:
        enc = row.get("face_encoding")
        if not enc: continue
        try:
            v = [float(x.strip()) for x in enc.split(",")]
            if len(v) == 128:
                students.append({"student_id": row["student_id"], "name": row["name"], "encoding": np.array(v, dtype=np.float64)})
        except Exception: continue
    return students

@st.cache_data(ttl=10, show_spinner=False)
def load_courses():
    return supabase.table("courses").select("*").order("course_id").execute().data or []

def bhutan_now(): return datetime.now(BHUTAN_TZ)

def match_face(img_array, known_students):
    if img_array is None or not known_students: return None, 1.0
    rgb = np.ascontiguousarray(img_array[..., :3], dtype=np.uint8)
    locs = face_recognition.face_locations(rgb, model="hog")
    if len(locs) == 0 or len(locs) > 1: return None, 1.0
    enc = face_recognition.face_encodings(rgb, locs, num_jitters=1)[0]
    known_encs = np.array([s["encoding"] for s in known_students])
    dists = face_recognition.face_distance(known_encs, enc)
    best = int(np.argmin(dists))
    best_dist = float(dists[best])
    if best_dist < FACE_MATCH_THRESHOLD: return known_students[best], best_dist
    return None, best_dist

def mark_present(student, course_id):
    now = bhutan_now()
    payload = {"student_id": student["student_id"], "attendance_date": now.date().isoformat(), "attendance_time": now.time().isoformat(), "status": "Present", "course_id": course_id}
    try:
        supabase.table("attendance").insert(payload).execute()
        return True, f"✓ {student['name']} marked Present."
    except Exception as e:
        msg = str(e).lower()
        if "duplicate" in msg or "unique" in msg: return False, f"{student['name']} is already marked Present today."
        return False, f"DB error: {e}"

# ---------------- TOP BAR ----------------
now = bhutan_now()
st.markdown(f"""
<div class="top-bar">
    BHUTAN TIME &nbsp;•&nbsp; {now.strftime('%d %b %Y')} &nbsp;|&nbsp; {now.strftime('%I:%M:%S %p')}
</div>
""", unsafe_allow_html=True)

# ---------------- PAGES ----------------
current_page = nav_options[st.session_state.page_idx]

if current_page == "◈ Dashboard":
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-pattern">◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆</div>
        <div style="color: #E7C76A; font-size: 15px; font-weight: bold;">Kuzuzangpo La! 👋</div>
        <div class="hero-title">Attendance Dashboard</div>
        <div class="hero-subtitle">A smarter and more reliable way to manage student attendance.</div>
        <div class="hero-date">{now.strftime('%A')}<br>{now.strftime('%d %B %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

    students = load_students()
    today = bhutan_now().date().isoformat()
    recs = (supabase.table("attendance").select("student_id, status").eq("attendance_date", today).execute().data or [])
    present_ids = {r["student_id"] for r in recs if r.get("status") == "Present"}
    present, total = len(present_ids), len(students)
    absent = max(total - present, 0)
    rate = (present / total * 100) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="stat-card"><div class="stat-header"><span class="stat-icon" style="background-color: #2C4A6E;">●</span><span class="stat-title">TOTAL STUDENTS</span></div><div class="stat-value">{total}</div><div class="stat-subtitle">Registered students</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card"><div class="stat-header"><span class="stat-icon" style="background-color: #23824B;">✓</span><span class="stat-title">PRESENT TODAY</span></div><div class="stat-value">{present}</div><div class="stat-subtitle">Face attendance recorded</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-card"><div class="stat-header"><span class="stat-icon" style="background-color: #B93636;">×</span><span class="stat-title">ABSENT TODAY</span></div><div class="stat-value">{absent}</div><div class="stat-subtitle">No attendance record</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="stat-card"><div class="stat-header"><span class="stat-icon" style="background-color: #C99A2E;">%</span><span class="stat-title">ATTENDANCE RATE</span></div><div class="stat-value">{rate:.1f}%</div><div class="stat-subtitle">Today\'s attendance</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c_mid1, c_mid2 = st.columns([1, 1])
    with c_mid1:
        st.markdown(f"""
        <div class="custom-card">
            <h3 style="margin-top: 0; color: #1A202C;">Today's Attendance</h3>
            <p style="color: #6B7280; font-size: 14px;">{present} of {total} students present</p>
            <div style="background-color: #DCE6F0; height: 14px; border-radius: 2px; width: 100%; margin: 15px 0;">
                <div style="background-color: #2C4A6E; height: 14px; border-radius: 2px; width: {max(min(rate, 100), 0)}%;"></div>
            </div>
            <p style="color: #B93636; font-weight: bold; font-size: 14px;">Attendance is currently low.</p>
        </div>
        """, unsafe_allow_html=True)

    with c_mid2:
        st.markdown('<div class="custom-card"><h3 style="margin-top: 0; color: #1A202C;">Quick Actions</h3>', unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📷 Take Attendance"): go_to_page("◎ Attendance")
            if st.button("◫ Open Reports"): go_to_page("◫ Reports")
        with col_btn2:
            if st.button("＋ Register Student"): go_to_page("◉ Students")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-card"><h3 style="margin-top: 0; color: #1A202C; display: inline-block;">Recent Attendance</h3> <span style="color: #6B7280; font-size: 14px; margin-left: 10px;">Latest check-ins</span>', unsafe_allow_html=True)
    recent = (supabase.table("attendance").select("student_id, attendance_date, attendance_time, status, course_id").order("attendance_date", desc=True).order("attendance_time", desc=True).limit(8).execute().data or [])
    if recent:
        smap = {str(s["student_id"]): s["name"] for s in students}
        cmap = {str(c["course_id"]): c.get("course_code", "-") for c in load_courses()}
        df = pd.DataFrame([{"Student ID": r["student_id"], "Student": smap.get(str(r["student_id"]), "-"), "Course": cmap.get(str(r.get("course_id")), "-"), "Date": r["attendance_date"], "Check-in": str(r["attendance_time"])[:8], "Status": r["status"]} for r in recent])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else: st.info("No attendance recorded yet.")
    st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "◉ Students":
    st.markdown("### Create a student profile and capture their face")
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            sid = st.text_input("Student ID")
            name = st.text_input("Full Name")
            section = st.text_input("Section")
        with col2:
            cls = st.selectbox("Class", ["B.Ed IT", "B.Ed Geo/Eng", "B.Ed His/Eng", "B.Ed Bio/Chem", "B.Ed Phy/Math"])
            year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        img_file = st.camera_input("Capture Face")
        if st.button("Register Student"):
            if not all([sid, name, section]) or img_file is None: st.warning("Fill in all fields and capture a face.")
            else:
                from PIL import Image
                img = np.array(Image.open(img_file).convert("RGB"))
                locs = face_recognition.face_locations(img)
                if len(locs) != 1: st.error(f"Detected {len(locs)} faces. Need exactly one.")
                else:
                    enc = face_recognition.face_encodings(img, locs)[0]
                    try:
                        supabase.table("students").insert({"student_id": sid, "name": name, "class": cls, "section": section, "year": year, "face_encoding": ",".join(str(float(x)) for x in enc)}).execute()
                        load_students.clear()
                        st.success(f"✓ {name} registered successfully!")
                    except Exception as e: st.error(f"Registration failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "◎ Attendance":
    st.markdown("### Select a course and start the camera")
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        courses = load_courses()
        if not courses: st.warning("No courses. Add one first via Supabase.")
        else:
            course_names = [f"{c['course_code']} — {c['course_name']}" for c in courses]
            choice = st.selectbox("Select Course", course_names)
            course = courses[course_names.index(choice)]
            st.markdown(f"<p style='color: #23824B; font-weight: bold;'>● Camera Ready</p>", unsafe_allow_html=True)
            students = load_students()
            if not students: st.warning("No registered students with encodings found.")
            else:
                img_file = st.camera_input("Capture face to mark attendance")
                if img_file is not None:
                    from PIL import Image
                    img = np.array(Image.open(img_file).convert("RGB"))
                    with st.spinner("Matching face…"):
                        student, dist = match_face(img, students)
                    if student:
                        st.success(f"Match: **{student['name']}** (distance {dist:.3f})")
                        if st.button("Mark Present"):
                            ok, msg = mark_present(student, course["course_id"])
                            (st.success if ok else st.warning)(msg)
                    else: st.error(f"No match (closest distance {dist:.3f}).")
        st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "◫ Reports":
    st.markdown("### Review and export student attendance")
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        date_filter = c1.date_input("Date", value=bhutan_now().date())
        courses = load_courses()
        course_opts = ["All Courses"] + [f"{c['course_code']} — {c['course_name']}" for c in courses]
        course_filter = c2.selectbox("Course", course_opts)
        search = c3.text_input("Search Student")
        q = supabase.table("attendance").select("*").eq("attendance_date", date_filter.isoformat())
        if course_filter != "All Courses":
            cid = courses[course_opts.index(course_filter) - 1]["course_id"]
            q = q.eq("course_id", cid)
        recs = q.order("attendance_time", desc=True).execute().data or []
        smap = {str(s["student_id"]): s["name"] for s in load_students()}
        cmap = {str(c["course_id"]): c.get("course_code", "-") for c in courses}
        rows = []
        for r in recs:
            sid = str(r["student_id"]); sname = smap.get(sid, "-"); ccode = cmap.get(str(r.get("course_id")), "-")
            if search.lower() and search.lower() not in f"{sid} {sname} {ccode}".lower(): continue
            rows.append({"ID": r.get("attendance_id"), "Student ID": sid, "Name": sname, "Course": ccode, "Date": r["attendance_date"], "Time": str(r["attendance_time"])[:8], "Status": r["status"]})
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2: st.download_button("↓ Export CSV", df.to_csv(index=False).encode("utf-8-sig"), file_name=f"attendance_{date_filter}.csv", mime="text/csv")
        else: st.info("No records match your filters.")
        st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "▣ Courses":
    st.markdown("### Manage Courses")
    st.info("Course management is available in the desktop version. For this web demo, manage courses via your Supabase dashboard.")

elif current_page == "⚙ Settings":
    st.markdown("### Settings")
    st.info("Settings coming soon.")