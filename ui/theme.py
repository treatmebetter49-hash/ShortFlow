"""Shared visual theme for the ShortFlow desktop app.

Single source of truth for the gold/black accent palette. Previously this
purple accent (#9b30ff / #7a20dd) was duplicated independently in app.py,
brain_tab.py, machine_tab.py and gradient_bar.py — this module replaces
all of those copies so the palette can't drift again.

Fertig/Status-Grün lebt bewusst NICHT hier: das ist Statusfarbe, keine
Akzentfarbe, und bleibt lokal dort, wo Status gerendert wird.
"""

# Base surfaces (dark app, single theme by design — see ui/app.py)
BG = "#0b0b10"
SURFACE = "#111118"
BORDER_DIM = "#2a2a3a"

# Gold — the one accent
GOLD = "#cfa347"
GOLD_HOVER = "#b78f3a"
GOLD_DARK = "#8f6a28"
GOLD_HI = "#f2d78f"        # highlight tone: wordmark, progress-bar sheen
INK_ON_GOLD = "#1c1408"    # dark text for solid-gold surfaces

# Silver — quiet secondary metal, never competes with gold
SILVER = "#9a9aa4"
SILVER_HOVER = "#84848f"

# CTkButton "glass" look: dark warm-black fill, gold border, gold text.
# Used via **theme.GLASS on every secondary button across the app.
GLASS = dict(
    fg_color="#181410",
    hover_color="#241d15",
    border_color=GOLD,
    border_width=1,
    corner_radius=10,
    text_color=GOLD_HI,
)
