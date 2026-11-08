
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
|---|---|
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

```text
FaceAttend/
│
├── main.py
├── dashboard.py
├── register_student.py
├── attendance.py
├── camera_test.py
├── camera_test_all.py
├── keyboard_camera_test.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── gradio_app/
│   ├── app.py
│   └── camera_test.py
│
├── streamlit_app/
│   └── app.py
│
└── Screenshots/
    ├── 01_Main_Dashboard.png
    ├── 02_Gradio_App.png
    └── 03_Streamlit_App.png
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
```

### Step 2: Open the Project Folder

```bash
cd FaceAttend
```

### Step 3: Install Dependencies

```bash
py -3.13 -m pip install -r requirements.txt
```

For Windows systems, facial recognition may require a compatible dlib installation.

### Step 4: Configure Supabase

Create a `.env` file in the main project folder.

Add the following configuration:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_server_side_secret_key
```

Replace the example values with your own Supabase project credentials.

**Security:** Keep your `.env` file private. Never upload secret keys, passwords, or actual biometric data to GitHub.

### Step 5: Run the Desktop Application

```bash
py -3.13 dashboard.py
```

### Step 6: Run the Gradio Application

Open the terminal in the main project folder and execute:

```powershell
$env:PYTHONPATH = (Get-Location).Path
py -3.13 gradio_app/app.py
```

Open the local URL displayed in the terminal.

### Step 7: Run the Streamlit Application

```bash
py -3.13 -m streamlit run streamlit_app/app.py
```

Open the local URL displayed in the terminal.

## 7. Database Structure

The system uses Supabase with three main tables.

### Students

- student_id
- name
- class
- section
- face_encoding

### Courses

- course_id
- course_code
- course_name
- teacher

### Attendance

- student_id
- course_id
- attendance_date
- status
- check_in_time

## 8. Application Screenshots

### 8.1 Tkinter Desktop Dashboard

![Main Dashboard](Screenshots/01_Main_Dashboard.png)

### 8.2 Gradio Web Application

![Gradio Application](Screenshots/02_Gradio_App.png)

### 8.3 Streamlit Web Application

![Streamlit Application](Screenshots/03_Streamlit_App.png)

## 9. Limitations

- The system requires a working webcam.
- Facial recognition accuracy may be affected by lighting and camera quality.
- A stable internet connection is required for Supabase operations.
- Database access requires correctly configured API credentials and security policies.
- Facial recognition libraries may require additional installation and configuration.

## 10. Future Improvements

- Improve facial recognition accuracy.
- Add user authentication and role-based access.
- Improve attendance report generation.
- Add attendance export to Excel and PDF.
- Improve the user interface and mobile accessibility.
- Strengthen biometric data protection.

## 11. Team Members

- Rinchen Tshering
- Tandin Penjor
- Pema Yangki
- Tashi Lhamo
- Sangay Choden

## 12. Acknowledgement

We would like to express our sincere gratitude to our lecturers, project supervisor, and everyone who supported us throughout the development of FaceAttend.

This project provided us with practical experience in Python programming, graphical user interface development, facial recognition, web-based applications, and database integration.

---

**FaceAttend – Bhutan Digital Attendance System**

Samtse College of Education  
Royal University of Bhutan
