# ShortFlow ausprobieren — Kurzanleitung

Danke, dass du ShortFlow testest! Die Einrichtung dauert ein paar Minuten. Hier steht alles Schritt für Schritt.

---

## 1. App starten

### Windows
1. ZIP-Datei entpacken (Rechtsklick → „Alle extrahieren").
2. Im Ordner `ShortFlow.exe` doppelklicken.
3. Windows zeigt beim ersten Mal eine blaue Warnung („Windows hat den PC geschützt"):
   → auf **„Weitere Informationen"** klicken → **„Trotzdem ausführen"**.
   (Die App ist harmlos, sie ist nur nicht kostenpflichtig zertifiziert.)

> Wichtig: Die Datei `ShortFlow.exe` und der Ordner `_internal` müssen **zusammen**
> im selben Ordner bleiben. Nicht nur die exe woanders hin kopieren.

### Mac
1. Die `.dmg`-Datei doppelklicken, ShortFlow ins Programme-Fenster ziehen.
2. Beim ersten Start meldet macOS evtl. „ShortFlow kann nicht geöffnet werden"
   oder „nicht verifizierter Entwickler":
   → **Rechtsklick** auf die App → **„Öffnen"** → im Dialog nochmal **„Öffnen"**.
   (Nur beim allerersten Start nötig.)
3. Falls „App ist beschädigt" erscheint: Terminal öffnen und einmal eingeben
   `xattr -cr /Applications/ShortFlow.app` — dann normal starten.

---

## 2. API-Keys eintragen (einmalig)

ShortFlow nutzt drei KI-Dienste. Du brauchst von jedem einen eigenen Schlüssel
(„API-Key"). Die Registrierung ist kostenlos, du zahlst nur die tatsächliche Nutzung
(Cent-Beträge pro Short). Ohne Keys kann die App nichts generieren.

| Dienst | Wofür | Key holen unter |
|--------|-------|-----------------|
| OpenAI | Themen/Texte (Brain) | https://platform.openai.com/api-keys |
| FAL AI | Bilder | https://fal.ai/dashboard/keys |
| ElevenLabs | Sprachausgabe | https://elevenlabs.io/app/settings/api-keys |

So geht's:
1. Bei den drei Diensten kostenlos registrieren.
2. Jeweils einen API-Key erstellen und kopieren.
3. In ShortFlow oben auf den Tab **„Settings"** gehen.
4. Die drei Keys in die passenden Felder einfügen, speichern.

> Deine Keys bleiben lokal auf deinem Rechner. Sie werden nicht an mich oder Dritte
> gesendet.

---

## 3. Loslegen

1. Tab **„Brain"**: Thema + Anzahl eingeben → generieren. Das erzeugt eine Tabelle
   mit Kurzvideo-Ideen.
2. Tab **„Machine"**: Ausgabe-Ordner wählen → **„Medien-Paket schnüren"**.
   ShortFlow legt pro Short einen Ordner an, generiert Bilder und Sprachausgabe.

---

## Feedback

Wenn etwas nicht funktioniert oder abstürzt:
- **Windows**: Es erscheint ein Fenster „ShortFlow – Startfehler" mit einer Meldung —
  mach davon bitte einen Screenshot.
- **Mac**: Falls die App sich beendet, liegt eine Datei `ShortFlow_log.txt` in deinem
  Benutzerordner — schick sie mir.

Danke fürs Testen!
