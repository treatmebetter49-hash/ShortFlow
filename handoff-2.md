# ShortFlow Handoff — Session 2

**Datum:** 2026-07-05  
**Projekt:** `/Users/mathiaskunze/Downloads/ClaudeCode/ShortFlow`

---

## Was ShortFlow ist

macOS Desktop App (.app via PyInstaller + CustomTkinter) für automatisierte YouTube Shorts / Instagram Reels Produktion (WTF_Wissen_Official, Psychologie-Content).

---

## Was in dieser Session gemacht wurde

### 1. Settings Label geändert
- `"OpenAI API-Key:"` → `"Brain Tab API-Key:"` (neutral, provider-agnostisch)
- Entscheidung: kein Multi-Provider — OpenAI + FAL AI + ElevenLabs bleiben fix verdrahtet

### 2. build.sh gefixt
- `rm -rf dist/ShortFlow.app` → `rm -rf dist/` (verhindert Build-Fehler bei nicht-leerem dist-Ordner)

### 3. Tutorial PDF aktualisiert
- Verlauf-Streifen (Rot→Lila→Blau) oben/unten
- Settings: Netlify-Erklärung, iPhone-only Hinweis
- Kosten: ElevenLabs Free Tier erwähnt
- Seite 7 ("Häufige Fehler") gelöscht
- Kosten-Tabelle: Registrierungslinks + "getestete Erfahrungswerte" Hinweis
- Script: `/tmp/build_tutorial_pdf.py`
- Output: `ShortFlow-Tutorial.pdf`

### 4. Lila Akzentfarbe (#9b30ff) eingebaut
- CTk Theme-Override direkt im Code (kein File-Pfad-Problem)
- In `ui/app.py` via `ThemeManager.theme[...]["fg_color"]` nach `set_default_color_theme("blue")`
- Buttons, RadioButtons, Checkboxen, Switch, OptionMenu alle lila
- Funktioniert — App zeigt lila Buttons

### 5. Gradient Progressbar
- `ui/gradient_bar.py` erstellt — Canvas-basierte Bar die Pink→Lila rendert
- In `brain_tab.py` und `machine_tab.py` eingebaut (ersetzt CTkProgressBar)
- `configure(mode=...)` Aufruf in brain_tab entfernt (gilt nicht für Canvas)

### 6. Gradient Header "ShortFlow" — NOCH NICHT FERTIG
- Ziel: Oben in der App einen Canvas-Header mit "ShortFlow" in Pink→Lila Buchstabe für Buchstabe
- Problem: Font `"SF Display"` nicht im PyInstaller Bundle → `bbox` gibt None → frühzeitiger Abbruch → Header unsichtbar
- Letzter Fix: Font auf `"Helvetica"` geändert
- Build läuft gerade noch (`bg5aifc41`) — **noch nicht getestet**
- Code in `ui/app.py`: Methode `_draw_header()`, Canvas `self._header`

---

## Aktueller Build-Status

Build `bg5aifc41` läuft noch wenn du diese Session übernimmst. Warte auf die Task-Notification, dann App neu starten und schauen ob der Gradient-Header sichtbar ist.

Falls immer noch nicht sichtbar: Mögliche Ursachen:
- CTk übermalt den Canvas
- Canvas hat Höhe 0 trotz `height=52`
- Font-Rendering im Bundle anders

Fallback-Idee: Header als `ctk.CTkFrame` mit Label statt Canvas, und Gradient nur durch eine Farbe (#9b30ff) simulieren — kein echter Verlauf aber zuverlässig.

---

## Wichtige Dateien

| Datei | Inhalt |
|---|---|
| `ui/app.py` | App-Hauptdatei, ThemeManager-Override, `_draw_header()` |
| `ui/brain_tab.py` | Brain Tab, GradientProgressBar, lila Buttons |
| `ui/machine_tab.py` | Machine Tab, GradientProgressBar, lila Buttons |
| `ui/gradient_bar.py` | Canvas-basierte Pink→Lila Progressbar |
| `ui/settings_tab.py` | Settings, neutrale Labels |
| `build.sh` | PyInstaller Build (fixed) |
| `shortflow_theme.json` | Lila Theme (wird nicht mehr aktiv genutzt, ThemeManager direkt) |
| `/tmp/build_tutorial_pdf.py` | PDF-Generierungs-Script |
| `ShortFlow-Tutorial.pdf` | Fertiges Tutorial |
| `handoff.md` | Vorheriger Handoff (Session 1) |

---

## Designentscheidungen

- **Tabelle wird nicht angefasst** — User hat das explizit verboten, mehrfach betont
- **Rot = Fehlerfarbe** — nicht für Buttons oder Akzente verwenden
- **Lila #9b30ff** = Akzentfarbe (aus ShortFlow Logo)
- **Pink #e91e8c → Lila #9b30ff** = Verlauf (wie im Logo und HTML-Tabellen-Header)
- **Kein Multi-Provider** — zu aufwändig für aktuellen Nutzwert

---

## Suggested Skills

- `verify` — nach Build testen ob Header sichtbar ist
- `systematic-debugging` — wenn Header immer noch nicht erscheint
- `anthropic-skills:pdf` — falls PDF weitere Änderungen braucht
