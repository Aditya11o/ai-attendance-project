# SnapClass — AI-Based Attendance Management System

**SnapClass** is a multi-modal AI classroom attendance management web application built with **Python**, **Streamlit**, **Supabase (PostgreSQL)**, **dlib**, and **Resemblyzer**. It streamlines attendance marking using **classroom photo face recognition** and **bulk voice speaker identification**, with dedicated portals for both **Students** and **Teachers**.

---

## Key Features

### Student Portal
- **Webcam FaceID Login & Registration:** Authenticate using facial recognition (`dlib` 128-D face embeddings) or register a new profile with a camera capture and optional voice sample.
- **Course Enrollment:** Join subjects manually by entering a subject code or via QR / URL deep link (`?join-code=<subject_code>`).
- **Student Dashboard:** View enrolled subjects with total classes, attended count, and one-click course unenrollment.

### Teacher Portal
- **Secure Authentication:** Teacher registration and password login secured with `bcrypt` password hashing.
- **Subject Management:** Create subjects (`subject_code`, `name`, `section`), view live enrolled student and class counts across all subjects, and generate shareable links and QR codes (`segno`).
- **AI Photo Attendance:** Capture live classroom snapshots or upload multiple photos, run batch face recognition across images, review `Present` / `Absent` results in a confirmation modal, and save logs to Supabase.
- **Voice Attendance:** Record classroom audio and identify enrolled students with registered voice profiles (`resemblyzer` + `librosa` speech segmentation).
- **Attendance Records:** View session-by-session attendance summaries grouped by timestamp and subject.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend / App Framework** | Python (`3.12` recommended), Streamlit (`>= 1.50`), Custom Scoped CSS, Material Symbols |
| **Database / Backend** | Supabase (`supabase` Python client / PostgREST) |
| **Face Recognition** | `dlib-bin` (HOG detector, 68-landmark shape predictor, ResNet-34 face encoder), `face_recognition_models`, `scikit-learn` (`SVC`), `Pillow`, `numpy` |
| **Voice Recognition** | `resemblyzer` (`VoiceEncoder`), `librosa` (audio loading & silence splitting), `torch`, `webrtcvad` |
| **Security & Utilities** | `bcrypt`, `pandas`, `segno` (QR code generation) |

---

## Project Structure

```text
ai-attendance-project/
├── app.py                                      # Application entry point & portal/query-param router
├── requirements.txt                            # Python dependencies
├── README.md                                   # Project documentation
├── .gitignore                                  # Excludes secrets, .venv, and Python cache files
├── .streamlit/
│   └── secrets.toml.example                    # Template for Supabase credentials
└── src/
    ├── components/
    │   ├── dialog_add_photo.py                 # Camera capture & multi-image upload modal
    │   ├── dialog_attendance_results.py        # Attendance review, styling, & confirmation modal
    │   ├── dialog_auto_enroll.py               # Deep-link (?join-code=) enrollment modal
    │   ├── dialog_create_subject.py            # New subject creation modal
    │   ├── dialog_enroll.py                    # Manual subject code enrollment modal
    │   ├── dialog_share_subject.py             # QR code & shareable join link modal
    │   ├── dialog_voice_attendance.py          # Classroom voice recording & matching modal
    │   ├── footer.py                           # Portal and homepage footer
    │   ├── header.py                           # SnapClass brand headers
    │   ├── icons.py                            # Centralized Material Symbols icon helpers
    │   └── subject_card.py                     # Reusable subject summary card component
    ├── database/
    │   ├── config.py                           # Supabase client initialization from st.secrets
    │   └── db.py                               # bcrypt helpers & Supabase CRUD queries
    ├── pipelines/
    │   ├── face_pipeline.py                    # Face embedding extraction & matching pipeline
    │   └── voice_pipeline.py                   # Speaker embedding & bulk audio processing pipeline
    ├── screens/
    │   ├── home_screen.py                      # Landing portal (Student / Teacher selector)
    │   ├── student_screen.py                   # Student FaceID login, signup, & dashboard
    │   └── teacher_screen.py                   # Teacher auth, Take Attendance, Subjects, & Records
    └── ui/
        └── base_layout.py                      # Global & portal-scoped CSS typography and layout
```

---

## Local Setup & Installation

### 1. Prerequisites
- **Python 3.12 (64-bit)** *(Recommended: the codebase uses Python 3.12+ f-string syntax, while `dlib-bin` and `resemblyzer` have reliable Windows wheels on Python 3.12.)*
- **Git** *(Required to install `face_recognition_models` from GitHub.)*
- A free **[Supabase](https://supabase.com)** project.

### 2. Create & Activate Virtual Environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 3. Install Dependencies

Install `setuptools<70.0.0` first (required by `face_recognition_models`), then install the project dependencies:

```powershell
pip install "setuptools<70.0.0"
pip install -r requirements.txt
```

> **Windows Tip (If `webrtcvad` fails without Visual C++ Build Tools):**
> Use the prebuilt `webrtcvad-wheels` package instead of compiling from source:
> ```powershell
> pip install streamlit numpy pandas scikit-learn dlib-bin "git+https://github.com/ageitgey/face_recognition_models" "setuptools<70.0.0" supabase bcrypt segno pillow librosa torch webrtcvad-wheels
> pip install --no-deps resemblyzer
> ```

### 4. Set Up Supabase Database Tables

Open **Supabase Dashboard → SQL Editor → New query** and run the following schema:

```sql
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    student_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    face_embedding DOUBLE PRECISION[],
    voice_embedding DOUBLE PRECISION[]
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_code TEXT NOT NULL,
    name TEXT NOT NULL,
    section TEXT NOT NULL,
    teacher_id BIGINT REFERENCES teachers(teacher_id)
);

CREATE TABLE IF NOT EXISTS subject_students (
    subject_id BIGINT REFERENCES subjects(subject_id),
    student_id BIGINT REFERENCES students(student_id),
    PRIMARY KEY (subject_id, student_id)
);

CREATE TABLE IF NOT EXISTS attendance_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id BIGINT REFERENCES students(student_id),
    subject_id BIGINT REFERENCES subjects(subject_id),
    timestamp TEXT NOT NULL,
    is_present BOOLEAN NOT NULL DEFAULT FALSE
);
```

> **Note:** For local development with the Supabase `anon` key, run the query without enabling restrictive RLS policies (or configure explicit policies if integrating Supabase Auth). Never commit a `service_role` key.

### 5. Configure Streamlit Secrets

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your Supabase Project URL and API key:

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-supabase-anon-or-publishable-key"
```

### 6. Run the Application

```powershell
streamlit run app.py
```

Open **`http://localhost:8501`** in your browser and grant **Camera** and **Microphone** permissions when prompted.

---

## How the AI Pipelines Work

1. **Face Recognition (`src/pipelines/face_pipeline.py`):**
   - Detects faces with `dlib.get_frontal_face_detector()`, extracts 68 facial landmarks via `dlib.shape_predictor`, and computes a 128-D face descriptor using `dlib.face_recognition_model_v1`.
   - Matches detected faces against registered student embeddings using `sklearn.svm.SVC` paired with a Euclidean distance threshold (`<= 0.6`).
2. **Voice Recognition (`src/pipelines/voice_pipeline.py`):**
   - Loads uploaded/recorded audio at `16 kHz` with `librosa`, splits speech segments by silence (`top_db=30`, minimum `0.5s`), computes 256-D embeddings with `resemblyzer.VoiceEncoder`, and matches enrolled speakers using dot-product similarity (`>= 0.65`).

---

## Known Limitations & Roadmap

- **Authentication & Liveness:** Student FaceID login currently relies on single-frame face matching without anti-spoofing/liveness detection or secondary PIN verification.
- **Subject-Scoped Recognition:** Face matching currently loads all registered students rather than filtering strictly to students enrolled in the selected subject.
- **Attendance Overrides & Exports:** Manual toggling in the confirmation modal, duplicate same-day session checks, and CSV/PDF report exports are planned for future iterations.
- **Share URL Domain:** `src/components/dialog_share_subject.py` defaults to `https://snapclass-360.streamlit.app` (`DEFAULT_APP_URL`); update it when deploying to a different host.
