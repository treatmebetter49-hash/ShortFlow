import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Callable

import fal_client
import requests
import pandas as pd

from modules import tts as tts_module

MODEL = "fal-ai/flux-pro/v1.1"

_MONTHS_DE = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]

_BILLING_KEYWORDS = (
    "exhausted balance",
    "insufficient balance",
    "insufficient credits",
    "insufficient funds",
    "quota exceeded",
    "out of credits",
    "payment required",
    "payment failed",
)

# ── Mock / Debug ──────────────────────────────────────────────────────────
# Set True to skip all real API calls. Set False only for production use.
USE_MOCK_IMAGE_API = False
_MIN_REAL_IMAGE_BYTES = 100_000  # mock PNGs ~7 KB, echte FAL-Bilder >1 MB

# Outcomes consumed in order, one per image generation call.
# After exhaustion every remaining call returns "ok".
#   "ok"      → write a valid 720×1280 placeholder PNG
#   "billing" → raise BillingError (simulates empty account)
#   "timeout" → raise a generic timeout exception
#   "error"   → raise a generic API exception
_MOCK_OUTCOMES: list[str] = ["ok", "ok"]  # nach Listenende: immer "ok"
_mock_idx: list[int] = [0]


def reset_mock() -> None:
    _mock_idx[0] = 0


def _mock_call(output_path: Path) -> None:
    import time
    time.sleep(0.4)
    i = _mock_idx[0]
    _mock_idx[0] += 1
    outcome = _MOCK_OUTCOMES[i] if i < len(_MOCK_OUTCOMES) else "ok"
    if outcome == "billing":
        raise BillingError("Mock: Guthaben leer (simuliert)")
    if outcome == "timeout":
        raise Exception("Mock: Verbindungs-Timeout")
    if outcome == "error":
        raise Exception("Mock: API-Fehler 500")
    # "ok" — write a valid PNG so the skip-logic sees the file as done
    _write_mock_png(output_path)


def _is_valid_png(path: Path) -> bool:
    try:
        return path.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
    except OSError:
        return False


def _write_mock_png(output_path: Path) -> None:
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (720, 1280), color=(28, 32, 48))
    draw = ImageDraw.Draw(img)
    label = output_path.stem          # e.g. "Bild01"
    folder = output_path.parent.name  # e.g. "Short01"
    draw.rectangle([40, 40, 680, 1240], outline=(80, 100, 160), width=3)
    draw.text((360, 580), "MOCK", fill=(80, 100, 200), anchor="mm")
    draw.text((360, 660), folder, fill=(160, 170, 200), anchor="mm")
    draw.text((360, 730), label, fill=(120, 140, 180), anchor="mm")
    img.save(str(output_path), "PNG")


def _sanitize_topic(topic: str) -> str:
    topic = topic.strip().replace(" ", "_")
    topic = re.sub(r"[^\w]", "", topic)
    return topic[:40]


class BillingError(Exception):
    pass


def generate_images(
    df: pd.DataFrame,
    output_dir: str | Path,
    fal_key: str,
    progress_cb: Callable[[str], None],
    topic: str = "",
    project_dir: Path | None = None,
    elevenlabs_key: str = "",
) -> pd.DataFrame:
    fal_client_instance = None
    if USE_MOCK_IMAGE_API:
        progress_cb("⚠️  MOCK-MODUS AKTIV – keine echten API-Kosten")
    else:
        if not fal_key:
            raise ValueError("FAL API Key fehlt. Bitte in den Einstellungen eintragen.")
        fal_client_instance = fal_client.SyncClient(key=fal_key)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if project_dir is not None:
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
        progress_cb(f"Projekt-Ordner: {project_dir.parent.name}/{project_dir.name}")
    else:
        today = date.today()
        safe_topic = re.sub(r'[<>:"/\\|?*]', '', topic).strip() or "Shorts"
        month_name = f"{today.month:02d}.{_MONTHS_DE[today.month - 1]}'{today.year % 100:02d}"
        existing = None
        for d in output_dir.iterdir():
            if d.is_dir() and d.name.startswith(safe_topic):
                existing = d
                break
        topic_dir = existing if existing else output_dir / safe_topic
        project_dir = topic_dir / month_name
        project_dir.mkdir(parents=True, exist_ok=True)
        progress_cb(f"Projekt-Ordner: {topic_dir.name}/{month_name}")
    progress_cb(f"[DBG] Projektordner (absolut): {project_dir}")

    df = df.copy()

    for idx, row in df.iterrows():
        short_name = str(row["Short"]).strip()
        if not short_name or short_name.lower() == "nan":
            continue

        folder = project_dir / short_name
        folder.mkdir(exist_ok=True)

        raw_prompts = str(row.get("Prompts", ""))
        prompts = [p.strip() for p in raw_prompts.split("||") if p.strip()]

        err_count = 0
        if not prompts:
            progress_cb(f"\n[{short_name}] Starte...")
            progress_cb(f"  [WARN] Keine Prompts gefunden — Bilder übersprungen")
        else:
            prompts_txt = folder / "prompts.txt"
            if not prompts_txt.exists():
                prompts_txt.write_text(
                    "\n".join(f"{i}. {p}" for i, p in enumerate(prompts[:10], 1)),
                    encoding="utf-8",
                )

            is_real = not USE_MOCK_IMAGE_API
            prompt_list = prompts[:10]
            already_done = sum(
                1 for i in range(1, len(prompt_list) + 1)
                if _is_valid_png(folder / f"Bild{i:02d}.png")
                and (not is_real or (folder / f"Bild{i:02d}.png").stat().st_size > _MIN_REAL_IMAGE_BYTES)
            )
            remaining = len(prompt_list) - already_done
            run_type = "RESUME" if already_done > 0 else "FRESH"
            if already_done > 0:
                progress_cb(f"\n[{short_name}] Fortsetzen — {already_done} vorhanden, {remaining} ausstehend")
            else:
                progress_cb(f"\n[{short_name}] Starte — {remaining} Bilder")
            progress_cb(f"  [DBG] {run_type} is_real={is_real} prompts={len(prompt_list)}")

            for i, prompt in enumerate(prompt_list, start=1):
                bild_path = folder / f"Bild{i:02d}.png"
                png_ok = _is_valid_png(bild_path)
                size = bild_path.stat().st_size if bild_path.exists() else 0
                size_ok = not is_real or size > _MIN_REAL_IMAGE_BYTES
                if png_ok and size_ok:
                    progress_cb(f"  [SKIP] Bild{i:02d}.png (size={size})")
                    continue
                progress_cb(f"  [DBG] Bild{i:02d} png_ok={png_ok} size={size} size_ok={size_ok}")

                progress_cb(f"  [GEN]  Bild{i:02d}.png...")
                try:
                    _generate_and_save(prompt, bild_path, fal_client_instance, log_cb=progress_cb)
                    progress_cb(f"  [OK]   Bild{i:02d}.png")
                except BillingError as exc:
                    progress_cb(f"  [BILLING] {exc.__cause__ or exc}")
                    raise
                except Exception as exc:
                    err_count += 1
                    progress_cb(f"  [ERR]  Bild{i:02d}.png — {exc}")

        if err_count:
            progress_cb(f"[{short_name}] ✓ Fertig ({err_count} Fehler)")
        else:
            progress_cb(f"[{short_name}] ✓ Fertig")

        # TTS — nur wenn Key gesetzt und voiceover.mp3 noch nicht existiert
        if elevenlabs_key:
            mp3_path = folder / f"{short_name}.mp3"
            if mp3_path.exists():
                progress_cb(f"  [SKIP] {short_name}.mp3")
            else:
                hook = str(row.get("Hook", "")).strip()
                text = str(row.get("Text", "")).strip()
                voiceover_text = f"{hook} {text}".strip()
                if voiceover_text:
                    try:
                        progress_cb(f"  [TTS]  {short_name}.mp3...")
                        tts_module.generate_voiceover(voiceover_text, mp3_path, elevenlabs_key)
                        progress_cb(f"  [OK]   {short_name}.mp3")
                    except Exception as exc:
                        progress_cb(f"  [ERR]  voiceover.mp3 — {exc}")

        df.at[idx, "Status"] = "Fertig"

    progress_cb("\n✅ Alle Shorts verarbeitet.")
    _mac_notify()
    return df


def _generate_and_save(prompt: str, output_path: Path, client=None, log_cb=None) -> None:
    if USE_MOCK_IMAGE_API:
        _mock_call(output_path)
        return
    if client is None:
        raise RuntimeError("Interner Fehler: kein FAL-Client übergeben.")
    if log_cb:
        log_cb(f"  [DBG] client_id={id(client)} model={MODEL}")
    try:
        result = client.subscribe(
            MODEL,
            arguments={
                "prompt": prompt,
                "image_size": {"width": 720, "height": 1280},
                "num_images": 1,
                "output_format": "png",
            },
            client_timeout=120,
        )
    except Exception as exc:
        billing_match = any(kw in str(exc).lower() for kw in _BILLING_KEYWORDS)
        if log_cb:
            log_cb(f"  [DBG] exc_type={type(exc).__name__} billing_match={billing_match}")
            log_cb(f"  [DBG] exc_str={str(exc)[:300]}")
        if billing_match:
            raise BillingError("Guthaben leer. Bitte Anbieter-Konto aufladen.") from exc
        raise
    if log_cb:
        keys = list(result.keys()) if isinstance(result, dict) else type(result).__name__
        log_cb(f"  [DBG] FAL response keys={keys}")
    images = result.get("images") if isinstance(result, dict) else None
    if not images or not isinstance(images, list):
        raise ValueError(f"Unerwartete FAL-Antwort – kein 'images'-Feld. Keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
    image_url = images[0].get("url") if isinstance(images[0], dict) else None
    if log_cb:
        log_cb(f"  [DBG] image_url={'...'+image_url[-40:] if image_url else None}")
    if not image_url:
        raise ValueError(f"Kein URL im FAL-Ergebnis. Erhalten: {images[0]}")
    response = requests.get(image_url, timeout=90)
    if log_cb:
        log_cb(f"  [DBG] HTTP {response.status_code} content_length={len(response.content)}")
    response.raise_for_status()
    output_path.write_bytes(response.content)


def _mac_notify() -> None:
    try:
        subprocess.run(
            ["osascript", "-e",
             'display notification "Fertig! Alle Bilder generiert." with title "ShortFlow" sound name "Glass"'],
            check=False,
        )
    except Exception:
        pass
