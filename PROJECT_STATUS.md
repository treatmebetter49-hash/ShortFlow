# ShortFlow — Project Status

**Stand:** 2026-05-12 (aktualisiert nach echtem Runtime-Test)
**Modus:** Python-Entwicklung (kein Packaging)

---

## Letzter Build

- `.app` gebaut mit PyInstaller 6.20.0 / Python 3.14.4
- Pfad: `dist/ShortFlow.app` (134 MB)
- Build-Befehl: `bash build.sh`
- Getestet: Prozess startet, läuft stabil

---

## Was funktioniert

- Brain: Thema + Anzahl → GPT-4o → JSON → DataFrame
- Machine: DataFrame → Ordner (Short01, Short02…) → Bilder via FAL AI
- CSV-Import in Machine-Tab
- Skip-Logik: bereits generierte Bilder werden übersprungen (dateibasiert)
- Resume nach Billing-Error
- Einstellungen: OpenAI Key, FAL Key, Output-Ordner (persistent in `~/Library/Application Support/ShortFlow/config.json`)
- XLSX / CSV / HTML-Export (table.py)
- macOS-Notification nach Abschluss (osascript)
- `.app` per Doppelklick startbar

## Echter Runtime-Test — 2026-05-12

- 2 Shorts sauber durchgelaufen, echte PNGs erzeugt (1.3–1.8 MB pro Bild)
- FAL-Response-Struktur bestätigt: `['images', 'timings', 'seed', 'has_nsfw_concepts', 'prompt']`
- Runtime-Debug-Logs ([DBG]-Zeilen) erscheinen korrekt in Reihenfolge
- Skip-Logik korrekt: `size=0 size_ok=False` bei nicht vorhandenen Dateien
- Kein alter Billing-State sichtbar — frische `client_id` pro Run bestätigt
- Offen: Billing-/Resume-Verhalten unter echtem Billing-Error noch nicht live getestet

---

## Bewusst zurückgestellt

- `.app`-Packaging pausiert — Core-App zuerst stabilisieren
- HTML-Dashboard nicht weiter priorisiert
- Copy-Buttons im Dashboard: später separat
- Textlänge/Stil: später als Einstellung planen
- Kein `.dmg`, kein Codesigning

---

## Offen / nicht implementiert

- Kein Video, kein Audio, kein Upload (by design)
- Resume über Tageswechsel bricht Skip-Logik (project_dir ist datumbasiert)
- Kein automatisches Retry bei transienten API-Fehlern
- Progress-Counter startet beim Resume immer bei 0
- `.app` nicht codesigniert (Gatekeeper: Rechtsklick → Öffnen nötig)
