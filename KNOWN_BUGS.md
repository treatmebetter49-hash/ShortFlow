# ShortFlow — Known Bugs

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

## Offen

### BUG-003 · OFFEN
**Resume nach Tageswechsel ignoriert bereits generierte Bilder**

Beschreibung: Läuft eine Generierung über Mitternacht, wird beim Resume ein neuer `project_dir` mit dem neuen Datum erstellt. Die Skip-Logik findet keine Dateien im neuen Ordner und generiert alle Bilder nochmal.

Ursache: `project_name` wird aus `date.today()` berechnet — kein persistenter Pfad zwischen Runs.

Datei: `modules/machine.py`, Zeilen 109–113

Workaround: Keiner. Generierungen möglichst nicht über Mitternacht lassen.

---

### BUG-004 · OFFEN
**Progress-Counter startet bei Resume immer bei 0**

Beschreibung: Beim Fortsetzen beginnt die Fortschrittsanzeige bei 0 %, auch wenn bereits 8 von 10 Shorts fertig sind. Springt erst dann, wenn im aktuellen Run ein Short abgeschlossen wird.

Ursache: `counter = [0]` in `_start()` wird bei jedem Aufruf neu initialisiert, bereits abgeschlossene Shorts aus vorherigen Runs werden nicht gezählt.

Datei: `ui/machine_tab.py`, Zeilen 120–127

Auswirkung: Nur visuell — keine funktionale Beeinträchtigung.
