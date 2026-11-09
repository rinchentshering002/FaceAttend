# FaceAttend – Bhutan Digital Attendance System

## 1. Project Overview

FaceAttend is a facial-recognition-based attendance management system developed to make student attendance recording easier, faster, and more efficient.

The system uses facial recognition technology to identify registered students and record their attendance. It integrates a Python desktop interface with web-based interfaces and a Supabase database for storing student information, course details, and attendance records.

## 2. Project Objectives

- To develop a digital attendance management system using facial recognition.
- To reduce manual attendance-taking time.
- To improve the accuracy of student identification and attendance recording.
- To store and manage attendance records digitally.
- To provide user-friendly interfaces for managing student attendance.

## 3. Key Features

- **Student Registration:** Register students with their personal details and facial images.
- **Facial Recognition:** Detect and recognise registered student faces.
- **Automatic Attendance:** Record attendance when a registered student is recognised.
- **Course Management:** Add and manage course information.
- **Attendance Reports:** View and manage attendance records.
- **Dashboard:** Display attendance-related information.
- **Database Integration:** Store student, course, and attendance information using Supabase.

## 4. Technologies Used

| Technology | Purpose |
| :--- | :--- |
| Python | Main programming language |
| Tkinter | Desktop graphical user interface |
| Gradio | Web-based interface |
| Streamlit | Web-based interface |
| OpenCV | Camera access and image processing |
| face_recognition | Facial detection and recognition |
| dlib | Facial recognition processing |
| NumPy | Numerical operations |
| Supabase | Cloud database |

## 5. Project Structure

The FaceAttend project has a unified structure where both the desktop and web applications share the same root folder.

```text
FaceAttend/
│
├── .env                    <-- (Create this file manually, do not upload)
├── .gitignore
├── requirements.txt
├── README.md
│
├── dashboard.py            <-- Main Tkinter Desktop Application
├── attendance.py
├── register_student.py
├── attendance_report.py
├── ui_helpers.py           <-- Tkinter UI Helpers
│
├── streamlit_app.py        <-- Streamlit Web Dashboard
├── gradio_interface.py     <-- Gradio AI Camera Interface
├── database.py             <-- Supabase Database Operations
├── face_engine.py          <-- Facial Encoding & Recognition
├── web_ui.py               <-- Streamlit UI Helpers
├── run.py                  <-- Web Application Launcher
│
└── Screenshots/            <-- Stores screenshots of the applications
```
## 6. Installation and Setup

### Requirements
- Python 3.13
- Webcam
- Internet connection
- Supabase account

### Step 1: Clone the Repository
```bash
git clone https://github.com/rinchentshering002/FaceAttend.git
cd FaceAttend
```

Step 2: Install Dependencies
```bash
py -3.13 -m pip install -r requirements.txt
(Note: For Windows systems, facial recognition may require a compatible dlib installation, which is included via dlib-bin in the requirements).
```

Step 3: Configure Supabase
Create a .env file in the main FaceAttend folder and add your credentials:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
Security: Keep your .env file private. Never upload secret keys or actual biometric data to GitHub. This file is already protected by .gitignore.
```

Step 4: Run the Tkinter Desktop Application
From the main FaceAttend folder, execute:

```bash
py -3.13 dashboard.py
```

Step 5: Run the Web Applications (Streamlit + Gradio)
From the main FaceAttend folder, execute:

```bash
py -3.13 run.py
```
This command automatically launches both the Gradio backend (for AI face scanning) and the Streamlit dashboard (for reporting and management).

7. Database Structure
The system uses Supabase to store and manage information across three main tables:

7.1 Students Table
- student_id (Primary Key)

- name

- class

- section

- year

- face_encoding

7.2 Courses Table
- course_id (Primary Key)

- course_code

- course_name

- teacher

7.3 Attendance Table
- attendance_id (Primary Key)

- student_id (Foreign Key)

- course_id (Foreign Key)

- attendance_date

- attendance_time

- status

8. Application Screenshots
8.1 Tkinter Desktop Dashboard
https://screenshots/dashboard.jpg

8.2 Gradio Web Application
https://screenshots/02_Gradio_App.png

8.3 Streamlit Web Application
https://screenshots/03_Streamlit_App.png

9. Limitations
- The system requires a working webcam.

- Facial recognition accuracy may be affected by lighting and camera quality.

- A stable internet connection is required for Supabase operations.

- Database access requires correctly configured API credentials and security policies.

10. Future Improvements
- Improve facial recognition accuracy and add liveness detection.

- Add user authentication and role-based access.

- Improve attendance report generation (Excel and PDF export).

- Improve the mobile accessibility of the web dashboard.

- Strengthen biometric data protection and privacy governance.

11. Team Members
- Rinchen Tshering

- Tandin Penjor

- Pema Yangki

- Tashi Lhamo

- Sangay Choden

12. Acknowledgement
We would like to express our sincere gratitude to our lecturers, project supervisor, and everyone who supported us throughout the development of FaceAttend.

This project provided us with practical experience in Python programming, graphical user interface development, facial recognition, web-based applications, and database integration.

FaceAttend – Bhutan Digital Attendance System
Samtse College of Education
Royal University of Bhutan

