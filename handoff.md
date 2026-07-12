# ShortFlow Handoff

**Datum:** 2026-07-05  
**Projekt:** ShortFlow — macOS Desktop App (.app via PyInstaller + CustomTkinter)  
**Nutzer:** Mathias (Matzimoto) — Solo-Gründer, KI-Beratung

---

## Was ist ShortFlow

Automatisierte Content-Produktion für YouTube Shorts / Instagram Reels für den Kanal WTF_Wissen_Official (Psychologie-Content).

- **Brain Tab:** Thema → GPT-4o → JSON → Tabelle (Hook, Text, Bildprompts, Beschreibungen)
- **Machine Tab:** Tabelle → FAL AI Bilder (Flux Pro) + ElevenLabs Voiceover (Wayne Steele, `5KvpaGteYkNayiswuX2h`, `eleven_multilingual_v2`)
- **IG Export:** HTML-Tabelle → Netlify Deploy → Telegram Bot → iPhone Safari

---

## Projektpfad

```
/Users/mathiaskunze/Downloads/ClaudeCode/ShortFlow/
```

Wichtige Dateien:
- `main.py` — Einstiegspunkt
- `ui/brain_tab.py` — Brain Tab inkl. IG Export + Netlify + Telegram
- `ui/machine_tab.py` — Machine Tab, startet generate_images()
- `ui/settings_tab.py` — Settings mit CTkScrollableFrame
- `modules/machine.py` — Bildgenerierung + TTS-Aufruf
- `modules/tts.py` — ElevenLabs TTS
- `modules/netlify_telegram.py` — Netlify Upload + Telegram sendMessage
- `modules/config_manager.py` — Config laden/speichern
- `build.sh` — PyInstaller Build (fixed: löscht jetzt `dist/` komplett)
- `ShortFlow-Tutorial.pdf` — Fertiges Tutorial PDF (dark theme)
- `/tmp/build_tutorial_pdf.py` — PDF-Generierungs-Script (reportlab)

---

## Was in dieser Session gemacht wurde

### Settings Label geändert
- `"OpenAI API-Key:"` → `"Brain Tab API-Key:"` (neutral, provider-agnostisch)
- Entscheidung: ShortFlow bleibt fix auf OpenAI + FAL AI + ElevenLabs — Multi-Provider wäre zu aufwändig für den Nutzen

### build.sh gefixt
- War: `rm -rf dist/ShortFlow.app build/ ShortFlow.spec` — ließ `dist/ShortFlow/` stehen → Build-Fehler
- Fix: `rm -rf dist/ build/ ShortFlow.spec`

### Tutorial PDF aktualisiert
Alle User-Wünsche umgesetzt:
1. Farbverlauf-Streifen (Rot → Lila → Blau) oben und unten statt solid red
2. Settings: Erklärung warum Netlify (Instagram Business App auf PC unbrauchbar), iPhone-only Hinweis
3. Tabellen auf Seiten 3 + 5 zentriert
4. Disclaimer: "mein persönlicher Workflow, keine Garantie"
5. Unterbrechung-Hinweis: FAL.ai braucht Zeit bis Guthaben sync, erst dann FORTSETZEN
6. ElevenLabs Free Tier erwähnt (reicht für 30 Shorts/Monat)
7. Footer: größer, fett, zentriert
8. Seite 7 ("Häufige Fehler") gelöscht
9. Kosten-Tabelle: zeigt jetzt Dienst + Registrierungslink + Hinweis dass es getestete Erfahrungswerte sind (kein Abo-Zwang bei OpenAI/FAL)

---

## Aktueller Stand

- App läuft stabil
- Build funktioniert sauber
- PDF ist fertig unter `ShortFlow-Tutorial.pdf`
- Settings zeigen neutrale Labels

## Offene Punkte / mögliche nächste Schritte

- Tester-Onboarding vorbereiten (wer bekommt die App zuerst?)
- Evtl. Kurzanleitung für API-Key Erstellung (OpenAI, FAL AI)
- Evtl. App als DMG verpacken für einfache Weitergabe

---

## Wichtige Designentscheidungen

- **Kein Multi-Provider:** OpenAI + FAL AI + ElevenLabs fix verdrahtet. Flexibilität erst wenn ShortFlow verkauft wird.
- **Labels neutral:** "Brain Tab API-Key" statt "OpenAI API-Key" — signalisiert Offenheit ohne Code-Aufwand
- **ElevenLabs Key:** Wayne Steele Voice, `eleven_multilingual_v2`, Hook + Text kombiniert als Voiceover
- **Netlify Site ID:** `ed653129-3bd5-482e-b4e1-82287a1713d6` (shortflowtabelle) hardcoded als Default

---

## Suggested Skills

- `anthropic-skills:pdf` — wenn weitere PDF-Änderungen nötig
- `verify` — nach Code-Änderungen App testen
- `systematic-debugging` — bei Build- oder API-Fehlern
