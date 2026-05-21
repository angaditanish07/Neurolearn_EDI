"""Audio conversion for speech recognition (WAV preferred; ffmpeg for WebM/MP4)."""
import io
import logging
import shutil
logger = logging.getLogger(__name__)


def ffmpeg_available():
    """Return True if ffmpeg/ffprobe is on PATH."""
    return shutil.which('ffmpeg') is not None


def prepare_audio_for_recognition(file_storage):
    """
    Read uploaded audio and return mono 16 kHz WAV bytes.
    WAV uploads work without ffmpeg; WebM/MP4 need ffmpeg + pydub.
    """
    from pydub import AudioSegment

    raw = file_storage.read()
    if not raw:
        raise ValueError('Empty audio file')

    filename = (getattr(file_storage, 'filename', None) or '').lower()
    content_type = (getattr(file_storage, 'content_type', None) or '').lower()

    is_wav = (
        filename.endswith('.wav')
        or 'wav' in content_type
        or raw[:4] == b'RIFF'
    )

    try:
        if is_wav:
            segment = AudioSegment.from_wav(io.BytesIO(raw))
        else:
            if not ffmpeg_available():
                raise RuntimeError(
                    'ffmpeg is not installed. Reading tests need ffmpeg on the server, '
                    'or use a browser that sends WAV (refresh the page and record again). '
                    'Windows: install ffmpeg and add it to PATH, then restart NeuroLearn.'
                )
            fmt = 'webm'
            if 'mp4' in content_type or filename.endswith('.mp4') or filename.endswith('.m4a'):
                fmt = 'mp4'
            segment = AudioSegment.from_file(io.BytesIO(raw), format=fmt)

        segment = segment.set_frame_rate(16000).set_channels(1)
        out = io.BytesIO()
        segment.export(out, format='wav')
        out.seek(0)
        return out.read()

    except Exception as e:
        err = str(e).lower()
        if 'ffmpeg' in err or 'avconv' in err or 'winerror 2' in err:
            raise RuntimeError(
                'ffmpeg is required to process this recording format. '
                'Install ffmpeg, add it to your system PATH, and restart the server. '
                'See README → Troubleshooting → Audio / ffmpeg.'
            ) from e
        raise
