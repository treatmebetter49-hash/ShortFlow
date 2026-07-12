# ShortFlow — Schnellstart-Tutorial

ShortFlow automatisiert die Content-Produktion für YouTube Shorts und Instagram Reels. Es generiert Texte, Bildprompts, Voiceovers und eine mobile IG-Übersicht.

---

## 1. Einrichtung (Settings)

Beim ersten Start: oben rechts auf **Settings** klicken.

| Feld | Was eintragen |
|------|--------------|
| OpenAI API-Key | Key von platform.openai.com |
| Bildgenerator API-Key | Key von fal.ai |
| Output-Ordner | Wo die Shorts gespeichert werden sollen |
| ElevenLabs API-Key | Key von elevenlabs.io (für Voiceover) |
| Netlify Token | Token von netlify.com → User Settings → Applications |
| Telegram Bot-Token | Token von @BotFather in Telegram |
| Telegram Chat-ID | Deine Chat-ID (via getUpdates abrufbar) |

**Wichtig:** Nach dem Eintragen auf **SPEICHERN** klicken.

ElevenLabs, Netlify und Telegram sind optional — ohne diese Keys funktionieren Brain und Machine trotzdem vollständig.

---

## 2. Brain Tab — Tabelle generieren

Hier wird der Content erstellt.

### Schritte:

1. **Thema** eingeben, z.B. `Psychologie`
2. **Modus wählen:**
   - *Einzeln* — du gibst die Anzahl der Shorts manuell ein
   - *Monat* — ShortFlow generiert automatisch für jeden Tag des gewählten Monats
3. Bei Monat-Modus: **Monat und Jahr** auswählen
4. Auf **TABELLE GENERIEREN** klicken
5. Warten — der Fortschrittsbalken zeigt den Status

### Was wird generiert:
- Hook (5 Varianten, die beste wird automatisch gewählt)
- Voiceover-Text (250–270 Zeichen)
- Titel und Beschreibungen für YouTube + Instagram
- 10 Bildprompts pro Short als filmisches Storyboard
- Energie-Typ (phonk / action / wissen / clever)

### Nach der Generierung:
- **Tabelle öffnen** — öffnet die HTML-Tabelle im Browser
- **→ WEITER ZU MACHINE** — wechselt zum Machine Tab
- **iPhone IG Export** — erstellt mobile Ansicht, lädt auf Netlify hoch und schickt Link per Telegram

---

## 3. Machine Tab — Bilder und Voiceover generieren

Hier werden die Bilder und MP3s erstellt.

### Schritte:

1. Entweder direkt aus dem Brain Tab auf **→ WEITER ZU MACHINE** klicken, oder eine vorhandene CSV-Datei über **CSV laden** öffnen
2. Output-Ordner prüfen (wird aus Settings übernommen)
3. Auf **GENERIEREN** klicken

### Was passiert:
- Pro Short wird ein Unterordner erstellt (`Short147/`, `Short148/`, ...)
- 10 Bilder werden generiert (`Bild01.png` bis `Bild10.png`)
- Eine Voiceover-Datei wird erstellt (`Short147.mp3`)
- Bereits vorhandene Dateien werden übersprungen (Skip-Logik)

### Bei Unterbrechung:
- Bei leerem Guthaben (FAL oder ElevenLabs): Konto aufladen, dann **FORTSETZEN** klicken
- ShortFlow macht exakt dort weiter wo er aufgehört hat

---

## 4. Ordnerstruktur

```
Output-Ordner/
└── Psychologie'26/
    └── 07.Juli'26/
        ├── Short147/
        │   ├── Bild01.png – Bild10.png
        │   ├── Short147.mp3
        │   └── prompts.txt
        ├── Short148/
        │   └── ...
        ├── Psychologie26-Short-Tabelle.html
        └── Psychologie26-Short-Tabelle-IG.html
```

---

## 5. iPhone IG Export

Nach der Generierung im Brain Tab auf **iPhone IG Export** klicken:

1. HTML-Datei wird im Monatsordner gespeichert
2. Datei wird auf Netlify hochgeladen
3. Telegram-Bot schickt dir den Link per DM
4. Link auf dem iPhone öffnen → Kopieren-Buttons funktionieren direkt

---

## 6. Empfohlener Workflow

```
Brain → Tabelle generieren
     → iPhone IG Export (Link ans Telefon)
     → WEITER ZU MACHINE

Machine → Generieren (läuft durch, Resume bei Bedarf)

Premiere Pro → Bilder importieren + MP3 als Voiceover
            → Text-Overlay, Musik, Schnitt
            → Export + Upload
```

---

## 7. Kosten (ca.)

| Dienst | Kosten |
|--------|--------|
| OpenAI GPT-4o | ~0,10–0,20 $ pro Monat (31 Shorts) |
| FAL AI (Flux Pro) | ~0,05 $ pro Bild × 10 × 31 = ~15 $ |
| ElevenLabs Starter | 5 $/Monat (~30.000 Zeichen) |
| Netlify | kostenlos |

---

## 8. Häufige Fehler

| Fehler | Lösung |
|--------|--------|
| `API Key ungültig` | Key in Settings prüfen und neu speichern |
| `Guthaben leer` | FAL- oder ElevenLabs-Konto aufladen, dann FORTSETZEN |
| App startet nicht | Rechtsklick auf ShortFlow.app → Öffnen |
| Tabelle hängt | App neu starten, CSV laden, FORTSETZEN |
