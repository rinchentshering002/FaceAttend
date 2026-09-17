import os
from dotenv import load_dotenv
from supabase import create_client

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Check credentials
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials are missing!")

# ============================================================
# CONNECT TO SUPABASE
# ============================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Connected to Supabase successfully!")

# ============================================================
# CHECK STUDENTS
# ============================================================

students = (
    supabase
    .table("students")
    .select("student_id, name")
    .execute()
)

print("\nStudents currently registered:")

for student in students.data:
    print(
        f"- {student['student_id']} : "
        f"{student['name']}"
    )

# ============================================================
# SELECT A STUDENT
# ============================================================

student_id = input("\nEnter Student ID to test attendance: ").strip()

# Check if student exists
student = next(
    (
        s for s in students.data
        if s["student_id"] == student_id
    ),
    None
)

if student is None:
    print(f"\n❌ Student '{student_id}' does not exist.")
    print("Attendance was NOT recorded.")
    exit()

print(f"\nStudent found: {student['name']}")

# ============================================================
# RECORD ATTENDANCE
# ============================================================

attendance = {
    "student_id": student_id,
    "status": "Present"
}

response = (
    supabase
    .table("attendance")
    .insert(attendance)
    .execute()
)

print("\n✅ Attendance recorded successfully!")
print(response.data)
