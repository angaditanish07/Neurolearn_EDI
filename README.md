# NeuroLearn — Inclusive Education Platform

NeuroLearn (EDI Neurolearn) is a web-based inclusive learning platform designed to support students with diverse learning needs—especially those at risk of or living with dyslexia—while giving parents visibility into progress, screening outcomes, and engagement. The application combines a student-facing learning hub, AI-assisted dyslexia screening, interactive computer-vision activities, and a parent dashboard backed by a persistent MongoDB database.

This document describes what the project does, how it is built, and how the major parts fit together. It intentionally avoids source code listings; refer to the repository and inline documentation for implementation details.

---

## Table of contents

1. [Project purpose and audience](#project-purpose-and-audience)
2. [Core features](#core-features)
3. [Technology stack](#technology-stack)
4. [System architecture](#system-architecture)
5. [Application structure](#application-structure)
6. [Data layer (MongoDB)](#data-layer-mongodb)
7. [Authentication and roles](#authentication-and-roles)
8. [Machine learning and computer vision](#machine-learning-and-computer-vision)
9. [Major user flows](#major-user-flows)
10. [Accessibility and inclusive design](#accessibility-and-inclusive-design)
11. [Real-time communication](#real-time-communication)
12. [Configuration and environment](#configuration-and-environment)
13. [Running locally](#running-locally)
14. [Deployment](#deployment)
15. [Health checks and troubleshooting](#health-checks-and-troubleshooting)
16. [Security considerations](#security-considerations)
17. [Limitations and future considerations](#limitations-and-future-considerations)

---

## Project purpose and audience

NeuroLearn addresses three overlapping goals:

**Early insight into reading difficulties** — Students complete a structured dyslexia screening battery (reading, spelling, letter recognition, word matching, number reading, sentence copying, and optional handwriting analysis). Responses are scored, fed into a trained machine-learning model where available, and stored so trends can be reviewed over time.

**Engaging, multimodal learning** — Beyond screening, students access interactive learning modules that use the device camera for emotion recognition, facial landmark exploration, finger counting practice, drawing activities, and adaptive quizzes that adjust difficulty based on detected emotional state.

**Family-connected progress** — Parents register separately, link to a child using a one-time family code, and view a dashboard with screening history, component scores, learning-path progress, activity timelines, and recommendations derived from the latest results.

The platform is built as a monolithic Flask application with server-rendered pages, JSON APIs for dynamic sections, and substantial client-side JavaScript for camera, speech, and accessibility features.

---

## Core features

### Student experience

- **Personalized home dashboard** — Welcome area, learning-path cards (visual learning, dyslexia screening, educational games), progress statistics (streak, lessons completed, skills mastered), and quick navigation.
- **Dyslexia screening module** — Multi-step assessment with optional read-aloud of prompts, speech-to-text for reading tasks, handwriting upload, and results with risk level, component breakdown, and recommendations. Dyslexia-friendly font toggle is deliberately **disabled** during screening so typography does not invalidate the assessment.
- **Interactive learning** — Camera-based emotion detection with adaptive multiple-choice questions (easier questions after sad or prolonged neutral expressions; harder questions after happy and correct answers), face-feature visualization with landmark overlays, finger counting with audio feedback, drawing canvas with toolbar, and optional educational games entry.
- **Account and profile** — Registration as student or parent, login/logout, profile and settings pages, browser-persisted accessibility preferences.

### Parent experience

- **Parent dashboard** — Lists linked children, summary metrics per child, path progress bars, screening history chart, component score breakdown, activity type breakdown, recent timeline, and recommendation text from the latest screening.
- **Link child** — Enter the student’s family link code to establish a verified parent–child relationship in the database.
- **Periodic refresh** — Dashboard data can be refreshed on an interval to show updated summaries without a full page reload.

### Platform-wide

- **Global navigation bar** — Consistent links to Home, Interactive Learning, Dyslexia Screening, Help, and Parent Dashboard (visible for parent accounts). Accessibility controls: dyslexic-friendly font (OpenDyslexic), high contrast, text size, read-aloud, voice navigation, and floating microphone/read buttons (bottom-left).
- **Botpress chat widget** — Embedded conversational assistant on selected pages for help and engagement.
- **Progress tracking** — Server-side events for screenings, module visits, emotion sessions, finger counting, and related activities; aggregated into summaries and parent views.

---

## Technology stack

### Backend

| Layer | Technology | Role |
|--------|------------|------|
| Web framework | Flask 2.3 | HTTP routing, sessions, templates |
| WSGI server | Gunicorn + Eventlet worker | Production and Docker serving; supports Socket.IO |
| Real-time | Flask-SocketIO | WebSocket events (e.g. parent notifications) |
| Database | MongoDB via PyMongo | Users, links, screening results, progress events |
| Session store | Flask signed cookies (default) or Redis via Flask-Session | Optional Redis for scalable sessions |
| Config | python-dotenv | Environment-driven settings |
| Password security | Werkzeug password hashing | Bcrypt-style hashes for credentials |

### Machine learning and signal processing

| Component | Technology | Role |
|-----------|------------|------|
| Emotion model | TensorFlow / Keras (FER2013 mini Xception HDF5) | Facial emotion classification from webcam frames |
| Dyslexia model | scikit-learn + joblib bundle | Risk scoring from engineered screening features |
| Face and hands | MediaPipe | Face mesh landmarks and hand detection for finger counting |
| Vision utilities | OpenCV (headless), Pillow, NumPy | Image decode, transforms, handwriting pipeline |
| Speech (server) | SpeechRecognition, pydub | Reading-test audio transcription when browser does not send WAV |
| Audio (server) | ffmpeg (optional system binary) | Fallback decode for WebM/MP4 recordings |

### Frontend

| Layer | Technology | Role |
|--------|------------|------|
| Templates | Jinja2 (HTML) | Server-rendered pages |
| Styling | Custom CSS, Lexend and OpenDyslexic fonts | Layout, dyslexia-friendly mode, dashboard navbar |
| Scripting | Vanilla JavaScript, jQuery (legacy sections) | APIs, camera, quizzes, accessibility |
| Charts | Plotly (screening/parent views where used) | Screening history visualization |
| Speech (client) | Web Speech API | Read-aloud and voice navigation |
| Audio capture | Browser MediaRecorder + custom WAV encoder | Microphone for reading tests without server ffmpeg |
| Permissions | media-permissions.js | Camera/mic guidance for non-HTTPS contexts |
| Chat | Botpress Cloud (inject script) | External hosted chatbot |

### DevOps and packaging

| Item | Technology | Role |
|------|------------|------|
| Container | Docker (Python 3.11 slim) | Reproducible deploy with ffmpeg and system libs |
| Orchestration | docker-compose | Local/production-style stack |
| Cloud deploy | Render (render.yaml), docs for Oracle/Atlas | Free-tier hosting guidance |
| TLS (local LAN) | pyOpenSSL adhoc | Optional HTTPS for camera on network IP |

---

## System architecture

NeuroLearn follows a **classic three-tier layout** adapted for ML-heavy routes:

1. **Presentation** — HTML templates under `templates/`, static assets under `static/`, and client scripts that call REST-style JSON endpoints.
2. **Application** — Flask blueprints in `app/routes/` delegate to services in `app/services/`; thin controllers keep HTTP concerns separate from business logic.
3. **Data** — MongoDB collections accessed through `app/mongo.py` helpers and document wrapper classes in `app/models.py` (not an ORM—explicit PyMongo operations).

**Request lifecycle (typical API call)**  
The browser sends a JSON or multipart request → Flask route applies `login_required` or `role_required` decorators → service layer reads/writes MongoDB and optionally loads ML models through lazy loaders in `app/ml/loaders.py` → JSON response or redirect.

**Model loading**  
Emotion and dyslexia models are loaded on first use and cached in process memory to avoid startup cost. Missing model files are logged; health endpoint reports availability.

**Entry points**  
- Development: `run.py` starts Flask-SocketIO with optional HTTPS.  
- Production: `wsgi.py` exposes the app for Gunicorn; Docker `start.sh` binds to the platform-assigned `PORT` (required for Render and similar hosts).

---

## Application structure

### Server package (`app/`)

- **`__init__.py`** — Application factory: configuration, MongoDB init, Socket.IO, blueprint registration.
- **`config.py`** — Central settings from environment variables (secrets, paths, MongoDB URI, feature flags).
- **`mongo.py`** — Connection pooling, TLS/CA handling for Atlas, index creation, ObjectId parsing.
- **`models.py`** — Document shapes for users, parent–child links, screening results, and progress events.
- **`extensions.py`** — Shared Socket.IO instance and connection tracking.
- **`routes/`** — HTTP blueprints:
  - **pages** — Home, login, register, profile, settings, help, interactive learning page, dyslexia screening page.
  - **auth** — Register, login, logout, current user, parent link-child API.
  - **progress** — Student/parent summary, screening history, generic progress events.
  - **parent** — Parent dashboard page and child detail APIs.
  - **dyslexia** — Handwriting analysis, test submission (simple and full), reading audio analysis, parent notify.
  - **emotion** — Emotion detection, face features, finger counting.
  - **health** — Liveness and dependency status (MongoDB, models, ffmpeg).
  - **debug_routes** — Optional test fixtures (disabled unless `ENABLE_DEBUG_ROUTES` is set).
  - **websocket** — Socket.IO event handlers.
- **`services/`** — Business logic:
  - **auth_service** — Registration, authentication, family linking.
  - **progress_service** — Screening persistence, streaks, parent aggregates, activity stats.
  - **dyslexia_service** — Feature extraction, ML inference, recommendations, result persistence.
  - **emotion_service**, **face_service**, **finger_service**, **handwriting_service** — Vision pipelines.
- **`ml/`** — Model loaders and feature schema definitions for dyslexia scoring.
- **`utils/`** — Audio conversion helpers, image processing utilities.

### Client assets (`static/`, `templates/`)

- **Global navbar** — `templates/includes/dashboard_navbar.html` plus `dashboard-navbar.css` / `dashboard-navbar.js`.
- **Accessibility** — `accessibility.js` (read-aloud, dyslexic font, contrast, font size; emoji stripping for TTS).
- **Voice** — `voice-nav.js`, floating controls in `nav_scripts.html`.
- **Module-specific** — `emotion-quiz.js`, `learning-module.js`, `parent-dashboard.js`, `app-home.js`, `auth.js`, `wav-encoder.js`, `media-permissions.js`.
- **Screening** — Large self-contained template `dyslexia_screening.html` with step flow and Botpress.

### Supporting files at repository root

- Pretrained model artifacts (emotion HDF5, dyslexia joblib).
- Legacy or utility scripts (`train_model.py`, `generate_audio.py`, etc.) for offline model and asset preparation.
- `scripts/init_mongodb.py` and `scripts/migrate_sqlite_to_mongo.py` for database setup and one-time SQLite migration.

---

## Data layer (MongoDB)

MongoDB stores **documents in collections** (not SQL tables). The application uses database name `neurolearn` by default.

### Collection: `users`

Each document represents a student or parent account.

- Unique username and email.
- Password hash (never plain text).
- Role: `student` or `parent`.
- Display name.
- **link_code** (students only) — short code parents use to link accounts.
- **preferences** embedded object — font size, dyslexic font flag, high contrast, read-aloud (synced with browser where applicable).
- `created_at` timestamp.

### Collection: `parent_child_links`

- `parent_id` and `child_id` (references to user ObjectIds).
- `linked_at` timestamp.
- Unique compound index prevents duplicate links.

### Collection: `screening_results`

- `user_id` (student).
- `overall_score`, `risk_level`.
- `component_scores` (JSON map of skill areas).
- `recommendations` (JSON list of strings).
- `feature_importance` (optional JSON for explainability).
- `created_at` — supports history charts and “latest screening” on dashboards.

### Collection: `progress_events`

- `user_id`, `event_type` (e.g. dyslexia_screening, interactive_emotion, interactive_fingers, module_visit).
- `payload` (JSON details).
- `created_at` — powers streaks, activity breakdown, and timelines.

Indexes are created automatically at application startup (username, email, link_code, user+time on results and events).

---

## Authentication and roles

- **Registration** creates a user, initializes preferences, and assigns a family link code for students.
- **Login** establishes a server session with user id, role, display name, and username.
- **Protected routes** require login; parent-only APIs additionally require `role === parent`.
- **Students** hitting the home URL see the learning hub; **parents** are redirected to the parent dashboard.
- **Guest pages** (login, register, help) use minimal layouts without the full dashboard chrome where appropriate.

Sessions are cookie-based unless Redis is configured for centralized session storage in multi-instance deployments.

---

## Machine learning and computer vision

### Dyslexia screening pipeline

1. **Data collection** — Client gathers typed or spoken responses per subtest; optional handwriting image uploaded for feature extraction.
2. **Feature engineering** — Service computes accuracies for reading, spelling, letters, word matching, numbers, sentence copying, and handwriting-derived metrics.
3. **Inference** — Full submission path loads the joblib model bundle (classifier + scaler + feature order); simple path may use rule-based scoring when appropriate.
4. **Output** — Risk level, overall score, per-component scores, textual recommendations; persisted to `screening_results` and logged as a progress event.

### Emotion detection

- Webcam frame sent as base64 image to the server.
- Keras model predicts emotion category with confidence.
- Client-side **EmotionQuiz** adapts MCQ difficulty from emotion state and answer correctness.

### Face features

- MediaPipe Face Mesh returns normalized landmarks.
- Frontend maps coordinates to SVG overlays on the video feed (accounting for mirror and object-fit cover).

### Finger counting

- MediaPipe Hands detects hands; service counts extended fingers with handedness labels.
- Audio feedback via pre-recorded MP3s in `static/audio/numbers/` or speech synthesis fallback.

### Handwriting analysis

- Uploaded image processed for stroke and shape metrics merged into screening feature vector before final submit.

---

## Major user flows

### Student: first visit

Register → receive family link code → log in → land on home → explore learning paths → open dyslexia screening or interactive learning → activities record progress events → screening results appear on home summary API.

### Parent: monitoring

Register as parent → log in → open Parent Dashboard → enter child link code → view linked children → select child for detailed summary, charts, and recommendations → optional real-time notification channel via Socket.IO for certain actions.

### Screening (logged-in student)

Navigate to Dyslexia Screening → complete steps (standard font enforced) → optional speech for reading items → submit → view results → data stored under student id for parent and history endpoints.

### Interactive learning

Open Interactive Learning → choose module (emotion, face, fingers, drawing, games) → grant camera permission (localhost or HTTPS) → interact; server endpoints score vision tasks where applicable → close learning module returns to menu.

---

## Accessibility and inclusive design

- **OpenDyslexic font** — Optional global toggle (loaded via dedicated CSS with CDN-hosted font files); increases letter distinction for everyday browsing.
- **Screening exception** — Dyslexic font disabled on screening route so assessment text remains standardized.
- **High contrast mode** — Body-level class inverts key colors for low-vision users.
- **Text scaling** — Root font size adjusted in steps within safe min/max bounds.
- **Read aloud** — Uses Web Speech API with voice selection that avoids misreading Windows device names; strips emojis and UI chrome from spoken text; section and path-card read buttons on home.
- **Voice navigation** — Speech recognition triggers navigation and accessibility commands on supported browsers.
- **Floating controls** — Microphone and read-aloud buttons fixed bottom-left on dashboard pages.
- **Media permissions helper** — Guides users when camera/mic blocked on insecure LAN URLs.

Preferences partially stored in browser `localStorage` and partially in MongoDB user preferences for continuity.

---

## Real-time communication

Flask-SocketIO enables bidirectional events. Example use: parent notification when a student triggers a video-call request action from the screening flow. Event payloads include timestamps and child identifiers; clients subscribe through the Socket.IO client library included with the stack.

---

## Configuration and environment

Key environment variables (set in `.env` or hosting dashboard):

| Variable | Purpose |
|----------|---------|
| FLASK_SECRET_KEY | Session signing; must be strong in production |
| FLASK_DEBUG / FLASK_ENV | Development vs production behavior |
| HOST, PORT | Bind address; PORT must match platform (e.g. Render injects PORT) |
| MONGODB_URI | MongoDB connection string (Atlas: use URL-encoded password if it contains special characters) |
| MONGODB_DB_NAME | Database name (default neurolearn) |
| EMOTION_MODEL_PATH | Path to emotion HDF5 weights |
| DYSLEXIA_MODEL_PATH | Path to dyslexia joblib bundle |
| UPLOAD_FOLDER | Writable directory for uploads |
| MAX_CONTENT_LENGTH | Upload size cap |
| REDIS_URL | Optional Redis for sessions |
| USE_HTTPS | Local dev HTTPS for camera on LAN |
| SESSION_COOKIE_SECURE | Set when served over HTTPS in production |
| ENABLE_DEBUG_ROUTES | Gates experimental debug endpoints |

---

## Running locally

### Prerequisites

- Python 3.11 virtual environment with dependencies from `requirements.txt`.
- MongoDB running locally **or** MongoDB Atlas cluster with network access configured.
- Model files present in project root (emotion HDF5 and dyslexia joblib).
- Optional: ffmpeg on PATH for server-side audio fallback; optional Redis.

### Steps

1. Create and activate the project virtual environment.
2. Install Python dependencies.
3. Copy environment settings into `.env` (MongoDB URI, secret key, ports).
4. Start MongoDB or confirm Atlas connectivity.
5. Launch the app via `start.ps1` on Windows or `python run.py` using the venv interpreter.
6. Open **http://localhost:8080** (not the raw LAN IP unless HTTPS is enabled).
7. Verify **http://localhost:8080/healthz** reports healthy MongoDB and model status.

For camera/microphone on another device on the same network, enable HTTPS in configuration and install pyOpenSSL, then use the HTTPS URL with certificate acceptance.

---

## Deployment

NeuroLearn is containerized (Dockerfile includes Python dependencies, ffmpeg, OpenGL-related libs for OpenCV/MediaPipe, and model files). Production serving uses Gunicorn with a single Eventlet worker and dynamic port binding via `docker/start.sh`.

**Recommended hosting patterns:**

- **MongoDB Atlas** (free M0) for the database.
- **Render**, **Railway**, **Fly.io**, or **Oracle Cloud free VM** for the application container.
- **Not suitable for Vercel** — serverless limits conflict with long-lived Flask, Socket.IO, and TensorFlow.

Detailed free-deployment steps, Atlas IP whitelist notes, 502 troubleshooting, and SSL URI encoding are documented in **docs/DEPLOY-FREE.md**.

---

## Health checks and troubleshooting

**Health endpoint:** `/healthz` returns JSON status for application liveness, MongoDB connectivity, ML model file presence, and ffmpeg availability.

| Symptom | Likely cause |
|---------|----------------|
| App exits on start | MongoDB unreachable or invalid URI; check Atlas Network Access and password encoding |
| 502 on Render after deploy | Wrong PORT binding (fixed in start script) or worker OOM from TensorFlow on free tier |
| Camera blocked | Using HTTP on LAN IP; use localhost or HTTPS |
| Read-aloud reads emojis | Update to latest accessibility.js (emoji sanitization) |
| Finger counting silent | Missing MP3 assets; falls back to speech |
| Screening font looks “spaced” only | OpenDyslexic CDN; screening page uses standard Lexend |
| Build fails on Render | Flask version conflict with flask-session (resolved in requirements 2.3.x) |

---

## Security considerations

- Passwords hashed before storage; never log credentials.
- Login-required APIs return 401 for anonymous JSON requests; redirects for HTML.
- Parent–child data scoped by verified links in `parent_child_links`.
- Session cookies HttpOnly; Secure flag recommended in production HTTPS.
- Debug routes disabled by default in production configuration.
- File upload size limits enforced at Flask level.
- MongoDB credentials only in environment variables, not committed to git (`.env` gitignored).

---

## Limitations and future considerations

- **Memory footprint** — TensorFlow and MediaPipe require substantial RAM; free cloud tiers may kill workers under load.
- **Single-worker Socket.IO** — Horizontal scaling needs sticky sessions and Redis message queue for Socket.IO.
- **Browser dependence** — Speech and camera features vary by browser and OS.
- **Chatbot** — Hosted externally (Botpress); subject to third-party availability and privacy policies.
- **Assessment validity** — Screening is a supportive tool, not a clinical diagnosis; standard font enforced during test for fairness.

Potential enhancements: dedicated API versioning, automated tests, CDN for static media, separate ML inference service, email notifications for parents, and expanded game content wired through the learning-path progress API.

---

## Documentation map

| Document | Contents |
|----------|----------|
| **README.md** (this file) | Project overview, stack, architecture, features |
| **docs/DEPLOY-FREE.md** | MongoDB Atlas, Render, Oracle VM, Cloudflare Tunnel, deploy troubleshooting |
| **.env** (local, not in git) | Secrets and connection strings for development |

---

## Credits and context

NeuroLearn was developed as an inclusive education technology project (EDI Neurolearn), combining accessibility-first UI design with practical ML-assisted screening and parent engagement. The stack intentionally balances educational research goals (dyslexia feature analysis, emotion-aware difficulty) with deployability concerns documented for student and pilot deployments.

For questions about setup, deployment, or architecture, start with the health endpoint and **docs/DEPLOY-FREE.md**, then inspect service modules under `app/services/` for behavior specific to each feature area.
