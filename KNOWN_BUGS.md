# ShortFlow — Known Bugs

Siehe auch: [[PROJECT_STATUS]] · [[ARCHITECTURE]] · [[2026-06-29-Session]]

Format: `ID · Status · Beschreibung · Ursache · Fix`

---

## Behoben

### BUG-001 · BEHOBEN · 2026-05-12
**Billing-Error bleibt nach Resume bestehen**

Beschreibung: Nach leerem Guthaben + Nachladen + Fortsetzen erscheint weiterhin derselbe Billing-Error, obwohl FAL-Konto aufgeladen ist.

Ursache: `fal_client.subscribe` (modul-global) nutzt intern einen geteilten HTTP-Connection-Pool. Nach `402 Payment Required` bleibt die Verbindung mit `keep-alive` im Pool. Der nächste `subscribe`-Aufruf zieht dieselbe Verbindung und bekommt erneut `402`.

Fix: Statt `fal_client.subscribe` wird jetzt `fal_client.SyncClient(key=fal_key)` pro `generate_images`-Aufruf erstellt. Jeder Run bekommt eine frische Instanz mit eigenem Connection-Pool.

Datei: `modules/machine.py`, Zeile 104

---

### BUG-002 · BEHOBEN · 2026-05-12
**config.json im App-Bundle (read-only) — API-Keys konnten nicht gespeichert werden**

Beschreibung: Im `.app`-Bundle liegt `config.json` innerhalb des Bundles, das macOS als read-only behandelt. Einstellungen konnten nicht gespeichert werden.

Ursache: `CONFIG_PATH = Path(__file__).parent.parent / "config.json"` zeigt im Bundle auf einen read-only Pfad.

Fix: Pfad auf `~/Library/Application Support/ShortFlow/config.json` umgestellt.

Datei: `modules/config_manager.py`, Zeile 4–6

---

### BUG-005 · BEHOBEN · 2026-07-22
**Prompts alter Shorts gehen bei erneuter Generierung verloren**

Beschreibung: Wurden einem Monats-Projekt neue Shorts hinzugefügt, überschrieb `save_prompts_json()` die `.prompts.json` komplett mit nur den neuen Rows — Prompts bereits vorhandener Shorts waren danach weg.

Ursache: `save_prompts_json()` baute das JSON ausschließlich aus dem übergebenen `df`, ohne mit dem bestehenden Dateiinhalt zu mergen. `ui/brain_tab.py:300` übergibt bei Nachgenerierung nur das neue Batch.

Fix: Bestehende JSON wird jetzt geladen und mit den neuen Werten aktualisiert (`dict.update`) statt überschrieben.

Datei: `modules/table.py`, Zeile 643

Beweis: Repro-Test — bestehende JSON (`Short01`, `Short02`) + neues df (`Short03`, `Short04`) ergab vorher nur `Short03`/`Short04`, danach alle vier Einträge.

---

### BUG-006 · BEHOBEN · 2026-07-22
**localStorage-Fertig-Markierungen gehen bei Neugenerierung an anderem Tag verloren**

Beschreibung: Der localStorage-Key-Präfix für "Fertig"-Markierungen enthielt das aktuelle Renderdatum. Wurde die HTML-Tabelle eines Projekts an einem späteren Tag erneut geschrieben (z. B. neue Shorts angehängt), änderte sich der Präfix, und bereits gesetzte Markierungen waren unter dem neuen Präfix nicht mehr auffindbar.

Ursache: `today = date.today().strftime(...)` floss in `_sf_pfx_js` ein, obwohl das Präfix stabil pro Projekt-Datei sein muss, nicht pro Renderzeitpunkt.

Fix: Präfix wird jetzt aus einem SHA256-Hash des aufgelösten Datei-Pfads gebildet (`sf_<hash>_`), bleibt damit über mehrere Renders derselben Datei stabil. `today`-Variable komplett entfernt, da sonst nirgends im Template verwendet.

Datei: `modules/table.py`, Zeile 113–120, 365

Beweis: Zwei aufeinanderfolgende `save_html()`-Aufrufe auf dieselbe Datei erzeugen denselben `_sfPfx`.

---

### BUG-007 · BEHOBEN · 2026-07-22
**Tkinter-Thread-Safety-Verletzung in `_deploy()` (Netlify-Upload)**

Beschreibung: Der Netlify/Telegram-Upload läuft in einem Background-Thread, aktualisierte dabei aber das Status-Label direkt (`self._status_lbl.configure(...)`) statt über den Hauptthread — anders als `_generate`/`_regenerate_hooks_thread`, die korrekt `self.after(0, ...)` nutzen. Tkinter-Widget-Zugriffe aus Nicht-Hauptthreads sind undefiniert/unsicher.

Ursache: `_deploy()` in `ui/brain_tab.py` rief `.configure()` direkt im Thread auf.

Fix: Alle drei Status-Updates laufen jetzt über `self.after(0, _set_status, text)`.

Datei: `ui/brain_tab.py`, Zeile 336–349

---

### BUG-008 · BEHOBEN · 2026-07-22
**Stale `after()`-Timer können Phasen-Animation eines neuen Laufs überspringen lassen**

Beschreibung: `_advance_phase`/`_tick_phase4` planten `after()`-Callbacks, die nur über die Flags `_animating`/`_current_phase` no-op'ten. Ein liegengebliebener Timer aus einem vorherigen Lauf konnte während eines neuen Laufs feuern und dessen `_current_phase` unerwartet vorspringen lassen (kein `after_cancel()` im gesamten File vorhanden).

Ursache: Fehlendes Timer-Tracking/Cancelling beim Start eines neuen Laufs bzw. bei Reset nach Erfolg/Fehler.

Fix: Pending-Timer-ID wird jetzt in `self._phase_after_id` gehalten und per `_cancel_phase_timer()` vor jedem Neuplanen sowie in `_on_success`, `_on_error` und `_set_status` (Laufstart) gecancelt.

Datei: `ui/brain_tab.py`, Zeile 360–398, 542–551

---

### BUG-009 · BEHOBEN · 2026-07-22
**Repo-Root `config.json` mit echten API-Keys war git-getrackt**

Beschreibung: `config.json` im Repo-Root stand schon in `.gitignore`, war aber seit dem allerersten Commit getrackt (Ignore greift nicht rückwirkend) und enthielt echte `openai_key`/`fal_key`-Werte. Betrifft nicht den Laufzeit-Pfad der App (`~/Library/Application Support/ShortFlow/config.json`), war ein Dev-Leftover.

Fix: `git rm --cached config.json` — lokale Datei bleibt erhalten, Tracking gestoppt. `config.json.example` als Referenz-Template ergänzt.

Datei: `config.json` (Repo-Root)

Offen bleibt: Keys stehen weiterhin in der Git-Historie (History-Rewrite bewusst nicht gemacht, siehe Commit `dc217df`). Key-Rotation bei OpenAI/FAL ist manueller Schritt des Repo-Owners.

---

### BUG-003 · BEHOBEN · 2026-07-22
**Resume über Monatswechsel (nicht Mitternacht) ignoriert bereits generierte Bilder — nur im CSV-Fallback-Pfad**

Beschreibung ursprünglich: „Läuft eine Generierung über Mitternacht, wird beim Resume ein neuer `project_dir` mit dem neuen Datum erstellt.“ Codex-Analyse (2026-07-22) hat das präzisiert: Der normale Brain→Machine-Workflow ist davon **nicht** betroffen, da `brain_tab.py` den `project_dir` vorab bestimmt und über `load_from_brain()` unverändert weiterreicht — Tageswechsel ändert daran nichts. Auch der Fallback-Pfad in `machine.py` (wenn `project_dir=None`) hängt nur von Monat+Jahr ab, nicht vom Tag — reiner Mitternachtswechsel innerhalb des Monats erzeugt gar keinen neuen Ordner.

Real reproduzierbar bleibt ein engerer Fall: **CSV-Ladeworkflow in `ui/machine_tab.py`** (`_load_csv()`) setzt nie einen `project_dir`, der bleibt `None`. Startet eine Generierung z. B. am 31.07. und wird nach Abbruch am 01.08. fortgesetzt, berechnete der Fallback bei jedem Aufruf neu aus `date.today()` — der Ordner wechselt von `.../07.Juli'26` auf `.../08.August'26`, Skip-Logik findet dort keine vorhandenen Bilder.

Ursache: `project_dir`-Fallback in `generate_images()` wurde bei *jedem* Aufruf neu aus dem aktuellen Datum berechnet statt einmalig bestimmt und vom Caller zwischen Start und Resume persistiert.

Fix: Berechnung in `machine.resolve_project_dir(output_dir, topic)` gekapselt. `ui/machine_tab.py:_start()` ruft das jetzt nur auf, wenn `self._project_dir is None` ist, und speichert das Ergebnis dauerhaft in `self._project_dir` — Resume verwendet danach denselben Ordner, unabhängig vom Datum.

Datei: `modules/machine.py` (neue Funktion `resolve_project_dir`, ersetzt Inline-Berechnung ca. Zeile 96–133), `ui/machine_tab.py:_start()`

Beweis: Repro-Test simuliert `date.today()` = 31.07.2026 dann 01.08.2026 — `resolve_project_dir()` liefert ohne Persistierung zwei unterschiedliche Pfade (Baseline-Bug bestätigt); mit der neuen Persistenz-Logik in `_start()` wird die Funktion bei Resume gar nicht erneut aufgerufen, der ursprüngliche Ordner bleibt maßgeblich.

---

## Geprüft — nicht reproduzierbar

### BUG-004 · GEPRÜFT — NICHT REPRODUZIERBAR · 2026-07-22
**Progress-Counter startet bei Resume immer bei 0**

Ursprüngliche Beschreibung: Beim Fortsetzen beginnt die Fortschrittsanzeige bei 0 %, auch wenn bereits 8 von 10 Shorts fertig sind. Springt erst dann, wenn im aktuellen Run ein Short abgeschlossen wird.

Codex-Analyse (2026-07-22): `counter = [0]` wird in `_start()` zwar bei jedem Aufruf neu initialisiert, aber `modules/machine.py` sendet die `✓ Fertig`-Message pro Zeile unabhängig davon, ob Bilder neu generiert oder nur per `[SKIP]` übersprungen wurden (bereits vorhandene PNGs) — und das noch vor dem optionalen TTS-Block. Beim Resume laufen bereits fertige Shorts dadurch in Sekundenschnelle durch und zählen den Counter hoch; der Balken springt schnell auf den korrekten Stand (z. B. 80 % bei 8/10), bleibt aber nicht bis zum ersten neuen Short bei 0 %.

Es gibt nur einen sehr kurzen visuellen Zwischenmoment bei 0 %, während Skip-Logs und Tk-`after()`-Callbacks abgearbeitet werden. Ein Vorab-Scan (Counter beim Start auf bereits fertige Shorts vorinitialisieren) würde nur diesen kurzen Übergang entfernen, dupliziert dafür bestehende Validierungslogik aus `machine.py` — kein Fix umgesetzt, da kein spürbarer Nutzwert.

Datei: `ui/machine_tab.py`, Zeile ~126–136; `modules/machine.py`, Zeile ~207

---

## Offen

Aktuell keine offenen Bugs.

Aktuell keine offenen Bugs.
