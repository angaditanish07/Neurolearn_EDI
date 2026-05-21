# NeuroLearn (EDI Neurolearn)

## Accounts and progress

1. **Register** at http://127.0.0.1:8080/register as **Student** — save your **family link code**.
2. **Register** a second account as **Parent** — open **Parent Dashboard** and enter the child's link code.
3. Student completes **Dyslexia Screening** while logged in — results save to their profile.
4. Parent sees progress, scores, and recommendations on `/parent/dashboard`.

**Database:** MongoDB (see [MongoDB setup](#mongodb-setup) below).

## Quick start (Windows, no Docker)

1. Open PowerShell in this folder.

2. If script activation is blocked, run once:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

3. Start the server (pick one):

   **Option A — recommended**
   ```powershell
   .\start.ps1
   ```

   **Option B — direct Python**
   ```powershell
   .\venv\Scripts\python.exe run.py
   ```

4. Open in browser: **http://localhost:8080** (port is set in `.env` as `PORT=8080`)

### Camera and microphone (important)

Browsers **block** camera/mic on `http://192.168.x.x` (shows "Not secure").

| What you want | URL to use |
|---------------|------------|
| Learning on **this PC** | **http://localhost:8080** |
| Learning from **phone/tablet** on same Wi‑Fi | Set `USE_HTTPS=1` in `.env`, run `pip install pyopenssl`, restart server, open `https://<your-pc-ip>:8080` and accept the certificate warning |

5. Stop the server with **Ctrl+C**.

You should see `NeuroLearn — starting development server` and `Server is running` in the terminal. If the prompt returns immediately with no message, run Option B and read any error text.

## Docker (optional)

Docker only works if **Docker Desktop is installed and running**.

```powershell
docker compose up --build
```

Redis is optional (`REDIS_URL` can stay empty in `.env` for cookie sessions).

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `can't open file app.py` | Use `run.py` or `start.ps1` — `app.py` was removed after refactor |
| `python run.py` shows nothing then exits | Run `.\venv\Scripts\python.exe run.py` (not system Python) |
| Port error (10013 / in use) | Change `PORT=8080` in `.env`, or stop the old server: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 5001).OwningProcess -Force` |
| Docker pipe error | Start Docker Desktop, or skip Docker and use `run.py` |
| Missing models | Keep `fer2013_mini_XCEPTION.102-0.66.hdf5` and `dyslexia_model.joblib` in project root |
| **Reading / audio not working** | See **Audio & ffmpeg** below |

### Audio & ffmpeg

**Dyslexia screening (read aloud)** sends audio to the server for speech-to-text. The app converts recordings to **WAV in the browser** when possible (no ffmpeg needed). If that fails, the server needs **ffmpeg** to decode WebM/MP4.

**Check:** open http://localhost:8080/healthz — `"ffmpeg": true` means server-side fallback is available.

**Install ffmpeg on Windows (recommended):**

1. Download a build from https://www.gyan.dev/ffmpeg/builds/ (release `ffmpeg-release-essentials.zip`) or install with winget:
   ```powershell
   winget install Gyan.FFmpeg
   ```
2. Add ffmpeg to PATH (installer often does this), or put `ffmpeg.exe` in a folder on your PATH.
3. Verify in a **new** PowerShell window:
   ```powershell
   ffmpeg -version
   ```
4. Restart NeuroLearn (`python run.py`).

**Finger counting** uses MP3 files under `static/audio/numbers/` if present; otherwise the browser speaks the number (no ffmpeg).

**Read aloud / voice nav** use the browser Web Speech API (no ffmpeg).

## MongoDB setup

MongoDB does not use SQL **tables** — it uses **collections** (like tables) and **documents** (like rows). NeuroLearn uses four collections:

| Collection | Purpose |
|------------|---------|
| `users` | Accounts (student/parent), passwords, link codes, preferences |
| `parent_child_links` | Parent ↔ student family links |
| `screening_results` | Dyslexia screening scores per student |
| `progress_events` | Activity log (modules, games, screenings) |

Indexes are created automatically when the app starts.

### 1. Install MongoDB

**Windows (recommended):**

```powershell
winget install MongoDB.Server
```

Or download [MongoDB Community Server](https://www.mongodb.com/try/download/community) and install as a service.

**macOS:** `brew install mongodb-community` then `brew services start mongodb-community`

**Linux:** follow [MongoDB install docs](https://www.mongodb.com/docs/manual/administration/install-on-linux/) for your distro.

### 2. Configure `.env`

```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=neurolearn
```

**MongoDB Atlas (cloud):** create a free cluster, get the connection string, and set:

```env
MONGODB_URI=mongodb+srv://USER:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=neurolearn
```

### 3. Install Python dependency

```powershell
.\venv\Scripts\pip install pymongo
```

### 4. Initialize collections (optional)

The app creates indexes on startup. To verify manually:

```powershell
.\venv\Scripts\python.exe scripts\init_mongodb.py
```

### 5. Migrate old SQLite data (optional)

If you have `data/neurolearn.db` from before:

```powershell
.\venv\Scripts\python.exe scripts\migrate_sqlite_to_mongo.py
```

Then **register again or log in again** — user IDs are now MongoDB ObjectIds (long hex strings), not integers.

### Useful MongoDB shell commands

```javascript
// Open shell: mongosh
use neurolearn
db.users.find().pretty()
db.screening_results.find().pretty()
db.progress_events.find().sort({ created_at: -1 }).limit(10)
db.parent_child_links.find().pretty()
```

## Deploy for free

See **[docs/DEPLOY-FREE.md](docs/DEPLOY-FREE.md)** for:

- **MongoDB Atlas** (database — you already use this)
- **Render.com** — easiest free Docker deploy (`render.yaml` included)
- **Oracle Cloud free VM** — best for full TensorFlow/MediaPipe features
- **Cloudflare Tunnel** — free public HTTPS link to your local `python run.py`

## Health check

http://127.0.0.1:8080/healthz — should show `"mongodb": true`
