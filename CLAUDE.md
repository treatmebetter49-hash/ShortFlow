# ShortFlow

## Architektur
- Brain: Thema + Anzahl → ChatGPT API → JSON → .xlsx/.csv
- Maschine: Tabelle → Ordner (Short01, Short02...) → Bilder generieren
- NICHT: Video, Audio, Upload
- Brain und Maschine strikt getrennt

## Datenstruktur
- ChatGPT liefert JSON: `{"shorts": [{"short", "hook", "text", "prompts": [], "titel", "beschreibung"}]}`
- Output: `Short01/bild01.png`, `bild02.png`, ...
- Tool validiert: ungültiges JSON · fehlende Prompts · leere Felder

## Regeln
- Einfachste Lösung, keine unnötigen Frameworks
- Keine automatischen Aktionen ohne User-Trigger
- Alle Prozesse müssen nachvollziehbar sein (Logs, Status)
- Stabilität vor Features
- Keine halbfertigen Features

## UI
- Input (links) | Vorschau (mitte) | Output (rechts)
- Nur notwendige Elemente

## Fehlerbehandlung
- Abfangen: ungültiges JSON · fehlende Prompts · API-Fehler · leere Felder
- Bei Fehler: Meldung anzeigen + Prozess stoppen

## Debugging
- Fehler minimal reproduzieren → exakte Datei + Funktion + Zeile
- Ursache in max. 3 Sätzen → dann Fix → isoliert testen → Gesamtworkflow
- Keine echten API-Calls ohne Freigabe
- Mock-Dateien müssen gültig sein
- Kein Refactor, keine neuen Features während Bugfixing
- Keine Fake-Erfolge oder simulierte Fixes
- Ein Bug gilt erst als gefixt, wenn der echte Repro-Fall erfolgreich getestet wurde
- Mock-Tests sind nur Vorprüfung, kein finaler Beweis
- Keine „wahrscheinlich gefixt"-Aussagen
- Vor jedem Fix: Ursache, Datei, Funktion, betroffener State nennen
- Nach jedem Fix: Beweis-Test mit Ergebnis dokumentieren
- Bei API-/Resume-Bugs muss Fresh Run vs Resume klar geloggt werden
- Bei Billing-Fehlern muss die aktuelle API-Response oder Exception-Quelle geloggt werden
- Reviewer muss prüfen, ob der echte Repro-Fall abgedeckt wurde

## Workflow
- Planungsmodus vor dem Coden (max. 5 Fragen)
- Erst Logik → dann UI
- Mock-Daten für API-Tests
- Fortschritt sichtbar machen bei langen Tasks
- Minimale Tokenverschwendung
