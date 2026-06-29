import io
import zipfile
from pathlib import Path

import requests

_NETLIFY_API = "https://api.netlify.com/api/v1"


def upload_to_netlify(html_path: Path, netlify_token: str, site_id: str = "") -> str:
    """Deploy html_path as index.html to a Netlify site. Returns the live URL."""
    if not netlify_token:
        raise ValueError("Netlify Token fehlt. Bitte in den Einstellungen eintragen.")

    headers = {"Authorization": f"Bearer {netlify_token}"}

    # Reuse existing site or create a new one
    if site_id:
        target_id = site_id
    else:
        resp = requests.post(f"{_NETLIFY_API}/sites", headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        target_id = data["id"]

    # Build zip with index.html + _headers to force correct content-type
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.html", html_path.read_bytes())
        zf.writestr("_headers", "/index.html\n  Content-Type: text/html; charset=utf-8\n")
    buf.seek(0)

    deploy_headers = {**headers, "Content-Type": "application/zip"}
    resp = requests.post(
        f"{_NETLIFY_API}/sites/{target_id}/deploys",
        headers=deploy_headers,
        data=buf.read(),
        timeout=90,
    )
    resp.raise_for_status()
    deploy = resp.json()

    url = deploy.get("deploy_ssl_url") or deploy.get("ssl_url") or deploy.get("url", "")
    if not url:
        raise ValueError(f"Netlify-Antwort enthält keine URL. Keys: {list(deploy.keys())}")
    return url


def send_telegram(bot_token: str, chat_id: str, text: str) -> None:
    """Send a text message via Telegram Bot API."""
    if not bot_token or not chat_id:
        raise ValueError("Telegram Bot-Token oder Chat-ID fehlt.")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    resp = requests.post(
        url,
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        timeout=15,
    )
    resp.raise_for_status()
