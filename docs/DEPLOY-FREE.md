# Deploy NeuroLearn for free

NeuroLearn needs **three things** in production:

1. **Web app** (Flask + ML models)
2. **MongoDB** (you already use **MongoDB Atlas M0** — free)
3. **HTTPS** (for camera/mic on phones — optional but recommended)

Free hosting is possible, but **full ML features** (emotion + dyslexia models) need **~1–2 GB RAM**. Many “free” PaaS tiers only give **512 MB**, which often crashes on TensorFlow.

---

## Recommended free setups

| Goal | Best option | Cost |
|------|-------------|------|
| **Full app** (all features) | [Oracle Cloud Always Free](https://www.oracle.com/cloud/free/) VM + Docker | $0 |
| **Demo / auth / screening only** (lighter) | [Render](https://render.com) free web service | $0 (sleeps when idle) |
| **Show classmates your PC** (no cloud build) | [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/) | $0 |
| **Database** | MongoDB Atlas M0 | $0 (already configured) |

---

## Option A — MongoDB Atlas (keep as-is)

You already have Atlas. For production:

1. **Network Access** → Add `0.0.0.0/0` (or your server IP only, stricter).
2. **Database Access** → user with read/write on `neurolearn`.
3. `.env` on the server:

```env
MONGODB_URI=mongodb+srv://USER:PASSWORD@cluster....mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=neurolearn
FLASK_SECRET_KEY=<long-random-hex-64-chars>
FLASK_ENV=production
FLASK_DEBUG=0
SESSION_COOKIE_SECURE=1
```

**Password rule:** if the password contains `@`, encode it as `%40` in the URI.

---

## Option B — Render.com (free web tier, easiest PaaS)

**Limits:** 512 MB RAM, sleeps after ~15 min idle, cold start ~30–60 s.  
**May fail** if TensorFlow runs out of memory — try anyway; if it crashes, use Option C.

### Steps

1. Push the project to **GitHub** (include model files `*.hdf5`, `*.joblib` in repo or use [Git LFS](https://git-lfs.com/) if > 100 MB).

2. [render.com](https://render.com) → **New +** → **Web Service** → connect repo.

3. Settings:
   - **Environment:** Docker (uses project `Dockerfile`)
   - **Instance type:** Free
   - **Health check path:** `/healthz`

4. **Environment variables** (Render dashboard → Environment):

| Key | Value |
|-----|--------|
| `MONGODB_URI` | Your Atlas URI (password URL-encoded) |
| `MONGODB_DB_NAME` | `neurolearn` |
| `FLASK_SECRET_KEY` | Random 64-char hex |
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |
| `PORT` | `8080` |
| `SESSION_COOKIE_SECURE` | `1` |
| `ENABLE_DEBUG_ROUTES` | `0` |

5. Deploy → open `https://your-app.onrender.com`.

6. Atlas **Network Access** must allow Render (often `0.0.0.0/0` for M0 dev).

**Note:** Camera/mic on Render HTTPS works on the public URL; students use that link, not `192.168.x.x`.

**Build error `flask-session` vs `flask==2.0.3`:** fixed in `requirements.txt` (Flask 2.3.3 + Werkzeug 2.3.7). Push and redeploy.

**502 Bad Gateway after “service is live”:** usually the app listened on port `8080` but Render routes to `$PORT` (e.g. `10000`). Fixed via `docker/start.sh` — **remove `PORT=8080` from Render env vars** if you added it; let Render set `PORT` automatically.

**Still 502 after port fix:** open **Logs** (runtime, not build) for `Killed`, `MemoryError`, or MongoDB errors — free tier may run out of RAM loading TensorFlow.

**`SSL handshake failed` / `TLSV1_ALERT_INTERNAL_ERROR` from Atlas:**

1. **Atlas → Network Access → Add IP Address → Allow access from anywhere** (`0.0.0.0/0`). Render uses changing IPs; without this, Atlas often fails with SSL errors.
2. Confirm `MONGODB_URI` uses `mongodb+srv://...` and password `@` is encoded as `%40`.
3. Redeploy after the app update (`certifi` + CA certs in Docker).

---

## Option C — Oracle Cloud free VM (best for full ML, $0)

Always-free **ARM VM** (up to 4 OCPU / 24 GB RAM) can run the full Docker stack.

### Outline

1. Create Oracle account → **Compute** → **Ampere A1** instance (Ubuntu 22.04).
2. Open firewall: ports **22**, **80**, **443**, **8080** (or only 80/443 behind nginx).
3. SSH into the VM:

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
# log out and back in
git clone <your-repo-url> neurolearn && cd neurolearn
```

4. Create `.env` on the server (same variables as Atlas section above).

5. Build and run:

```bash
docker compose up -d --build
```

6. Open `http://<VM-public-IP>:8080` or put **Caddy/nginx** in front for HTTPS.

MongoDB stays on **Atlas** — no need to install MongoDB on the VM.

---

## Option D — Cloudflare Tunnel (free “deploy” from your laptop)

Good for **class demos** without cloud RAM limits. Your PC runs the app; Cloudflare gives a public HTTPS URL.

1. Install [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/).
2. Start NeuroLearn locally: `python run.py`
3. In another terminal:

```bash
cloudflared tunnel --url http://localhost:8080
```

4. Share the `https://....trycloudflare.com` URL.  
5. Keep the PC awake and the terminal open.

Atlas URI in `.env` still works from your machine.

---

## Option E — Railway / Fly.io

- **Railway:** small monthly credit; similar to Render, set env vars + Dockerfile.
- **Fly.io:** `fly launch` + `fly deploy` with the existing `Dockerfile`; free allowance is limited.

Same env vars as Render. Watch RAM for TensorFlow.

---

## Checklist before any public deploy

- [ ] Change `FLASK_SECRET_KEY` to a strong random value (not the dev placeholder).
- [ ] `FLASK_DEBUG=0`, `ENABLE_DEBUG_ROUTES=0`
- [ ] Atlas user password is strong; URI uses `%40` for `@` in password.
- [ ] Model files exist on the server (`fer2013_mini_XCEPTION....hdf5`, `dyslexia_model.joblib`).
- [ ] Visit `/healthz` → `"mongodb": true`, `"status": "ok"`.
- [ ] Register a test student + parent and link with family code.

---

## What will not work on strict free tiers

- **Large concurrent ML traffic** on 512 MB instances.
- **Always-on** without sleep (Render free sleeps).
- **Bundling MongoDB on the same 512 MB box** — use Atlas instead (you already do).

---

## Quick test after deploy

```text
GET https://your-domain/healthz
POST https://your-domain/api/register  (create student)
GET  https://your-domain/login
```

If the container exits immediately, check logs for `MemoryError` or TensorFlow — move to Oracle VM or disable heavy routes in a slim build.
