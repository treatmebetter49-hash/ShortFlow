## description: Erzwingt echtes Debugging statt blindem Herumfixen

Bei wiederkehrenden Fehlern gilt:

1. Keine neuen Features
2. Kein Refactor
3. Kein UI-Redesign
4. Keine Vermutungen

Stattdessen:

1. Fehler minimal reproduzieren
2. Exakte Datei + Funktion + Zeile finden
3. Ursache in maximal 3 Sätzen erklären
4. Erst danach Fix schreiben
5. Fix isoliert testen
6. Erst danach gesamten Workflow testen

WICHTIG:

* Keine echten API-Calls ohne User-Freigabe
* Mock-Modus klar sichtbar machen
* Mock-Dateien müssen gültig sein
* Niemals kaputte Dateien erzeugen
