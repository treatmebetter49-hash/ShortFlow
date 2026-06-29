import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from openai import OpenAI, AuthenticationError, RateLimitError

from modules import hook_engine

COLUMNS = ["Short", "Datum", "Tag", "Hook", "Text", "Titel", "YTBeschreibung", "IGBeschreibung", "Prompts", "Status", "EnergiTyp"]
PROMPT_COUNT = 10
_BATCH_SIZE = 5
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
    "HOOK-FORMEL (Pflicht): Die 5 Varianten müssen diese Typen abdecken:\n"
    "- Mindestens 2x WIDERSPRUCHS-HOOK: Aussage die der Leser sofort anzweifelt. "
    "Beispiele: 'Dein Gehirn spürt keinen Schmerz.' · 'Du schläfst nie wirklich ein.' · 'Dein bester Freund lügt dich an.'\n"
    "- Mindestens 1x OPINION-HOOK: Kontroverse oder unbequeme Wahrheit. "
    "Beispiele: 'Niemand will's hören – aber [WAHRHEIT].' · 'Alle machen bei [THEMA] denselben Fehler.' · 'Du bist nicht faul – du wurdest schlecht beraten.'\n"
    "- Mindestens 1x STORY-HOOK: Persönlich, emotional, authentisch. "
    "Beispiele: 'Ein Satz hat mein Denken über [THEMA] verändert.' · 'Ich dachte, ich mache alles richtig – bis das passiert ist.' · 'Keiner redet über die Schattenseite.'\n"
    "VERBOTEN für alle 5 Varianten: philosophische Aussagen, 'X der Y'-Konstrukte, abstrakte Begriffe ohne konkreten Bezug.\n"
    "Die 5 Varianten nutzen verschiedene Einstiegswörter — nie dasselbe Startwort zweimal.\n\n"

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

    "EINZIGARTIGKEIT — ABSOLUT PFLICHT:\n"
    "Jeder Short in diesem Batch behandelt ein ANDERES psychologisches Phänomen, einen anderen Bias oder Effekt. "
    "Kein Konzept darf zweimal vorkommen — auch nicht anders formuliert oder aus einem anderen Blickwinkel. "
    "Spotlight-Effekt = Spotlight-Effekt, egal ob du schreibst 'Niemand schaut hin' oder 'Du stehst nicht im Mittelpunkt'.\n\n"

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


def _refine_text(prompt: str, client: OpenAI, model: str = "gpt-4o-mini") -> str | None:
    try:
        response = client.chat.completions.create(
            model=model,
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


def _adjust_length(short_id: str, hook: str, text: str, client: OpenAI, model: str = "gpt-4o-mini") -> str:
    total = len(hook) + len(text)

    if _LEN_MIN <= total <= _LEN_MAX:
        print(f"[LENGTH] {short_id}: {total} Zeichen ✓")
        return text

    text_target = _LEN_TARGET - len(hook)

    if total > _LEN_MAX:
        print(f"[TRIM] {short_id}: {total} Zeichen → kürze auf ~{_LEN_TARGET}")
        refined = _refine_text(_PROMPT_SHORTEN.format(target=text_target, text=text), client, model)
        if refined:
            refined = _ensure_sentence_end(refined)
            new_total = len(hook) + len(refined)
            if new_total <= _LEN_MAX:
                print(f"[TRIM] {short_id}: {total} → {new_total} Zeichen ✓")
                return refined
            print(f"[TRIM FALLBACK] {short_id}: Ergebnis {new_total} Zeichen → mechanisch kürzen")
            fallback = _mechanical_trim(hook, refined)
        else:
            print(f"[TRIM FALLBACK] {short_id}: → mechanisch kürzen")
            fallback = _mechanical_trim(hook, text)
        print(f"[TRIM FALLBACK] {short_id}: → {len(hook) + len(fallback)} Zeichen")
        return fallback

    # total < _LEN_MIN
    # Ziel relativ zu _LEN_MAX, nicht _LEN_TARGET — damit Unterlieferung (80-85%) trotzdem >= 250 ergibt
    expand_target = _LEN_MAX - len(hook) + 40
    min_chars = _LEN_MIN - len(hook)
    print(f"[EXPAND] {short_id}: {total} Zeichen → Mindest-Text: {min_chars}, Ziel: {expand_target} Zeichen")
    refined = _refine_text(_PROMPT_EXPAND.format(target=expand_target, min_chars=min_chars, text=text), client, model)
    if refined:
        cleaned = _ensure_sentence_end(refined)
        refined = cleaned if len(hook) + len(cleaned) >= _LEN_MIN else refined
        new_total = len(hook) + len(refined)
        if new_total >= _LEN_MIN:
            status = "✓" if new_total <= _LEN_MAX else "(außerhalb Ziel)"
            print(f"[EXPAND] {short_id}: {total} → {new_total} Zeichen {status}")
            return refined
        print(f"[EXPAND RETRY] {short_id}: {new_total} noch < {_LEN_MIN} → nochmal erweitern")
        retry = _refine_text(_PROMPT_EXPAND.format(target=expand_target, min_chars=min_chars, text=refined), client, model)
        if retry:
            retry_cleaned = _ensure_sentence_end(retry)
            retry = retry_cleaned if len(hook) + len(retry_cleaned) >= _LEN_MIN else retry
            new_total2 = len(hook) + len(retry)
            status = "✓" if _LEN_MIN <= new_total2 <= _LEN_MAX else "(außerhalb Ziel)"
            print(f"[EXPAND RETRY] {short_id}: {new_total} → {new_total2} Zeichen {status}")
            return retry
        print(f"[EXPAND RETRY] {short_id}: fehlgeschlagen → nehme erstes Ergebnis ({new_total} Zeichen)")
        return refined
    print(f"[EXPAND] {short_id}: Adjust fehlgeschlagen — Original behalten ({total} Zeichen)")
    return text


def _validate_df(df: pd.DataFrame, expected: int) -> list[str]:
    errors: list[str] = []
    if len(df) != expected:
        errors.append(f"Anzahl: erwartet {expected}, erhalten {len(df)}")
    for _, row in df.iterrows():
        sid = str(row.get("Short", "?"))
        for field in ("Hook", "Text", "Titel", "Prompts"):
            if not str(row.get(field, "")).strip():
                errors.append(f"{sid}: Feld '{field}' leer")
    return errors


def _generate_concepts(topic: str, count: int, client: OpenAI, model: str) -> list[str]:
    prompt = (
        f"Generiere genau {count} einzigartige psychologische Phänomene, Biases oder Effekte "
        f"für TikTok-Shorts zum Thema '{topic}'.\n"
        f"Kein Konzept darf sich mit einem anderen überschneiden. "
        f"Antworte NUR mit einem JSON-Objekt: {{\"konzepte\": [\"Name1\", \"Name2\", ...]}}"
    )
    try:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=1024,
            timeout=30,
        )
        data = json.loads(response.choices[0].message.content)
        concepts: list[str] = []
        if isinstance(data, list):
            concepts = data
        else:
            for v in data.values():
                if isinstance(v, list):
                    concepts = v
                    break
        concepts = [str(c).strip() for c in concepts if str(c).strip()]
        # Deduplizieren: case-insensitive exakte Matches entfernen
        seen: set[str] = set()
        unique: list[str] = []
        for c in concepts:
            key = c.lower()
            if key not in seen:
                seen.add(key)
                unique.append(c)
        if len(unique) < len(concepts):
            print(f"[KONZEPTE] {len(concepts) - len(unique)} Duplikate entfernt")
        concepts = unique
        print(f"[KONZEPTE] {len(concepts)} einzigartige Konzepte generiert")
        return concepts[:count]
    except Exception as exc:
        print(f"[KONZEPTE] Fehler: {exc} — fahre ohne Konzept-Vorgaben fort")
        return []


def _find_duplicate_indices(df: pd.DataFrame) -> list[int]:
    """Return indices of rows whose Titel shares a key word with an earlier row."""
    _stop = {"der", "die", "das", "ein", "eine", "des", "dem", "den", "von", "vor", "und", "oder", "im", "in", "zu"}
    seen_words: list[set[str]] = []
    dupes: list[int] = []
    for idx, row in df.iterrows():
        titel = str(row.get("Titel", "")).lower()
        words = {w for w in re.split(r'\W+', titel) if len(w) > 4 and w not in _stop}
        is_dupe = any(words & prev for prev in seen_words)
        if is_dupe:
            dupes.append(idx)
        seen_words.append(words)
    return dupes


_SYSTEM_DEDUP = (
    "Du bist ein TikTok/Reels-Voiceover-Autor. Erstelle genau 1 Short zum Thema '{topic}'.\n"
    "Antworte NUR mit validem JSON ohne Markdown-Blöcke.\n"
    "Format (exakt so): "
    "{{\"shorts\": [{{\"short\": \"Short01\", "
    "\"hook\": \"...\", "
    "\"text\": \"...\", "
    "\"titel\": \"...\", "
    "\"energie_typ\": \"wissen\"}}]}}\n\n"
    "Regeln: Hook max 70 Zeichen, direkte Aussage. "
    "Text ca. 190 Zeichen, du/dich/dein. "
    "Energie-Typ: phonk | action | wissen | clever."
)


def _regenerate_single(
    client: OpenAI, topic: str, pattern_str: str, model: str,
    used_titels: list[str], used_hooks: list[str], row: pd.Series
) -> pd.Series | None:
    used_t = "\n".join(f"- {t}" for t in used_titels[:40])
    used_h = "\n".join(f"- {h}" for h in used_hooks[:15])
    user_msg = (
        f"Erstelle 1 Short zum Thema: {topic}\n\n"
        f"Bereits verwendete Konzepte/Titel (NICHT wiederholen):\n{used_t}\n\n"
        f"Bereits verwendete Hooks (KEIN ähnliches Konzept):\n{used_h}"
    )
    _stop = {"der", "die", "das", "ein", "eine", "des", "dem", "den", "von", "vor", "und", "oder", "im", "in", "zu"}

    def _titel_conflicts(titel: str) -> bool:
        words = {w for w in re.split(r'\W+', titel.lower()) if len(w) > 4 and w not in _stop}
        for t in used_titels:
            other = {w for w in re.split(r'\W+', t.lower()) if len(w) > 4 and w not in _stop}
            if words & other:
                return True
        return False

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _SYSTEM_DEDUP.format(topic=topic)},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.9 + attempt * 0.05,
                max_tokens=2048,
                timeout=60,
            )
            data = json.loads(response.choices[0].message.content)
            shorts = data.get("shorts", [])
            if not shorts:
                continue
            s = shorts[0]
            neuer_titel = s.get("titel", "")
            if not neuer_titel:
                continue
            if _titel_conflicts(neuer_titel):
                print(f"[DEDUP] Versuch {attempt+1}: '{neuer_titel}' kollidiert noch — retry")
                continue
            hook = s.get("hook") or (s.get("hook_variants", [""])[0] if s.get("hook_variants") else "")
            new_row = row.copy()
            new_row["Hook"] = hook
            new_row["Text"] = s.get("text", row["Text"])
            new_row["Titel"] = neuer_titel
            new_row["EnergiTyp"] = s.get("energie_typ", row.get("EnergiTyp", "wissen"))
            return new_row
        except Exception as exc:
            print(f"[DEDUP] Versuch {attempt+1} fehlgeschlagen: {exc}")
    return None


def _deduplicate(
    df: pd.DataFrame, client: OpenAI, topic: str, pattern_str: str, model: str,
    existing_hooks: list[str]
) -> pd.DataFrame:
    df = df.copy()
    for runde in range(1, 4):
        dupes = _find_duplicate_indices(df)
        if not dupes:
            print(f"[DEDUP] Keine Dopplungen ✓ (nach Runde {runde - 1})")
            return df
        print(f"[DEDUP] Runde {runde}: {len(dupes)} Dopplungen — regeneriere")
        for idx in dupes:
            # Rebuild used lists from current df state after each replacement
            used_titels = df.loc[[i for i in df.index if i != idx], "Titel"].tolist()
            used_hooks_all = existing_hooks + df.loc[[i for i in df.index if i != idx], "Hook"].tolist()
            new_row = _regenerate_single(client, topic, pattern_str, model, used_titels, used_hooks_all, df.loc[idx])
            if new_row is not None:
                df.loc[idx] = new_row  # update df immediately so next iteration sees this
                print(f"[DEDUP] {new_row['Short']} → {new_row['Titel']}")
            else:
                print(f"[DEDUP] {df.loc[idx, 'Short']} konnte nicht ersetzt werden")
    print(f"[DEDUP] Max Runden erreicht — verbleibende Dopplungen akzeptiert")
    return df


def _fetch_batch_with_retry(
    client: OpenAI, topic: str, count: int, pattern_str: str, batch_num: int = 1, model: str = "gpt-4o",
    used_hooks: list[str] | None = None,
    concepts: list[str] | None = None,
) -> pd.DataFrame:
    last_exc: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        print(f"[BATCH {batch_num}] Versuch {attempt}/{_MAX_RETRIES}: {count} Shorts angefordert")
        try:
            df = _fetch_batch(client, topic, count, pattern_str, model, used_hooks, concepts)
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


_PROVIDER_CONFIG = {
    "openai": {"base_url": None,                                                          "model": "gpt-4o"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",    "model": "gemini-2.5-flash"},
}


def generate_table(
    topic: str,
    count: int,
    openai_key: str,
    start_date: date | None = None,
    provider: str = "openai",
    fallback_key: str = "",
    fallback_provider: str = "",
    start_num: int = 1,
    existing_hooks: list[str] | None = None,
) -> pd.DataFrame:
    provider = provider if provider in _PROVIDER_CONFIG else "openai"
    pconf = _PROVIDER_CONFIG[provider]
    if not openai_key:
        label = provider.capitalize()
        raise ValueError(f"{label} API Key fehlt. Bitte in den Einstellungen eintragen.")
    if not topic.strip():
        raise ValueError("Bitte ein Thema eingeben.")

    client = OpenAI(api_key=openai_key, base_url=pconf["base_url"])
    model = pconf["model"]

    fallback_client: OpenAI | None = None
    fallback_model = ""
    if fallback_key and fallback_provider and fallback_provider in _PROVIDER_CONFIG:
        fb_conf = _PROVIDER_CONFIG[fallback_provider]
        fallback_client = OpenAI(api_key=fallback_key, base_url=fb_conf["base_url"])
        fallback_model = fb_conf["model"]

    examples = hook_engine.get_pattern_examples(topic)
    pattern_str = "\n".join(f"• {h}" for h in examples)

    def _fetch_with_fallback(batch_size: int, batch_num: int, used_hooks: list[str], concepts: list[str] | None = None) -> pd.DataFrame:
        try:
            return _fetch_batch_with_retry(client, topic, batch_size, pattern_str, batch_num, model, used_hooks, concepts)
        except ValueError as exc:
            if "Rate Limit" in str(exc) and fallback_client:
                print(f"[FALLBACK] Rate Limit auf {provider} → wechsle zu {fallback_provider} (Batch {batch_num})")
                return _fetch_batch_with_retry(fallback_client, topic, batch_size, pattern_str, batch_num, fallback_model, used_hooks, concepts)
            raise

    batch_sizes: list[int] = []
    remaining = count
    while remaining > 0:
        batch_sizes.append(min(_BATCH_SIZE, remaining))
        remaining -= batch_sizes[-1]

    prior_hooks: list[str] = list(existing_hooks) if existing_hooks else []
    if prior_hooks:
        print(f"[DEDUP] {len(prior_hooks)} bestehende Hooks als Kontext übergeben")

    # Phase 1: einzigartige Konzepte generieren und auf Batches verteilen
    print(f"[KONZEPTE] Generiere {count} einzigartige Konzepte...")
    all_concepts = _generate_concepts(topic, count, client, model)
    batch_concepts: list[list[str]] = []
    offset = 0
    for size in batch_sizes:
        batch_concepts.append(all_concepts[offset:offset + size] if all_concepts else [])
        offset += size

    # Phase 2: parallele Batches, jeder mit eigenem Konzept-Slice
    frames: list[pd.DataFrame] = [pd.DataFrame()] * len(batch_sizes)
    with ThreadPoolExecutor(max_workers=len(batch_sizes)) as executor:
        future_to_idx = {
            executor.submit(_fetch_with_fallback, size, i + 1, prior_hooks, batch_concepts[i]): i
            for i, size in enumerate(batch_sizes)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            frames[idx] = future.result()

    merged = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0].copy()

    if len(merged) < count:
        missing = count - len(merged)
        print(f"[REPAIR] {missing} Shorts fehlen — generiere fehlende Shorts nach")
        repair_df = _fetch_with_fallback(missing, len(batch_sizes) + 1, prior_hooks)
        merged = pd.concat([merged, repair_df], ignore_index=True)
        print(f"[REPAIR] Fertig — {len(merged)}/{count} Shorts total")

    _WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    if start_date is None:
        start_date = date.today()
    for i, idx in enumerate(merged.index, start=0):
        merged.at[idx, "Short"] = f"Short{start_num + i:02d}"
        d = start_date + timedelta(days=i)
        merged.at[idx, "Datum"] = d.strftime("%d.%m.")
        merged.at[idx, "Tag"] = _WOCHENTAGE[d.weekday()]

    print(f"[MERGE] Finaler Merge erfolgreich: {len(merged)} Shorts ✓")
    merged = _deduplicate(merged, client, topic, pattern_str, model, prior_hooks)
    return merged


def _fetch_batch(client: OpenAI, topic: str, count: int, pattern_str: str, model: str = "gpt-4o", used_hooks: list[str] | None = None, concepts: list[str] | None = None) -> pd.DataFrame:
    user_msg = f"Erstelle {count} Shorts zum Thema: {topic}"
    if concepts:
        concepts_list = "\n".join(f"- {c}" for c in concepts)
        user_msg += f"\n\nVerpflichtend: Behandle genau diese {len(concepts)} Konzepte (je eines pro Short):\n{concepts_list}"
    if used_hooks:
        used_list = "\n".join(f"- {h}" for h in used_hooks)
        user_msg += f"\n\nBereits verwendete Hooks aus früheren Generierungen (NICHT wiederholen):\n{used_list}"
    try:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM.format(count=count, topic=topic, pattern_examples=pattern_str)},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.8,
            max_tokens=16384,
            timeout=90,
        )
    except AuthenticationError:
        raise ValueError("API Key ist ungültig. Bitte in den Einstellungen prüfen.") from None
    except RateLimitError:
        raise ValueError("Rate Limit erreicht. Bitte kurz warten und erneut versuchen.") from None

    raw = response.choices[0].message.content
    print(f"\n─── LLM Raw Response (count={count}, model={model}) ───")
    print(raw[:2000])
    print("──────────────────────────\n")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Kein gültiges JSON erhalten.\n\nFehler: {exc}\n\nAntwort:\n{raw[:500]}"
        ) from None

    return _to_dataframe(data, count, raw, client, model)


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


def _to_dataframe(data: dict | list, expected: int, raw: str, client: OpenAI, model: str = "gpt-4o-mini") -> pd.DataFrame:
    shorts = _extract_shorts_list(data, raw)

    if len(shorts) == 0:
        raise ValueError("Die KI hat eine leere Shorts-Liste zurückgegeben.")

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

        text = _adjust_length(short_id, hook, str(s["text"]), client, model)

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


_MONTHS_DE = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def make_project_dir(topic: str, base: Path | str, month: int | None = None, year: int | None = None) -> Path:
    today = date.today()
    month = month or today.month
    year = year or today.year
    safe_topic = re.sub(r'[<>:"/\\|?*]', '', topic).strip() or "Shorts"
    month_name = f"{month:02d}.{_MONTHS_DE[month - 1]}'{year % 100:02d}"

    base_path = Path(base)
    # Suche nach bestehendem Ordner der mit dem Topic-Namen beginnt (z.B. Psychologie'26)
    existing = None
    if base_path.is_dir():
        for d in base_path.iterdir():
            if d.is_dir() and d.name.startswith(safe_topic):
                existing = d
                break

    topic_dir = existing if existing else base_path / safe_topic
    project_dir = topic_dir / month_name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir
