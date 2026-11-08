"""
FaceAttend — Gradio version
Run:  python gradio_app.py
"""
import os
import numpy as np
import pandas as pd
import gradio as gr
import face_recognition
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials missing")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BHUTAN_TZ = ZoneInfo("Asia/Thimphu")
FACE_MATCH_THRESHOLD = 0.50

def _load_students():
    resp = supabase.table("students").select("student_id, name, face_encoding").execute()
    out = []
    for row in resp.data or []:
        enc = row.get("face_encoding")
        if not enc: continue
        try:
            v = [float(x.strip()) for x in enc.split(",")]
            if len(v) == 128:
                out.append({"student_id": row["student_id"], "name": row["name"], "encoding": np.array(v, dtype=np.float64)})
        except Exception: continue
    return out

def _courses():
    return supabase.table("courses").select("*").order("course_id").execute().data or []

def register(sid, name, cls, year, section, img):
    if not all([sid, name, section]): return "⚠ Fill Student ID, Name, Section."
    if img is None: return "⚠ Capture a face first."
    rgb = np.ascontiguousarray(img[..., :3], dtype=np.uint8)
    locs = face_recognition.face_locations(rgb)
    if len(locs) != 1: return f"⚠ Detected {len(locs)} faces — need exactly 1."
    enc = face_recognition.face_encodings(rgb, locs)[0]
    try:
        supabase.table("students").insert({
            "student_id": sid, "name": name, "class": cls, "section": section, "year": year,
            "face_encoding": ",".join(str(float(x)) for x in enc),
        }).execute()
        return f"✅ {name} registered successfully!"
    except Exception as e: return f"❌ Registration failed: {e}"

def take_attendance(course_label, img):
    if img is None: return "⚠ Capture a face first."
    courses = _courses()
    if not courses: return "⚠ No courses exist."
    labels = [f"{c['course_code']} — {c['course_name']}" for c in courses]
    if course_label not in labels: return "⚠ Select a valid course."
    course = courses[labels.index(course_label)]

    students = _load_students()
    if not students: return "⚠ No students with encodings."

    rgb = np.ascontiguousarray(img[..., :3], dtype=np.uint8)
    locs = face_recognition.face_locations(rgb)
    if len(locs) != 1: return f"⚠ Detected {len(locs)} faces — need exactly 1."
    enc = face_recognition.face_encodings(rgb, locs)[0]
    known = np.array([s["encoding"] for s in students])
    dists = face_recognition.face_distance(known, enc)
    best = int(np.argmin(dists)); best_dist = float(dists[best])

    if best_dist >= FACE_MATCH_THRESHOLD: return f"❌ No match (closest {best_dist:.3f})"

    student = students[best]
    now = datetime.now(BHUTAN_TZ)
    try:
        supabase.table("attendance").insert({
            "student_id": student["student_id"],
            "attendance_date": now.date().isoformat(),
            "attendance_time": now.time().isoformat(),
            "status": "Present",
            "course_id": course["course_id"],
        }).execute()
        return f"✅ {student['name']} marked Present\nDistance: {best_dist:.3f} | Time: {now.strftime('%I:%M:%S %p')}"
    except Exception as e:
        msg = str(e).lower()
        if "duplicate" in msg or "unique" in msg: return f"⚠ {student['name']} already marked Present today."
        return f"❌ DB error: {e}"

def load_report(date_str, course_label, search):
    try: d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception: d = datetime.now(BHUTAN_TZ).date()
    q = supabase.table("attendance").select("*").eq("attendance_date", d.isoformat())
    courses = _courses()
    if course_label and course_label != "All Courses":
        labels = [f"{c['course_code']} — {c['course_name']}" for c in courses]
        if course_label in labels: q = q.eq("course_id", courses[labels.index(course_label)]["course_id"])
    recs = q.order("attendance_time", desc=True).execute().data or []
    smap = {str(s["student_id"]): s["name"] for s in _load_students()}
    cmap = {str(c["course_id"]): c.get("course_code", "-") for c in courses}
    rows = []
    for r in recs:
        sid = str(r["student_id"]); sname = smap.get(sid, "-"); ccode = cmap.get(str(r.get("course_id")), "-")
        if search and search.lower() not in f"{sid} {sname} {ccode}".lower(): continue
        rows.append([r.get("attendance_id"), sid, sname, ccode, r["attendance_date"], str(r["attendance_time"])[:8], r["status"]])
    return pd.DataFrame(rows, columns=["ID", "Student ID", "Name", "Course", "Date", "Time", "Status"])

# ---- BUILD UI ----
with gr.Blocks(title="FaceAttend — Gradio") as demo:
    gr.Markdown(f"# 📷 FaceAttend — Gradio Edition\n*Bhutan Time: {datetime.now(BHUTAN_TZ).strftime('%A, %d %B %Y')}*")
    with gr.Tab("◎ Take Attendance"):
        courses = _courses()
        labels = ["All Courses"] + [f"{c['course_code']} — {c['course_name']}" for c in courses] if courses else ["No courses"]
        course_dd = gr.Dropdown(labels[1:] if len(labels) > 1 else labels, label="Course")
        attend_img = gr.Image(sources=["webcam"], type="numpy", label="Capture face")
        attend_btn = gr.Button("Mark Present", variant="primary")
        attend_out = gr.Textbox(label="Result", lines=3)
        attend_btn.click(take_attendance, inputs=[course_dd, attend_img], outputs=[attend_out])

    with gr.Tab("➕ Register Student"):
        with gr.Row():
            sid_in = gr.Textbox(label="Student ID")
            name_in = gr.Textbox(label="Full Name")
            section_in = gr.Textbox(label="Section")
        with gr.Row():
            cls_in = gr.Dropdown(["B.Ed IT", "B.Ed Geo/Eng", "B.Ed His/Eng", "B.Ed Bio/Chem", "B.Ed Phy/Math"], label="Class")
            year_in = gr.Dropdown(["1st Year", "2nd Year", "3rd Year", "4th Year"], label="Year")
        reg_img = gr.Image(sources=["webcam"], type="numpy", label="Capture face")
        reg_btn = gr.Button("Register", variant="primary")
        reg_out = gr.Textbox(label="Result", lines=2)
        reg_btn.click(register, inputs=[sid_in, name_in, cls_in, year_in, section_in, reg_img], outputs=[reg_out])

    with gr.Tab("📊 Reports"):
        with gr.Row():
            date_in = gr.Textbox(label="Date (YYYY-MM-DD)", value=datetime.now(BHUTAN_TZ).date().isoformat())
            course_filter = gr.Dropdown(["All Courses"] + (labels[1:] if len(labels) > 1 else []), value="All Courses", label="Course")
            search_in = gr.Textbox(label="Search student")
        refresh_btn = gr.Button("Load Report")
        report_df = gr.Dataframe(headers=["ID", "Student ID", "Name", "Course", "Date", "Time", "Status"], label="Attendance")
        refresh_btn.click(load_report, inputs=[date_in, course_filter, search_in], outputs=[report_df])

if __name__ == "__main__":
    demo.launch()