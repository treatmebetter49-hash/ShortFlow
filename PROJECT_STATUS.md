# ShortFlow — Project Status

Siehe auch: [[ARCHITECTURE]] · [[KNOWN_BUGS]] · [[handoff]] · [[2026-06-29-Session]] · [[2026-06-22-Session]] · [[2026-06-15-Session]]

**Stand:** 2026-06-29
**Modus:** .app (PyInstaller, codesigned, dist/ShortFlow.app — Dock zeigt direkt darauf)

---

## Letzter Build

- `.app` gebaut mit PyInstaller / Python 3.14
- Pfad: `dist/ShortFlow.app` (Dock-App zeigt direkt hierauf, kein cp nötig)
- Build-Befehl: `python3 -m PyInstaller ShortFlow.spec -y && codesign --force --deep --sign - dist/ShortFlow.app`
- Codesigned: ja (ad-hoc)

---

## Was funktioniert

- Brain: Thema + Anzahl → GPT-4o → JSON → DataFrame
- Machine: DataFrame → Ordner → Bilder via FAL AI
- Monat-Modus: Monat + Jahr wählbar, generiert Anzahl Tage des Monats
- Ordner-Logik: findet bestehenden Topic-Ordner (z.B. `Psychologie'26`) automatisch, legt Monatsordner darin an
- Short-Nummerierung: läuft automatisch weiter ab höchster vorhandener Nummer
- Skip-Logik: bereits generierte Bilder werden übersprungen
- Resume nach Billing-Error
- Einstellungen: OpenAI Key, FAL Key, Output-Ordner (persistent)
- XLSX / CSV / HTML-Export
- macOS-Notification nach Abschluss
- Hook-System: 5 Varianten pro Short (2x Widerspruch, 1x Opinion, 1x Story, 1x frei)
- Batch-Generierung: 31 Shorts = 7 Batches à 5 (parallel via ThreadPoolExecutor)
- **Konzept-Liste upfront**: `_generate_concepts()` generiert N einzigartige Konzepte vorab, Batches bekommen je einen Slice → keine Inter-Batch-Dopplungen
- Startup-Scanner: liest bestehende Hooks + Short-Nummern aus Vault beim App-Start
- iPhone IG Export: HTML-Seite für mobiles Copy-Paste, optional Netlify-Deploy + Telegram
- **Bestätigt: Juli 2026, Short147 in `Psychologie'26/07.Juli'26`** ✅

---

## Änderungen Session 2026-06-21 / 2026-06-22

### Hook-Prompt verbessert ✅
- `modules/brain.py`: Hook-Formel eingebaut basierend auf 100-Hook-Bibliothek
- Mindestens 2 Widerspruchs-Hooks, 1 Opinion-Hook, 1 Story-Hook pro Short
- Basiert auf Analyse: die 2k-View-Shorts hatten Widerspruchs-Hooks ("Dein Gehirn spürt keinen Schmerz")

### Doppelter Ordner-Bug gefixt ✅
- `modules/brain.py` + `modules/machine.py`: beide suchen nach bestehendem Topic-Ordner mit Suffix
- Logik: `d.name.startswith(safe_topic)` findet `Psychologie'26` statt neu `Psychologie` anzulegen
- Bestätigt: kein Duplikat mehr

### make_project_dir bekommt Monat + Jahr ✅
- `modules/brain.py`: Parameter `month` und `year` hinzugefügt
- `ui/brain_tab.py`: übergibt `start_date.month` und `start_date.year`

### Hänger-Bug gefixt ✅
- Ursache: `max_tokens=32768` + `_BATCH_SIZE=10` → OpenAI-Client wartete unbegrenzt
- Fix: `_BATCH_SIZE` 10 → **5**, `max_tokens` 32768 → **16384**, `timeout` 120 → **90**
- Bestätigt: 31 Shorts (Juli 2026) laufen durch, kein Hänger

### Status-Text sichtbar ✅
- `ui/brain_tab.py`: Topic-Eingabefeld width 300 → 150

---

## Offen / bekannte Probleme

- JSON-Fehler bei manchen Generierungen (Sonderzeichen in Hooks) — tritt seltener auf mit kleineren Batches
- Kein Video, kein Audio, kein Upload (by design)
- Resume über Tageswechsel bricht Skip-Logik
- Progress-Counter startet beim Resume bei 0

---

## Kannal-Analyse WTFWissen (Stand 2026-06-21)

- 83 Abonnenten, 52.638 Views gesamt seit Februar 2026
- 131 Shorts veröffentlicht
- Top-Short: "Das weiß fast niemand" — 2.038 Views
- Erkenntnis: Beste Shorts haben eine einzige Bildwelt + Widerspruchs-Hook
- Schwache Shorts: zu viele verschiedene Bildwelten, philosophische Hooks

---

## Workflow (wie Mathias arbeitet)

1. ShortFlow Brain → Tabelle generieren (31 Shorts für Juli, startet ab Short147)
2. ShortFlow Machine → Bilder generieren
3. Adobe Premiere Pro → Harte Cuts, Text-Overlay, Musik
4. Upload YouTube Shorts + Instagram Reels
- Ca. 24 Minuten pro 2 Shorts in Premiere
- 30 Shorts werden in 1-2 Tagen produziert
