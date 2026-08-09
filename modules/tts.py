from pathlib import Path

import requests

_VOICE_ID = "5KvpaGteYkNayiswuX2h"  # Wayne Steele
_MODEL = "eleven_turbo_v2_5"
_API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{_VOICE_ID}"


def generate_voiceover(text: str, output_path: Path, api_key: str) -> None:
    """Generate MP3 voiceover via ElevenLabs and save to output_path."""
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
                "speed": 1.15,
            },
        },
        timeout=60,
    )
    resp.raise_for_status()
    output_path.write_bytes(resp.content)
