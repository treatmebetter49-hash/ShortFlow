# ShortFlow — Architecture

Siehe auch: [[PROJECT_STATUS]] · [[KNOWN_BUGS]] · [[handoff]]

---

## Überblick

Zwei strikt getrennte Phasen:

```
Brain   →  Thema + Anzahl  →  GPT-4o  →  DataFrame (JSON)
Machine →  DataFrame        →  FAL AI  →  PNG-Dateien auf Disk
```

Keine direkte Verbindung zwischen Brain und Machine — Übergabe nur via DataFrame.

---

## Ordnerstruktur

```
ShortFlow/
├── main.py                  # Entry point: App().mainloop()
├── modules/
│   ├── brain.py             # OpenAI-Call → DataFrame
│   ├── machine.py           # FAL-Call → PNG-Dateien
│   ├── table.py             # XLSX / CSV / HTML-Export + CSV-Import
│   └── config_manager.py    # Lesen/Schreiben config.json
├── ui/
│   ├── app.py               # CTkTabview, Tab-Routing
│   ├── brain_tab.py         # Brain-UI
│   ├── machine_tab.py       # Machine-UI + Threading
│   └── settings_tab.py      # Settings-UI
├── build.sh                 # PyInstaller Build-Skript
└── dist/ShortFlow.app       # Fertiges macOS Bundle
```

---

## Datenfluss

```
BrainTab
  └─ brain.generate_table(topic, count, openai_key)
       └─ GPT-4o → JSON → pd.DataFrame
            └─ on_go_to_machine(df, topic)
                 └─ MachineTab.load_from_brain(df, topic)

MachineTab._start()
  └─ Thread → machine.generate_images(df, output_dir, fal_key, cb, topic)
       └─ pro Short → Ordner anlegen
            └─ pro Prompt → fal_client.SyncClient(key).subscribe()
                 └─ URL → requests.get() → .png speichern
```

---

## DataFrame-Schema

| Spalte | Inhalt |
|---|---|
| Short | "Short01", "Short02" … |
| Hook | Einstiegssatz |
| Text | Haupttext |
| Titel | YouTube-Titel |
| Beschreibung | YouTube-Beschreibung |
| Prompts | Bild-Prompts, getrennt durch ` \|\| ` |
| Status | "Ausstehend" / "Fertig" |

---

## Output-Struktur auf Disk

```
output_dir/
└── DD_MM_YY_Thema/
    ├── Short01/
    │   ├── Bild01.png
    │   └── Bild02.png …
    └── Short02/
        └── …
```

`project_dir` wird aus `date.today()` + Topic berechnet. Bei gleichem Tag + Topic = gleicher Ordner → Skip-Logik greift.

---

## Konfiguration

- Pfad: `~/Library/Application Support/ShortFlow/config.json`
- Felder: `openai_key`, `fal_key`, `output_dir`
- Wird bei jedem `get_config()`-Aufruf frisch von Disk gelesen (kein Cache)

---

## .app Build

- Tool: PyInstaller 6.20.0
- Python: 3.14.4 (System)
- Tkinter + Tcl/Tk: im Bundle enthalten
- customtkinter Assets: `--collect-all customtkinter`
- Neu: keine Session wird zwischen Runs geteilt (`fal_client.SyncClient` pro Lauf)
- Build: `bash build.sh` → `dist/ShortFlow.app`
