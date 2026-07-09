import difflib
import json
import random
import re
from pathlib import Path

_PATTERNS_FILE = Path(__file__).parent.parent / "hook_patterns.json"

_recent_hooks: list[str] = []
_MAX_CACHE = 20

_TOPIC_TYPE_KEYWORDS: dict[str, list[str]] = {
    "gaming": [
        "game", "gaming", "gamer", "spieler", "cs", "valorant", "fortnite",
        "lol", "league", "streamer", "esport", "twitch", "minecraft", "cod",
        "counter-strike", "overwatch", "dota", "pubg",
    ],
    "sport": [
        "fußball", "tennis", "basketball", "sport", "athlet", "weltmeister",
        "nfl", "nba", "boxer", "schwimmer", "leichtathletik", "olympia",
        "bundesliga", "champions league", "formel 1", "golf",
    ],
    "nature": [
        "tier", "tiere", "natur", "wald", "ozean", "pflanze", "meer",
        "berge", "wildlife", "fauna", "flora", "dschungel", "hai",
        "wolf", "bär", "adler", "schlange", "insekt",
    ],
    "psychology": [
        "psychologie", "psychologisch", "effekt", "gehirn", "verhalten",
        "bias", "unterbewusst", "unterbewusstsein", "wahrnehmung",
        "manipulation", "manipulieren", "denkfehler", "kognitiv",
        "emotion", "trigger", "glaube", "überzeugung", "gewohnheit",
        "gedächtnis", "angst", "sucht",
    ],
}

_TOPIC_CATEGORY_MAP: dict[str, list[str]] = {
    "gaming": ["story", "fact", "opinion", "warning", "list"],
    "sport":  ["story", "fact", "list", "opinion", "warning"],
    "nature": ["fact", "mystery", "story", "warning"],
    "psychology": ["psychology"],
    "general": ["story", "fact", "warning", "mystery", "opinion", "howto", "list"],
}

_FORBIDDEN_RE: list[re.Pattern] = [
    re.compile(r"[Ww]as wäre"),
    re.compile(r"[Ss]tell dir vor"),
    re.compile(r"[Hh]ast du.*vorgestellt"),
    re.compile(r"[Ww]ie würde es"),
    re.compile(r"\?$"),
    re.compile(r"[Ii]n der Welt des?\b"),
    re.compile(r"[Mm]anchmal gibt es"),
    re.compile(r"[Ee]rstaunliche[rs]?\s+\w+"),
]

_FILLER_SIGNALS = [
    "gilt als",
    "ist bekannt für",
    "Ein Blick in",
    "macht.*zu einem",
    "macht.*zu einer",
]

_WEAK_OPENERS = {"ist", "sind", "war", "waren", "hat", "haben", "wird", "werden", "es"}


def _load_patterns() -> dict:
    if not _PATTERNS_FILE.exists():
        return {"categories": {}}
    with _PATTERNS_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def _detect_topic_type(topic: str) -> str:
    topic_lower = topic.lower()
    for topic_type, keywords in _TOPIC_TYPE_KEYWORDS.items():
        if any(k in topic_lower for k in keywords):
            return topic_type
    return "general"


def get_pattern_examples(topic: str, n: int = 5) -> list[str]:
    topic_type = _detect_topic_type(topic)
    categories = _TOPIC_CATEGORY_MAP.get(topic_type, _TOPIC_CATEGORY_MAP["general"])

    patterns = _load_patterns()
    cat_data = patterns.get("categories", {})

    candidates: list[dict] = []
    # Pull from each relevant category, prioritising high-energy hooks
    for cat in categories:
        for hook in cat_data.get(cat, []):
            if hook.get("energy") in ("extrem", "hoch"):
                candidates.append(hook)

    if not candidates:
        for cat in categories:
            candidates.extend(cat_data.get(cat, []))

    random.shuffle(candidates)
    return [h["text"] for h in candidates[:n]]


def score_hook(hook: str, recent_hooks: list[str]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    hook = hook.strip()

    # 1. Length
    length = len(hook)
    if length <= 70:
        score += 20
    else:
        reasons.append(f"zu lang ({length} Zeichen)")

    # 2. Opener quality
    words = hook.split()
    first = words[0].lower() if words else ""
    if first in _WEAK_OPENERS:
        score -= 10
        reasons.append(f"schwacher Einstieg '{words[0]}'")
    else:
        score += 15

    # 3. Forbidden patterns
    forbidden_hit = any(p.search(hook) for p in _FORBIDDEN_RE)
    if forbidden_hit:
        score -= 20
        reasons.append("verbotenes Muster")
    else:
        score += 20

    # 4. Filler signals
    filler_hit = any(re.search(sig, hook, re.IGNORECASE) for sig in _FILLER_SIGNALS)
    if filler_hit:
        score -= 5
        reasons.append("Filler-Signal")
    else:
        score += 15

    # 5. Doku / Wikipedia style
    doku_signals = ["gilt als", "ist bekannt für", "In der Welt", "manchmal gibt es"]
    if any(s.lower() in hook.lower() for s in doku_signals):
        score -= 10
        reasons.append("Doku-Stil")
    else:
        score += 10

    # 6. Variety vs session cache
    if recent_hooks:
        max_sim = max(
            difflib.SequenceMatcher(None, hook.lower(), r.lower()).ratio()
            for r in recent_hooks
        )
        if max_sim < 0.35:
            score += 20
        elif max_sim < 0.55:
            score += 5
            reasons.append(f"leicht ähnlich zu vorherigem Hook ({max_sim:.0%})")
        else:
            score -= 30
            reasons.append(f"zu ähnlich zu vorherigem Hook ({max_sim:.0%})")
    else:
        score += 20

    return max(0.0, score), reasons


def select_best_hook(variants: list[str], recent_hooks: list[str]) -> str:
    if not variants:
        raise ValueError("Keine Hook-Varianten übergeben.")

    scored: list[tuple[float, str, list[str]]] = []
    for hook in variants:
        s, reasons = score_hook(hook, recent_hooks)
        scored.append((s, hook.strip(), reasons))
        tag = "✓" if s >= 60 else "✗"
        print(f"[HOOK {tag}] Score {s:>4.0f}  '{hook.strip()}'")
        if reasons:
            print(f"            → {', '.join(reasons)}")

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_hook, _ = scored[0]

    if best_score < 60:
        print(f"[HOOK WARN] Kein Hook über Score 60. Bester Score: {best_score:.0f} — trotzdem verwendet.")
    else:
        print(f"[HOOK SELECT] '{best_hook}'  (Score {best_score:.0f})")

    return best_hook


def get_recent_hooks() -> list[str]:
    return list(_recent_hooks)


def update_session_cache(hook: str) -> None:
    _recent_hooks.append(hook)
    if len(_recent_hooks) > _MAX_CACHE:
        _recent_hooks.pop(0)
