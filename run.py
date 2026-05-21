"""
Development server entry point.

  .\\venv\\Scripts\\python.exe run.py

Open http://127.0.0.1:8080 after you see the startup banner (port from .env).
Press Ctrl+C to stop.
"""
import os
import sys


def _relaunch_with_venv_if_needed():
    """Use project venv when system Python lacks dependencies."""
    root = os.path.dirname(os.path.abspath(__file__))
    if sys.platform == 'win32':
        venv_py = os.path.join(root, 'venv', 'Scripts', 'python.exe')
    else:
        venv_py = os.path.join(root, 'venv', 'bin', 'python')
    if not os.path.isfile(venv_py):
        return
    if os.path.normcase(os.path.realpath(sys.executable)) == os.path.normcase(
        os.path.realpath(venv_py)
    ):
        return
    try:
        import flask  # noqa: F401
    except ImportError:
        import subprocess
        print('Using venv Python (system Python is missing dependencies)...')
        raise SystemExit(subprocess.call([venv_py, *sys.argv]))


_relaunch_with_venv_if_needed()

# Load .env before any app imports
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _check_models():
    emotion = os.environ.get(
        'EMOTION_MODEL_PATH', 'fer2013_mini_XCEPTION.102-0.66.hdf5'
    )
    dyslexia = os.environ.get('DYSLEXIA_MODEL_PATH', 'dyslexia_model.joblib')
    missing = [p for p in (emotion, dyslexia) if not os.path.isfile(p)]
    if missing:
        print('WARNING: Missing model files (some features will fail until present):')
        for p in missing:
            print(f'  - {p}')
        print()


def main():
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '8080'))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'

    print('=' * 50)
    print('  NeuroLearn — starting development server')
    print('=' * 50)
    _check_models()

    try:
        from app import create_app
        from app.config import Config
        from app.extensions import socketio
    except ImportError as e:
        print('ERROR: Failed to import application.', file=sys.stderr)
        print(f'  {e}', file=sys.stderr)
        print(file=sys.stderr)
        print('Install dependencies:', file=sys.stderr)
        print('  .\\venv\\Scripts\\pip install -r requirements.txt', file=sys.stderr)
        sys.exit(1)

    try:
        flask_app = create_app()
    except Exception as e:
        print(f'ERROR: Could not create app: {e}', file=sys.stderr)
        sys.exit(1)

    display_host = '127.0.0.1' if host in ('0.0.0.0', '::') else host
    use_https = Config.USE_HTTPS
    print(f'  Camera/mic: use http://localhost:{port} (not http://192.168.x.x)')
    if use_https:
        print(f'  HTTPS URL:  https://127.0.0.1:{port}  (accept browser warning)')
        print(f'  HTTPS LAN:  https://<your-ip>:{port}  (camera works on network)')
    else:
        print(f'  Local URL:  http://localhost:{port}')
        print(f'  Health:     http://localhost:{port}/healthz')
        print('  Tip: set USE_HTTPS=1 in .env for HTTPS (needs: pip install pyopenssl)')
    print(f'  Debug mode: {debug}')
    print('  Press Ctrl+C to stop.')
    print('=' * 50)
    sys.stdout.flush()

    ssl_context = None
    if use_https:
        try:
            import OpenSSL  # noqa: F401
            ssl_context = 'adhoc'
        except ImportError:
            print('WARNING: USE_HTTPS=1 but pyopenssl missing. Run: pip install pyopenssl', file=sys.stderr)
            ssl_context = None

    try:
        socketio.run(
            flask_app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,
            ssl_context=ssl_context,
        )
    except OSError as e:
        winerr = getattr(e, 'winerror', None)
        if winerr in (10048, 10013) or 'address already in use' in str(e).lower():
            print(f'ERROR: Cannot bind to port {port}.', file=sys.stderr)
            if winerr == 10013:
                print('  Windows blocked this port (in use or reserved by Hyper-V).', file=sys.stderr)
            else:
                print('  Port is already in use by another process.', file=sys.stderr)
            print(f'  Fix: set PORT=8080 in .env (or stop the other app on port {port}).', file=sys.stderr)
            print('  PowerShell: Get-NetTCPConnection -LocalPort 5001 | Select OwningProcess', file=sys.stderr)
        else:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nServer stopped.')


if __name__ == '__main__':
    main()
