import os
import subprocess
import tempfile
from pathlib import Path

import requests

_VOICE_ID = "5KvpaGteYkNayiswuX2h"  # Wayne Steele
_MODEL = "eleven_turbo_v2_5"
_API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{_VOICE_ID}"
_SPEED = 1.15


def generate_voiceover(text: str, output_path: Path, api_key: str) -> None:
    if not api_key:
        raise ValueError("ElevenLabs API-Key fehlt. Bitte in den Einstellungen eintragen.")

    resp = requests.post(
        _API_URL,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": text,
            "model_id": _MODEL,
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.51,
                "style": 0.76,
            },
        },
        timeout=60,
    )
    resp.raise_for_status()

    if _SPEED == 1.0:
        output_path.write_bytes(resp.content)
        return

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_in:
        tmp_in.write(resp.content)
        tmp_in_path = tmp_in.name
    tmp_out_path = tmp_in_path.replace(".mp3", "_fast.mp3")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_in_path, "-filter:a", f"atempo={_SPEED}", tmp_out_path],
            check=True, capture_output=True,
        )
        output_path.write_bytes(Path(tmp_out_path).read_bytes())
    finally:
        os.unlink(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)
