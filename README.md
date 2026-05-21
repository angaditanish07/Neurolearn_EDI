# NeuroLearn (EDI Neurolearn)

## Accounts and progress

1. **Register** at http://127.0.0.1:8080/register as **Student** — save your **family link code**.
2. **Register** a second account as **Parent** — open **Parent Dashboard** and enter the child's link code.
3. Student completes **Dyslexia Screening** while logged in — results save to their profile.
4. Parent sees progress, scores, and recommendations on `/parent/dashboard`.

Default: SQLite database at `data/neurolearn.db` (created automatically).

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

## Health check

http://127.0.0.1:8080/healthz
