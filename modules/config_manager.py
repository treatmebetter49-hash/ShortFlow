import json
from pathlib import Path

_CONFIG_DIR = Path.home() / "Library" / "Application Support" / "ShortFlow"
_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = _CONFIG_DIR / "config.json"

DEFAULTS = {
    "openai_key": "",
    "fal_key": "",
    "output_dir": str(Path.home() / "Desktop"),
    "first_run_music_setup_done": False,
    "music_mapping_enabled": False,
    "music_tracks": [
        {"label": "Aggressiv / Phonk",      "energie": "phonk",  "track": ""},
        {"label": "Action / Dringend",       "energie": "action", "track": ""},
        {"label": "Wissen / Ruhig",          "energie": "wissen", "track": ""},
        {"label": "Clever / Überraschend",   "energie": "clever", "track": ""},
    ],
}


def load() -> dict:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return dict(DEFAULTS)


def save(config: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
