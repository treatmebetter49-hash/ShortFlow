# Windows-exe selbst auf GitHub bauen

So baust du jederzeit selbst eine frische Windows-Version von ShortFlow — ohne Windows-Rechner, ohne Terminal. GitHub baut sie für dich in der Cloud.

## Einmal-Voraussetzung

Deine Code-Änderungen müssen auf GitHub sein (gepusht). Solange du in Claude Code arbeitest, macht das die Session. Danach ist alles Weitere reines Klicken im Browser.

## Schritt für Schritt

1. **Actions-Seite öffnen:**
   https://github.com/treatmebetter49-hash/ShortFlow/actions

2. In der linken Spalte auf **"Build Windows EXE"** klicken.

3. Rechts erscheint der Knopf **"Run workflow"** (grau/blau).
   - Drauf klicken
   - Branch **main** stehen lassen
   - Nochmal auf den grünen **"Run workflow"** klicken

4. Nach ein paar Sekunden taucht oben ein neuer Lauf mit gelbem Punkt auf.
   Warten, bis der Punkt **grün** wird (ca. 3–4 Minuten). Seite ggf. neu laden.

5. Auf den **grünen Lauf klicken** (auf den Titel).

6. Ganz unten auf der Seite, im Kasten **"Artifacts"**, liegt
   **"ShortFlow-Windows"**. Drauf klicken → es lädt eine ZIP-Datei runter.

7. ZIP entpacken. Der Ordner enthält `ShortFlow.exe` und den Ordner `_internal`.
   **Beides gehört zusammen** — nie nur die exe alleine kopieren, sonst startet sie nicht.

8. Auf einem Windows-PC: `ShortFlow.exe` doppelklicken.
   - Beim ersten Start warnt Windows evtl. ("Windows hat den PC geschützt")
     → **"Weitere Informationen"** → **"Trotzdem ausführen"**.

## Wichtig zum Testen

Die exe läuft auf normalen, halbwegs aktuellen Windows-PCs (das bestätigt der
automatische Start-Test im Build). Deine **Windows-VM auf dem Mac ist als
Testumgebung ungeeignet** — die alte Intel-i5-CPU der VM bringt numpy/pandas
zum sofortigen Absturz, obwohl mit der exe alles in Ordnung ist. Zum echten
Testen brauchst du einen richtigen Windows-PC.

## Wenn ein Build fehlschlägt (roter Punkt)

Auf den roten Lauf klicken → auf **"build"** → den rot markierten Schritt
aufklappen. Dort steht der Fehler im Klartext. Text kopieren und mir schicken,
dann fixe ich es gezielt.

## Wo ist der Bauplan?

- Workflow-Datei: `.github/workflows/build-windows.yml`
- Build-Rezept (was mit rein muss): `ShortFlow-windows.spec`
