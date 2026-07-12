# Plan: Retention-Check vor Hook-Feature-Einsatz

**Datum:** 2026-07-09
**Kontext:** Fortsetzung von `~/Desktop/handoff-2026-07-09-shortflow-hooks-part2.md`

## Vereinbart mit User

- Bis Dienstag (14.07.) bereits geplante Clips bleiben unangetastet.
- **Samstag (11.07.):** Retention-Daten der laufenden "Warum du…"-Serie prüfen.
  - Vorher Cache-Alter in `youtube_analytics.db` checken, ggf. Sync (`youtube_sync.py`) mit User abstimmen (echter API-Call).
  - `ratio_bucket` 0.0–0.15 gegen eigenen Kanalschnitt (letzte ~20 Shorts) vergleichen.
  - Faustregel: unter ca. 50–100 Views pro Video ist die Kurve zu verrauscht für eine belastbare Aussage.
- **Sonntag (12.07.):** 7 neue Clips generieren — Vorgehen abhängig vom Samstags-Ergebnis:
  - Einbruch am Anfang (0.0–0.15) unter Kanalschnitt → Hook-Fix ist der richtige Hebel, `regenerate_hooks_only`-Feature einsetzen (Branch `fix/hook-engine-psychology`, echter API-Call, Kosten vorher schätzen, User muss zustimmen).
  - Retention normal/gut, aber Views niedrig → Hooks waren nicht das Problem, Feature bringt nichts, stattdessen Thumbnail/Titel/Auffindbarkeit angehen.

## Offene Punkte (aus Handoff Teil 2)

1. Merge-Entscheidung: `fix/title-curiosity-gap` (`7951887`) + `fix/hook-engine-psychology` (`70c373f`) zusammenführen, vor nächster Live-Serie.
2. Branch-Entscheidung für `regenerate_hooks_only`-Feature (`modules/brain.py`, `ui/brain_tab.py`, aktuell uncommitted): gleicher Branch oder eigener Feature-Branch.
3. `regenerate_hooks_only` bisher nur mock-getestet, kein echter End-to-End-Lauf mit echtem OpenAI-Call.

## Diagnose-Regeln (Referenz)

Siehe Projekt-CLAUDE.md `YouTube-Analytics-Agent` bzw. Agent `~/.claude/agents/mira.md`:
- Immer gegen eigenen Kanalschnitt vergleichen, nicht generische Richtwerte.
- Zukunfts-`published_at` = geplant, nicht als Flop werten.
- Retention-Einbruch 0.0–0.15 → Hook-/Thumbnail-Problem. Einbruch 0.4–0.7 → Pacing/Länge. Views niedrig, Retention normal → Auffindbarkeit.
- Datenlage dünn → offen sagen statt raten.
