import json
import re
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from openai import OpenAI, AuthenticationError, RateLimitError

from modules import hook_engine

COLUMNS = ["Short", "Datum", "Tag", "Hook", "Text", "Titel", "YTBeschreibung", "IGBeschreibung", "Prompts", "Status", "EnergiTyp"]
PROMPT_COUNT = 10
_BATCH_SIZE = 10
_MAX_RETRIES = 3
_HOOK_MAX = 70
_LEN_MIN = 250    # Hook + Text Minimum
_LEN_MAX = 270    # Hook + Text Maximum
_LEN_TARGET = 260 # Ziel-Mitte für Kürzen/Erweitern

_SYSTEM = (
    "Du bist ein TikTok/Reels-Voiceover-Autor. "
    "Erstelle {count} Shorts zum Thema '{topic}'.\n\n"

    "HOOK-VARIANTEN:\n"
    "Erstelle für jeden Short genau 5 Hook-Varianten im Feld 'hook_variants' (Array mit 5 Strings). "
    "Maximal 70 Zeichen pro Hook. Keine Fragen. Keine 'Was wäre wenn'-Formulierungen. "
    "Kein 'Stell dir vor'-Stil. Direkte Aussage, harte Neugier, sofortige Spannung.\n"
    "Thematisch: Gaming → kompetitiv, direkt. Natur → emotional, atmosphärisch. Sport → actiongeladen.\n"
    "Die 5 Varianten nutzen verschiedene Einstiegswörter und Hook-Typen (Story, Fakt, Warnung, Meinung, Zahl).\n\n"

    "Creator-Stil-Muster (nur als Rhythmus-Vorlage — nicht wörtlich kopieren):\n"
    "{pattern_examples}\n\n"

    "TEXT:\n"
    "Du redest DIREKT zu einer Person — nicht über ein Thema. Persönliche Ansprache (du/dich/dein). "
    "Emotional, konkret, überraschend. Kein Lehrton, keine Erklärungen, keine Definitionen.\n"
    "VERBOTEN: Doku-Stil, Wikipedia-Stil, 'Von X bis Y'-Aufzählung, Fachbegriffe erklären.\n"
    "VERBOTEN-Beispiel: 'Manipulation nutzt subtile Techniken, um Menschen zu beeinflussen.'\n"
    "RICHTIG-Beispiel: 'Du wirst gerade manipuliert — und du merkst es noch nicht einmal.'\n"
    "Ca. 190–200 Zeichen reiner Text. Hook + Text zusammen: 250–270 Zeichen.\n\n"

    "BILDPROMPTS — exakt einhalten:\n"
    "Erstelle für jeden Short exakt 10 englische Bildprompts als professionelle filmische Shot-Liste. "
    "Ziel: Filmstills / Cinematic Storyboard / Trailer-Shots — keine generischen AI-Art-Bilder, kein Keyword-Spam.\n"
    "Die 10 Prompts sind ein zusammenhängender filmischer Zeitstrahl, keine 10 unabhängigen Bilder.\n\n"

    "STORYBOARD-STRUKTUR — absolut einhalten:\n"
    "Teile die 10 Prompts in vier filmische Segmente:\n\n"

    "HOOK (0–3 Sek.) → Prompt 01:\n"
    "Maximaler Scrollstop. Löst das Versprechen des Hooks visuell sofort ein. "
    "Starke Symbolik, harte Kontraste, hohe Spannung. "
    "Pflicht-Shot-Typen: Establishing Shot ODER Symbolic Shot.\n\n"

    "BODY A (3–10 Sek.) → Prompts 02–04:\n"
    "Kontext und Storyaufbau. Chronologisch: illustriert Satz 1 des Voiceovers. "
    "Eher weite, ruhigere Shots — Raum geben, Situation etablieren. "
    "Pflicht-Shot-Typen: Wide Shot, Medium Shot, Atmospheric Shot.\n\n"

    "BODY B (10–17 Sek.) → Prompts 05–08:\n"
    "Steigende Intensität. Chronologisch: illustriert Satz 2 und (falls vorhanden) Satz 3. "
    "Mehr Nähe, mehr Emotion, mehr visuelle Details. "
    "Pflicht-Shot-Typen: Close-Up, Extreme Close-Up, Macro Shot, Detail Shot, POV.\n\n"

    "OUTRO (17–20 Sek.) → Prompts 09–10:\n"
    "Emotionale Auflösung. Letzter visueller Eindruck, Signatur-Stimmung. "
    "Pflicht-Shot-Typen: Atmospheric Shot, Wide Shot ODER Symbolic Shot.\n\n"

    "CHRONOLOGISCHE PFLICHT:\n"
    "Die Bildreihenfolge folgt dem gesprochenen Voiceover — keine Rückblenden, keine Vorgriffe. "
    "BODY A zeigt ausschließlich, was in Satz 1 passiert. "
    "BODY B zeigt ausschließlich, was in Satz 2/3 passiert. "
    "VERBOTEN: Ein Bild zeigt ein Ereignis, das erst später gesprochen wird.\n\n"

    "EMOTIONALER SUBTEXT — Pflicht:\n"
    "Bilder sollen den emotionalen Subtext des Voiceovers verstärken, nicht wörtlich illustrieren. "
    "Frage für jeden Prompt: 'Was ist die EMOTION dieses Moments — und welches visuelle Motiv transportiert sie am stärksten?' "
    "Beispiel: 'Gefahr' → nicht Warnschild, sondern instabile Brücke über Abgrund. "
    "'Verlust' → nicht leerer Stuhl, sondern Schuhe vor einer geschlossenen Tür.\n\n"

    "SHOT-VARIATION — erzwungen:\n"
    "Verfügbare Typen: Wide Shot · Medium Shot · Close-Up · Extreme Close-Up · Macro Shot · Detail Shot · POV · Atmospheric Shot · Symbolic Shot. "
    "Nie mehr als 2 aufeinanderfolgende Shots desselben Typs. "
    "Nie mehr als 3 Shots desselben Typs in einem Short insgesamt.\n\n"

    "PFLICHTINHALT PRO PROMPT (fließende englische Beschreibung, kein Listenstil):\n"
    "Kameraposition und Shot-Typ · Hauptmotiv mit physischer Aktion oder Zustand · "
    "Lichtstimmung und Lichtquelle · Materialdetails und Texturen · Atmosphäre · Bildkomposition · Realismusgrad.\n\n"

    "Gut (Beispiel): 'A single bullet casing falling through the air in extreme slow motion, "
    "glowing hot with smoke trailing behind it, dark background with golden rim light, "
    "hyper-realistic metal textures, dramatic macro shot, photorealistic.'\n"
    "Verboten (Beispiel): 'soldier action cinematic' · 'gaming battle epic' · 'war scene dramatic'\n\n"

    "STIL-KONSISTENZ: Alle 10 Prompts eines Shorts teilen dieselbe visuelle Palette — "
    "gleicher Farbton, gleiche Lichtstimmung, gleicher Realismusgrad. Kein Stilwechsel.\n"
    "Themen: Gaming/Military → taktische Shooter-Ästhetik, moderne Ausrüstung, realistische Anatomie. "
    "Natur → atmosphärisch, ruhig, cinematic. Mystery → dunkel, symbolisch.\n"
    "VERBOTEN: anime, cartoon, fantasy, magic, distorted hands/faces, floating elements, "
    "mixed genres, AI-artifact glow, Keyword-Listen ohne Szenenkontext.\n"
    "Kein Präfix, keine Nummerierung in den Prompts.\n\n"

    "ENERGIE-TYP:\n"
    "Wähle für jeden Short einen Energie-Typ aus vier Optionen: phonk | action | wissen | clever.\n"
    "phonk = aggressiv, dunkel, konfrontativ. "
    "action = dringend, spannend, bewegend. "
    "wissen = ruhig, lehrreich, reflektiert. "
    "clever = überraschend, witzig, doppeldeutig.\n"
    "Füge das Feld 'energie_typ' in jedes Short-Objekt ein.\n\n"

    "BESCHREIBUNGEN:\n"
    "Erstelle für jeden Short zwei separate Beschreibungen:\n"
    "'yt_beschreibung': YouTube — informativ, 2-3 Sätze, 3-5 themenrelevante Hashtags.\n"
    "'ig_beschreibung': Instagram — emotional, kurz (1-2 Sätze), andere Hashtags als YT.\n\n"

    "Antworte NUR mit validem JSON ohne Markdown-Blöcke. "
    "Der Root-Key muss exakt 'shorts' heißen. "
    "Format:\n"
    '{{"shorts": [{{"short": "Short01", "hook_variants": ["...", "...", "...", "...", "..."], "text": "...", '
    '"titel": "...", "yt_beschreibung": "...", "ig_beschreibung": "...", '
    '"prompts": ["...", ...(exakt 10)], "energie_typ": "phonk"}}]}}\n'
)

_PROMPT_SHORTEN = (
    "Kürze diesen Voiceover-Text auf ca. {target} Zeichen. "
    "Entferne: Füllwörter, schwache Nebensätze, doppelte Aussagen, unnötige Adjektive. "
    "Behalte: natürlichen Creator-Voiceover-Fluss, Spannung, Mini-Story-Struktur. "
    "Klingt wie natürliches gesprochenes Voiceover — nicht wie komprimierter AI-Text. "
    "Antworte NUR mit dem Text, kein Kommentar.\n\nText: {text}"
)

_PROMPT_EXPAND = (
    "Erweitere diesen Voiceover-Text. "
    "PFLICHT: Das Ergebnis muss mindestens {min_chars} Zeichen lang sein (Ziel: ca. {target} Zeichen). "
    "Ergänze: ein konkretes Detail, eine kleine Spannung oder eine stärkere Aussage. "
    "Kein Fülltext. Natürlicher Creator-Voiceover-Fluss muss erhalten bleiben. "
    "Antworte NUR mit dem Text, kein Kommentar.\n\nText: {text}"
)


def _split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]


def _ensure_sentence_end(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    if text[-1] in ".!?":
        return text
    last_end = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
    if last_end > 0:
        return text[: last_end + 1]
    return text


def _refine_text(prompt: str, client: OpenAI) -> str | None:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            timeout=30,
        )
        result = response.choices[0].message.content.strip()
        if result.startswith('"') and result.endswith('"'):
            result = result[1:-1]
        return result
    except Exception as exc:
        print(f"[REFINE ERROR] GPT-Adjust fehlgeschlagen: {exc}")
        return None


def _mechanical_trim(hook: str, text: str) -> str:
    sentences = _split_sentences(text)
    while sentences:
        candidate = " ".join(sentences)
        if len(hook) + len(candidate) <= _LEN_MAX:
            return candidate
        sentences.pop()
    # Letzter Fallback: auf Wortgrenze kürzen
    target = _LEN_MAX - len(hook)
    truncated = text[:target]
    last_space = truncated.rfind(" ")
    return truncated[:last_space] if last_space > 0 else truncated


def _adjust_length(short_id: str, hook: str, text: str, client: OpenAI) -> str:
    total = len(hook) + len(text)

    if _LEN_MIN <= total <= _LEN_MAX:
        print(f"[LENGTH] {short_id}: {total} Zeichen ✓")
        return text

    text_target = _LEN_TARGET - len(hook)

    if total > _LEN_MAX:
        print(f"[TRIM] {short_id}: {total} Zeichen → kürze auf ~{_LEN_TARGET}")
        refined = _refine_text(_PROMPT_SHORTEN.format(target=text_target, text=text), client)
        if refined:
            refined = _ensure_sentence_end(refined)
            new_total = len(hook) + len(refined)
            if new_total <= _LEN_MAX:
                print(f"[TRIM] {short_id}: {total} → {new_total} Zeichen ✓")
                return refined
            print(f"[TRIM FALLBACK] {short_id}: GPT-Ergebnis {new_total} Zeichen → mechanisch kürzen")
            fallback = _mechanical_trim(hook, refined)
        else:
            print(f"[TRIM FALLBACK] {short_id}: → mechanisch kürzen")
            fallback = _mechanical_trim(hook, text)
        print(f"[TRIM FALLBACK] {short_id}: → {len(hook) + len(fallback)} Zeichen")
        return fallback

    # total < _LEN_MIN
    # Ziel relativ zu _LEN_MAX, nicht _LEN_TARGET — damit GPT-Unterlieferung (80-85%) trotzdem >= 250 ergibt
    expand_target = _LEN_MAX - len(hook) + 40
    min_chars = _LEN_MIN - len(hook)
    print(f"[EXPAND] {short_id}: {total} Zeichen → Mindest-Text: {min_chars}, Ziel: {expand_target} Zeichen")
    refined = _refine_text(_PROMPT_EXPAND.format(target=expand_target, min_chars=min_chars, text=text), client)
    if refined:
        cleaned = _ensure_sentence_end(refined)
        refined = cleaned if len(hook) + len(cleaned) >= _LEN_MIN else refined
        new_total = len(hook) + len(refined)
        if new_total >= _LEN_MIN:
            status = "✓" if new_total <= _LEN_MAX else "(außerhalb Ziel)"
            print(f"[EXPAND] {short_id}: {total} → {new_total} Zeichen {status}")
            return refined
        print(f"[EXPAND RETRY] {short_id}: {new_total} noch < {_LEN_MIN} → nochmal erweitern")
        retry = _refine_text(_PROMPT_EXPAND.format(target=expand_target, min_chars=min_chars, text=refined), client)
        if retry:
            retry_cleaned = _ensure_sentence_end(retry)
            retry = retry_cleaned if len(hook) + len(retry_cleaned) >= _LEN_MIN else retry
            new_total2 = len(hook) + len(retry)
            status = "✓" if _LEN_MIN <= new_total2 <= _LEN_MAX else "(außerhalb Ziel)"
            print(f"[EXPAND RETRY] {short_id}: {new_total} → {new_total2} Zeichen {status}")
            return retry
        print(f"[EXPAND RETRY] {short_id}: fehlgeschlagen → nehme erstes Ergebnis ({new_total} Zeichen)")
        return refined
    print(f"[EXPAND] {short_id}: GPT-Adjust fehlgeschlagen — Original behalten ({total} Zeichen)")
    return text


def _validate_df(df: pd.DataFrame, expected: int) -> list[str]:
    errors: list[str] = []
    if len(df) != expected:
        errors.append(f"Anzahl: erwartet {expected}, erhalten {len(df)}")
    for _, row in df.iterrows():
        sid = str(row.get("Short", "?"))
        for field in ("Hook", "Text", "Titel", "Beschreibung", "Prompts"):
            if not str(row.get(field, "")).strip():
                errors.append(f"{sid}: Feld '{field}' leer")
    return errors


def _fetch_batch_with_retry(
    client: OpenAI, topic: str, count: int, pattern_str: str, batch_num: int = 1
) -> pd.DataFrame:
    last_exc: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        print(f"[BATCH {batch_num}] Versuch {attempt}/{_MAX_RETRIES}: {count} Shorts angefordert")
        try:
            df = _fetch_batch(client, topic, count, pattern_str)
            errors = _validate_df(df, count)
            if errors:
                summary = "; ".join(errors[:3])
                print(f"[BATCH {batch_num}] Validierung fehlgeschlagen: {summary}")
                last_exc = ValueError(summary)
                if attempt < _MAX_RETRIES:
                    print(f"[RETRY] Batch {batch_num} — Versuch {attempt + 1} ausgelöst")
                    continue
                print(f"[BATCH {batch_num}] Alle Versuche fehlgeschlagen — nehme Teilergebnis ({len(df)} Shorts)")
                return df
            print(f"[BATCH {batch_num}] Erfolgreich: {len(df)} Shorts ✓")
            return df
        except (AuthenticationError, RateLimitError):
            raise
        except Exception as exc:
            print(f"[BATCH {batch_num}] Versuch {attempt} Fehler: {exc}")
            last_exc = exc
            if attempt == _MAX_RETRIES:
                raise
    raise last_exc  # type: ignore[misc]


def generate_table(topic: str, count: int, openai_key: str, start_date: date | None = None) -> pd.DataFrame:
    if not openai_key:
        raise ValueError("OpenAI API Key fehlt. Bitte in den Einstellungen eintragen.")
    if not topic.strip():
        raise ValueError("Bitte ein Thema eingeben.")

    client = OpenAI(api_key=openai_key)
    examples = hook_engine.get_pattern_examples(topic)
    pattern_str = "\n".join(f"• {h}" for h in examples)

    frames: list[pd.DataFrame] = []
    remaining = count
    batch_num = 0

    while remaining > 0:
        batch_size = min(_BATCH_SIZE, remaining)
        batch_num += 1
        df_batch = _fetch_batch_with_retry(client, topic, batch_size, pattern_str, batch_num)
        frames.append(df_batch)
        remaining -= batch_size  # Advance by expected size — deficit handled by repair below

    merged = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0].copy()

    if len(merged) < count:
        missing = count - len(merged)
        print(f"[REPAIR] {missing} Shorts fehlen — generiere fehlende Shorts nach")
        batch_num += 1
        repair_df = _fetch_batch_with_retry(client, topic, missing, pattern_str, batch_num)
        merged = pd.concat([merged, repair_df], ignore_index=True)
        print(f"[REPAIR] Fertig — {len(merged)}/{count} Shorts total")

    _WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    if start_date is None:
        start_date = date.today()
    for i, idx in enumerate(merged.index, start=0):
        merged.at[idx, "Short"] = f"Short{i + 1:02d}"
        d = start_date + timedelta(days=i)
        merged.at[idx, "Datum"] = d.strftime("%d.%m.")
        merged.at[idx, "Tag"] = _WOCHENTAGE[d.weekday()]

    print(f"[MERGE] Finaler Merge erfolgreich: {len(merged)} Shorts ✓")
    return merged


def _fetch_batch(client: OpenAI, topic: str, count: int, pattern_str: str) -> pd.DataFrame:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM.format(count=count, topic=topic, pattern_examples=pattern_str)},
                {"role": "user", "content": f"Erstelle {count} Shorts zum Thema: {topic}"},
            ],
            temperature=0.8,
            max_tokens=16384,
            timeout=120,
        )
    except AuthenticationError:
        raise ValueError("OpenAI API Key ist ungültig. Bitte in den Einstellungen prüfen.") from None
    except RateLimitError:
        raise ValueError("OpenAI Rate Limit erreicht. Bitte kurz warten und erneut versuchen.") from None

    raw = response.choices[0].message.content
    print(f"\n─── OpenAI Raw Response (count={count}) ───")
    print(raw[:2000])
    print("──────────────────────────\n")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"OpenAI hat kein gültiges JSON zurückgegeben.\n\nFehler: {exc}\n\nAntwort:\n{raw[:500]}"
        ) from None

    return _to_dataframe(data, count, raw, client)


def _extract_shorts_list(data: dict | list, raw: str) -> list:
    if isinstance(data, list):
        return data

    if "shorts" in data and isinstance(data["shorts"], list):
        return data["shorts"]

    for key, val in data.items():
        if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
            print(f"[WARN] 'shorts'-Key nicht gefunden. Nutze alternativen Key: '{key}'")
            return val

    for key, val in data.items():
        if isinstance(val, dict):
            try:
                return _extract_shorts_list(val, raw)
            except ValueError:
                continue

    keys = list(data.keys())
    raise ValueError(
        f"OpenAI-Antwort enthält keinen 'shorts'-Key.\n"
        f"Gefundene Keys: {keys}\n\n"
        f"Antwort (gekürzt):\n{raw[:400]}"
    )


def _to_dataframe(data: dict | list, expected: int, raw: str, client: OpenAI) -> pd.DataFrame:
    shorts = _extract_shorts_list(data, raw)

    if len(shorts) == 0:
        raise ValueError("OpenAI hat eine leere Shorts-Liste zurückgegeben.")

    if len(shorts) != expected:
        print(f"[WARN] Erwartet {expected} Shorts, erhalten {len(shorts)}. Fahre fort.")

    rows = []
    for i, s in enumerate(shorts, start=1):
        if not isinstance(s, dict):
            raise ValueError(f"Short {i}: Eintrag ist kein Objekt (erhalten: {type(s).__name__}).")

        required = ["short", "text", "titel", "prompts"]
        missing = [f for f in required if f not in s]
        has_hook = "hook" in s or ("hook_variants" in s and isinstance(s.get("hook_variants"), list))
        if not has_hook:
            missing.append("hook oder hook_variants")
        if missing:
            raise ValueError(
                f"Short {i}: Pflichtfeld(er) fehlen: {', '.join(missing)}\n"
                f"Vorhandene Keys: {list(s.keys())}"
            )

        prompts = s["prompts"]
        if not isinstance(prompts, list) or len(prompts) == 0:
            raise ValueError(f"Short {i}: 'prompts' muss eine nicht-leere Liste sein.")
        if len(prompts) != PROMPT_COUNT:
            print(f"[WARN] Short {i}: {len(prompts)} Prompts (erwartet {PROMPT_COUNT}). Nehme was vorhanden ist.")

        prompts_str = " || ".join(f"[Aspect Ratio 9:16] {p.strip()}" for p in prompts if p.strip())

        short_id = str(s["short"]).strip() or f"Short{i:02d}"
        if "hook_variants" in s and isinstance(s.get("hook_variants"), list) and s["hook_variants"]:
            hook = hook_engine.select_best_hook(
                [str(h) for h in s["hook_variants"] if h],
                hook_engine.get_recent_hooks(),
            )
        else:
            print(f"[HOOK FALLBACK] {short_id}: 'hook_variants' fehlt, nutze 'hook'")
            hook = str(s.get("hook", ""))
        hook_engine.update_session_cache(hook)

        if len(hook) > _HOOK_MAX:
            print(f"[WARN] {short_id}: Hook = {len(hook)} Zeichen (max {_HOOK_MAX})")

        text = _adjust_length(short_id, hook, str(s["text"]), client)

        # Absolute Sicherheitsgrenze — kann nicht umgangen werden
        total_final = len(hook) + len(text)
        if total_final > _LEN_MAX:
            text = _mechanical_trim(hook, text)
            print(f"[HARD CAP] {short_id}: {total_final} → {len(hook) + len(text)} Zeichen erzwungen")

        energie_typ = str(s.get("energie_typ", "")).strip().lower()
        if energie_typ not in ("phonk", "action", "wissen", "clever"):
            energie_typ = "wissen"

        rows.append({
            "Short": short_id,
            "Datum": "",
            "Tag": "",
            "Hook": hook,
            "Text": text,
            "Titel": str(s.get("titel", "")).strip(),
            "YTBeschreibung": str(s.get("yt_beschreibung", s.get("beschreibung", ""))).strip(),
            "IGBeschreibung": str(s.get("ig_beschreibung", "")).strip(),
            "Prompts": prompts_str,
            "Status": "Ausstehend",
            "EnergiTyp": energie_typ,
        })

    return pd.DataFrame(rows, columns=COLUMNS)


def make_project_dir(topic: str, base: Path | str) -> Path:
    clean = re.sub(r"[^\w\s-]", "", topic.strip())
    clean = re.sub(r"\s+", "-", clean)
    clean = re.sub(r"-{2,}", "-", clean)
    clean = clean[:40]
    date_str = date.today().strftime("%d-%m-%y")
    name = f"{clean}-{date_str}" if clean else date_str
    project_dir = Path(base) / name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir
