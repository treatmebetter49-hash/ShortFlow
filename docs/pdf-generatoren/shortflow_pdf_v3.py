from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

W, H = A4
IMG = "/Users/mathiaskunze/Downloads/ShortFlow/Bilder/"

BG        = HexColor("#0b0b10")
SURFACE   = HexColor("#111118")
ROW_ALT   = HexColor("#16161f")
BORDER    = HexColor("#252535")
GREEN     = HexColor("#9b59b6")
GREEN_DIM = HexColor("#6a3d85")
WHITE     = HexColor("#e2e2e2")
GRAY      = HexColor("#999999")
GRAY_DIM  = HexColor("#555555")
GRAY_LITE = HexColor("#cccccc")

# Badge colors exact from HTML table CSS
BADGE = {
    "Action":      (HexColor("#1c1010"), HexColor("#f87171")),
    "Phonk":       (HexColor("#1a1028"), HexColor("#c084fc")),
    "Wissen":      (HexColor("#0d1f14"), HexColor("#4ade80")),
    "Clever":      (HexColor("#1a180d"), HexColor("#fbbf24")),
    "Ausstehend":  (HexColor("#16161f"), HexColor("#555555")),
    "Fertig":      (HexColor("#0d2a1a"), HexColor("#2ecc71")),
}

TOTAL = 9


def bg(c):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def header_bar(c, section_tag, title_white, title_green=None):
    """Top section header like the ShortFlow UI"""
    # Top green line
    c.setStrokeColor(GREEN)
    c.setLineWidth(1.5)
    c.line(0, H - 14*mm, W, H - 14*mm)

    # Logo left
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(GREEN)
    c.drawString(20*mm, H - 10*mm, "ShortFlow")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(49*mm, H - 10*mm, "·  " + section_tag)

    # Page section line
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(0, H - 28*mm, W, H - 28*mm)

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 43*mm, title_white)
    if title_green:
        tw = c.stringWidth(title_white, "Helvetica-Bold", 24)
        c.setFillColor(GREEN)
        c.drawString(20*mm + tw + 4*mm, H - 43*mm, title_green)


def badge(c, x, y, text, w=22*mm, h=5.5*mm):
    bg_col, txt_col = BADGE.get(text, BADGE["Ausstehend"])
    c.setFillColor(bg_col)
    c.roundRect(x, y, w, h, 1.5*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(txt_col)
    c.drawCentredString(x + w/2, y + 1.8*mm, text.upper())


def row_line(c, y):
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.4)
    c.line(20*mm, y, W - 20*mm, y)


def stat_card(c, x, y, w, value, label):
    c.setFillColor(SURFACE)
    c.roundRect(x, y, w, 16*mm, 2*mm, fill=1, stroke=0)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, 16*mm, 2*mm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(GREEN)
    c.drawCentredString(x + w/2, y + 8.5*mm, value)
    c.setFont("Helvetica", 7)
    c.setFillColor(GRAY)
    c.drawCentredString(x + w/2, y + 3*mm, label.upper())


def img_simple(c, fname, x, y, w, h):
    try:
        ir = ImageReader(IMG + fname)
        iw, ih = ir.getSize()
        ratio = iw / ih
        if w / h > ratio:
            fw = h * ratio; fh = h
            fx = x + (w - fw) / 2; fy = y
        else:
            fw = w; fh = w / ratio
            fx = x; fy = y + (h - fh) / 2
        c.drawImage(ir, fx, fy, fw, fh)
    except:
        c.setFillColor(SURFACE)
        c.roundRect(x, y, w, h, 2*mm, fill=1, stroke=0)
        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY)
        c.drawCentredString(x + w/2, y + h/2, fname)


def pnum(c, n):
    c.setFont("Helvetica", 7)
    c.setFillColor(GRAY_DIM)
    c.drawRightString(W - 20*mm, 10*mm, f"{n:02d} / {TOTAL:02d}")
    c.setFillColor(GREEN_DIM)
    c.drawString(20*mm, 10*mm, "ShortFlow")


# ── 1. COVER ────────────────────────────────────────────────────────────
def page_cover(c):
    bg(c)

    # Top bar like the HTML table
    c.setFillColor(SURFACE)
    c.rect(0, H - 14*mm, W, 14*mm, fill=1, stroke=0)
    c.setStrokeColor(GREEN)
    c.setLineWidth(1.5)
    c.line(0, H - 14*mm, W, H - 14*mm)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(GREEN)
    c.drawString(20*mm, H - 9.5*mm, "ShortFlow")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(49*mm, H - 9.5*mm, "·  Dokumentation · 2026")

    # Big title
    c.setFont("Helvetica-Bold", 64)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 80*mm, "Short")
    c.setFillColor(GREEN)
    c.drawString(20*mm, H - 110*mm, "Flow.")

    c.setFont("Helvetica", 12)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 124*mm, "Von der Idee zum Short.")

    # Divider row like table separator
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(20*mm, H - 132*mm, W - 20*mm, H - 132*mm)

    # Stat cards
    cards = [("154+", "Shorts"), ("6", "Monate"), ("4", "Musiktitel"), ("1", "App")]
    cw = (W - 44*mm) / 4
    for i, (val, lbl) in enumerate(cards):
        stat_card(c, 20*mm + i * (cw + 1.3*mm), H - 160*mm, cw, val, lbl)

    # Preview strip
    strip_y = 55*mm
    strip_w = (W - 44*mm) / 3
    for i, fname in enumerate(["Bild03.png", "Bild02.png", "Bild07.png"]):
        x = 20*mm + i * (strip_w + 4*mm)
        c.setFillColor(SURFACE)
        c.roundRect(x, strip_y, strip_w, 40*mm, 2*mm, fill=1, stroke=0)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.roundRect(x, strip_y, strip_w, 40*mm, 2*mm, fill=0, stroke=1)
        img_simple(c, fname, x + 1*mm, strip_y + 1*mm, strip_w - 2*mm, 38*mm)

    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRAY_DIM)
    c.drawString(20*mm, 12*mm, "Mathias Kunze · WTF_Wissen_Official · 2026")
    c.showPage()


# ── 2. GESCHICHTE ───────────────────────────────────────────────────────
def page_story(c):
    bg(c)
    header_bar(c, "Die Geschichte", "Wie ShortFlow", "entstand.")

    # Table-style rows for story paragraphs
    paras = [
        ("Start", "Action",
         "Idee: ein bisschen Taschengeld verdienen. Faceless YouTube Kanal, Psychologie-Content, KI-Stimme."),
        ("Problem", "Phonk",
         "Die Fleißarbeit. Jeden Prompt einzeln in Adobe Firefly, Ordner erstellen, Bilder umbenennen. 30 Min pro Short."),
        ("Script", "Wissen",
         "\"SchnelleBilder\" — Python-Script liest Prompts, schickt sie zu fal.ai, lädt Bilder runter, benennt um, legt ab."),
        ("Ergebnis", "Fertig",
         "Was vorher 30 Min pro Short war: 10 Minuten für den ganzen Monat. Zeit gewonnen."),
        ("Problem 2", "Phonk",
         "ChatGPT wurde unzuverlässiger. Vergaß die Tabellenstruktur. Texte zu lang oder zu kurz. Stundenlange Diskussionen."),
        ("Lösung", "Action",
         "Mit Claude Code eine eigene App bauen. Tage, Wochen, Monate. Der Name musste her: ShortFlow."),
        ("Zwischenstand", "Wissen",
         "Wollte die App verkaufen. KI-Analyse sagte klar: wird nicht klappen. Das tat weh."),
        ("Heute", "Fertig",
         "Egal. Die App läuft. Short154 ist fertig. Zum Aufgeben ist es zu spät."),
    ]

    # Table header
    y = H - 58*mm
    c.setFillColor(SURFACE)
    c.rect(20*mm, y - 1*mm, W - 40*mm, 7*mm, fill=1, stroke=0)
    row_line(c, y + 6*mm)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(GRAY)
    for label, xoff in [("Phase", 0), ("Typ", 38*mm), ("Was passierte", 64*mm)]:
        c.drawString(20*mm + xoff, y + 1.5*mm, label.upper())

    row_line(c, y - 1*mm)

    for i, (phase, typ, text) in enumerate(paras):
        y -= 11*mm
        if i % 2 == 0:
            c.setFillColor(ROW_ALT)
            c.rect(20*mm, y - 2*mm, W - 40*mm, 10*mm, fill=1, stroke=0)

        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(WHITE)
        c.drawString(21*mm, y + 2*mm, phase)

        badge(c, 20*mm + 38*mm, y + 0.5*mm, typ, 22*mm, 5.5*mm)

        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY_LITE)
        # truncate if too long
        max_w = W - 40*mm - 64*mm - 4*mm
        while c.stringWidth(text, "Helvetica", 8) > max_w and len(text) > 10:
            text = text[:-4] + "..."
        c.drawString(20*mm + 64*mm, y + 2*mm, text)
        row_line(c, y - 2*mm)

    pnum(c, 2)
    c.showPage()


# ── 3. BRAIN TAB ────────────────────────────────────────────────────────
def page_brain(c):
    bg(c)
    header_bar(c, "Schritt 01 · Brain", "Thema rein,", "Tabelle raus.")

    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 53*mm, "Thema eingeben, Anzahl wählen — ShortFlow generiert Hooks, Texte, Bildprompts, Titel und Beschreibungen.")

    # Screenshot
    img_simple(c, "Bild03.png", 20*mm, H - 175*mm, W - 40*mm, 112*mm)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.roundRect(20*mm, H - 175*mm, W - 40*mm, 112*mm, 2*mm, fill=0, stroke=1)

    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRAY_DIM)
    c.drawCentredString(W/2, H - 181*mm, "Brain-Tab — Thema \"Biologie\", 2 Shorts generiert, Nächster: Short179")

    # Feature rows
    feats = [
        ("Einzeln", "Wissen", "Wenige Shorts auf Abruf generieren"),
        ("Monat", "Action", "Ganzen Monat auf einmal — mit Datum, Wochentag, Musik"),
        ("Weiterzählen", "Fertig", "Erkennt vorhandene Shorts und zählt korrekt weiter"),
    ]
    y = H - 197*mm
    row_line(c, y + 6*mm)
    for i, (name, typ, desc) in enumerate(feats):
        if i % 2 == 0:
            c.setFillColor(ROW_ALT)
            c.rect(20*mm, y - 2*mm, W - 40*mm, 9*mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(WHITE)
        c.drawString(22*mm, y + 1.5*mm, name)
        badge(c, 20*mm + 38*mm, y + 0.2*mm, typ, 22*mm, 5.5*mm)
        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY_LITE)
        c.drawString(20*mm + 64*mm, y + 1.5*mm, desc)
        row_line(c, y - 2*mm)
        y -= 10*mm

    pnum(c, 3)
    c.showPage()


# ── 4. TABELLE VORHER / NACHHER ─────────────────────────────────────────
def page_tabelle(c):
    bg(c)
    header_bar(c, "Das Herzstück", "Vorher.", "Nachher.")

    half = (W - 44*mm) / 2

    # VORHER label
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 55*mm, "VORHER")
    badge(c, 46*mm, H - 57*mm, "Ausstehend", 30*mm, 5.5*mm)
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(79*mm, H - 54.5*mm, "Numbers — alles manuell")

    # NACHHER label
    x2 = 20*mm + half + 4*mm
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GREEN)
    c.drawString(x2, H - 55*mm, "NACHHER")
    badge(c, x2 + 28*mm, H - 57*mm, "Fertig", 20*mm, 5.5*mm)
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(x2 + 51*mm, H - 54.5*mm, "ShortFlow HTML")

    # Screenshots
    img_simple(c, "Bild01.png", 20*mm, H - 170*mm, half, 107*mm)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.rect(20*mm, H - 170*mm, half, 107*mm, stroke=1, fill=0)

    img_simple(c, "Bild02.png", x2, H - 170*mm, half, 107*mm)
    c.setStrokeColor(GREEN_DIM)
    c.setLineWidth(0.5)
    c.rect(x2, H - 170*mm, half, 107*mm, stroke=1, fill=0)

    # Stat row
    row_line(c, H - 178*mm)
    stats = [("30 Min / Short", "Ausstehend", "manuell"), ("10 Min / Monat", "Fertig", "automatisch")]
    sw = (W - 44*mm) / 2
    for i, (val, typ, sub) in enumerate(stats):
        xi = 20*mm + i * (sw + 4*mm)
        c.setFillColor(SURFACE)
        c.roundRect(xi, H - 199*mm, sw, 17*mm, 2*mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(GREEN if i == 1 else GRAY)
        c.drawString(xi + 4*mm, H - 190*mm, val)
        badge(c, xi + 4*mm, H - 197*mm, typ, 28*mm, 5.5*mm)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(GRAY)
        c.drawString(xi + 35*mm, H - 195.5*mm, sub)

    # Info rows
    row_line(c, H - 202*mm)
    infos = [
        "Kopier-Button 1x klicken → leicht transparent (teilweise fertig)",
        "Alle Felder kopiert → Zeile dunkel (Short komplett abgehakt)",
        "Zwei Versionen: Desktop-HTML für den iMac + iPhone-HTML für Instagram",
    ]
    y = H - 211*mm
    for i, info in enumerate(infos):
        if i % 2 == 0:
            c.setFillColor(ROW_ALT)
            c.rect(20*mm, y - 2*mm, W - 40*mm, 7*mm, fill=1, stroke=0)
        c.setFillColor(GREEN)
        c.circle(23*mm, y + 2*mm, 1*mm, fill=1, stroke=0)
        c.setFont("Helvetica", 8.5)
        c.setFillColor(GRAY_LITE)
        c.drawString(26*mm, y + 0.5*mm, info)
        row_line(c, y - 2*mm)
        y -= 8.5*mm

    pnum(c, 4)
    c.showPage()


# ── 5. MACHINE TAB ──────────────────────────────────────────────────────
def page_machine(c):
    bg(c)
    header_bar(c, "Schritt 02 · Machine", "Medien-Paket", "schnüren.")

    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 53*mm, "CSV laden → Button klicken → ShortFlow generiert alle Bilder und legt sie automatisch ab.")

    img_simple(c, "Bild04.png", 20*mm, H - 185*mm, W - 40*mm, 122*mm)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.roundRect(20*mm, H - 185*mm, W - 40*mm, 122*mm, 2*mm, fill=0, stroke=1)

    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRAY_DIM)
    c.drawCentredString(W/2, H - 191*mm, "Machine-Tab — Bildgenerierung läuft, Log zeigt Echtzeit-Fortschritt")

    # Flow steps as badge row
    row_line(c, H - 200*mm)
    steps = [("CSV laden", "Wissen"), ("fal.ai", "Action"), ("Umbenennen", "Phonk"), ("Ablegen", "Fertig")]
    sw = (W - 40*mm) / 4
    y_s = H - 215*mm
    for i, (step, typ) in enumerate(steps):
        xi = 20*mm + i * sw
        c.setFillColor(SURFACE)
        c.roundRect(xi, y_s, sw - 2*mm, 12*mm, 2*mm, fill=1, stroke=0)
        badge(c, xi + 1*mm, y_s + 6*mm, typ, sw - 4*mm, 5*mm)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(WHITE)
        c.drawCentredString(xi + (sw - 2*mm)/2, y_s + 1.5*mm, step)
        if i < len(steps) - 1:
            c.setFillColor(GREEN_DIM)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(xi + sw - 2.5*mm, y_s + 3*mm, "›")

    row_line(c, y_s - 1*mm)
    c.setFillColor(SURFACE)
    c.roundRect(20*mm, y_s - 20*mm, W - 40*mm, 17*mm, 2*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(GREEN)
    c.drawString(26*mm, y_s - 8.5*mm, "10 Bilder pro Short")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRAY)
    c.drawString(26*mm, y_s - 15*mm, "Automatisch generiert, umbenannt und in den richtigen Short-Ordner abgelegt")

    pnum(c, 5)
    c.showPage()


# ── 6. SETTINGS ─────────────────────────────────────────────────────────
def page_settings(c):
    bg(c)
    header_bar(c, "Einmalig einrichten", "Settings.")

    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 53*mm, "Einmalig API-Keys eintragen — danach läuft alles auf Knopfdruck.")

    img_simple(c, "Bild05.png", 20*mm, H - 190*mm, W - 40*mm, 127*mm)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.roundRect(20*mm, H - 190*mm, W - 40*mm, 127*mm, 2*mm, fill=0, stroke=1)

    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRAY_DIM)
    c.drawCentredString(W/2, H - 196*mm, "Settings-Tab — alle Keys eingetragen, Musik-Zuordnung aktiv")

    # Keys as badge rows
    keys = [
        ("OpenAI / Gemini API-Key", "Wissen"),
        ("fal.ai Bildgenerator-Key", "Action"),
        ("Netlify Token + Site-ID", "Phonk"),
        ("Telegram Bot-Token + Chat-ID", "Clever"),
        ("Output-Ordner", "Fertig"),
    ]
    row_line(c, H - 203*mm)
    y = H - 212*mm
    for i, (key, typ) in enumerate(keys):
        if i % 2 == 0:
            c.setFillColor(ROW_ALT)
            c.rect(20*mm, y - 2*mm, W - 40*mm, 7.5*mm, fill=1, stroke=0)
        badge(c, 21*mm, y, typ, 26*mm, 5.5*mm)
        c.setFont("Helvetica", 8.5)
        c.setFillColor(GRAY_LITE)
        c.drawString(50*mm, y + 1*mm, key)
        row_line(c, y - 2*mm)
        y -= 9*mm

    pnum(c, 6)
    c.showPage()


# ── 7. IPHONE EXPORT ────────────────────────────────────────────────────
def page_iphone(c):
    bg(c)
    header_bar(c, "Schritt 03 · iPhone Export", "Direkt aufs", "iPhone.")

    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 53*mm, "\"iPhone IG Export\" klicken → Netlify → Telegram DM → Safari öffnen → 1-Tap kopieren.")

    half = (W - 44*mm) / 2

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 62*mm, "TELEGRAM BOT")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GREEN)
    c.drawString(20*mm + half + 4*mm, H - 62*mm, "IPHONE SAFARI")

    img_simple(c, "Bild06.png", 20*mm, H - 175*mm, half, 105*mm)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.rect(20*mm, H - 175*mm, half, 105*mm, stroke=1, fill=0)

    x2 = 20*mm + half + 4*mm
    img_simple(c, "Bild07.png", x2, H - 175*mm, half, 105*mm)
    c.setStrokeColor(GREEN_DIM)
    c.setLineWidth(0.5)
    c.rect(x2, H - 175*mm, half, 105*mm, stroke=1, fill=0)

    # Flow as badge row
    row_line(c, H - 183*mm)
    steps = [("Export klicken", "Action"), ("→ Netlify", "Wissen"), ("→ Telegram", "Phonk"), ("→ 1-Tap", "Fertig")]
    sw = (W - 40*mm) / 4
    y_s = H - 198*mm
    for i, (step, typ) in enumerate(steps):
        xi = 20*mm + i * sw
        c.setFillColor(SURFACE)
        c.roundRect(xi, y_s, sw - 2*mm, 12*mm, 2*mm, fill=1, stroke=0)
        badge(c, xi + 1*mm, y_s + 6*mm, typ, sw - 4*mm, 5*mm)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(WHITE)
        c.drawCentredString(xi + (sw - 2*mm)/2, y_s + 1.5*mm, step)

    row_line(c, y_s - 1*mm)
    c.setFillColor(SURFACE)
    c.roundRect(20*mm, y_s - 20*mm, W - 40*mm, 17*mm, 2*mm, fill=1, stroke=0)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRAY)
    c.drawString(26*mm, y_s - 10*mm, "Netlify Site-ID ist fest hinterlegt — jeder Export überschreibt die gleiche Seite.")
    c.drawString(26*mm, y_s - 16.5*mm, "Der Telegram-Bot schickt den Link automatisch per DM.")

    pnum(c, 7)
    c.showPage()


# ── 8. ORDNERSTRUKTUR ───────────────────────────────────────────────────
def page_folder(c):
    bg(c)
    header_bar(c, "Ausgabe · Dateisystem", "Alles an", "seinem Platz.")

    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 53*mm, "ShortFlow legt die gesamte Ordnerstruktur automatisch an — sortiert nach Thema und Monat.")

    half_w = (W - 44*mm) / 2
    half_h = 68*mm
    grid = [
        ("Bild08.png", "Shorts/  —  Themen-Ebene", "Wissen"),
        ("Bild09.png", "Biologie/  —  Monats-Ebene", "Action"),
        ("Bild10.png", "06.Juni'26  —  Shorts + HTML-Tabellen", "Phonk"),
        ("Bild11.png", "Short178  —  10 Bilder + prompts.txt", "Fertig"),
    ]
    row_line(c, H - 60*mm)
    for i, (fname, label, typ) in enumerate(grid):
        col = i % 2
        row = i // 2
        xi = 20*mm + col * (half_w + 4*mm)
        yi = H - 68*mm - row * (half_h + 14*mm)

        img_simple(c, fname, xi, yi, half_w, half_h)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.rect(xi, yi, half_w, half_h, stroke=1, fill=0)

        badge(c, xi, yi - 7*mm, typ, 22*mm, 5.5*mm)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(GRAY)
        c.drawString(xi + 24*mm, yi - 5.5*mm, label)

    pnum(c, 8)
    c.showPage()


# ── 9. ABSCHLUSS ────────────────────────────────────────────────────────
def page_end(c):
    bg(c)

    c.setFillColor(SURFACE)
    c.rect(0, H - 14*mm, W, 14*mm, fill=1, stroke=0)
    c.setStrokeColor(GREEN)
    c.setLineWidth(1.5)
    c.line(0, H - 14*mm, W, H - 14*mm)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(GREEN)
    c.drawString(20*mm, H - 9.5*mm, "ShortFlow")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(49*mm, H - 9.5*mm, "·  Stand Juni 2026")

    c.setFont("Helvetica-Bold", 48)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 70*mm, "Short154")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(GREEN)
    c.drawString(20*mm, H - 83*mm, "ist fertig.")

    row_line(c, H - 92*mm)

    # Stats row
    cards = [("154+", "Shorts"), ("6", "Monate"), ("4", "Musiktitel"), ("1", "App")]
    cw = (W - 44*mm) / 4
    for i, (val, lbl) in enumerate(cards):
        stat_card(c, 20*mm + i * (cw + 1.3*mm), H - 122*mm, cw, val, lbl)

    row_line(c, H - 126*mm)

    # Quote as highlighted row
    c.setFillColor(SURFACE)
    c.roundRect(20*mm, H - 158*mm, W - 40*mm, 26*mm, 2*mm, fill=1, stroke=0)
    c.setStrokeColor(GREEN)
    c.setLineWidth(2)
    c.line(20*mm, H - 158*mm, 20*mm, H - 132*mm)
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(WHITE)
    c.drawString(26*mm, H - 142*mm, "\"Es gibt Automatisierungen, die das alles können und sogar selbst posten.")
    c.drawString(26*mm, H - 149*mm, "Ich will die Kontrolle behalten. Ich schneide jeden Clip selbst.\"")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(26*mm, H - 156*mm, "Mathias Kunze · WTF_Wissen_Official")

    row_line(c, H - 162*mm)

    # Final badge status row
    items = [
        ("Brain", "Fertig"), ("Machine", "Fertig"), ("HTML Export", "Fertig"),
        ("iPhone Export", "Fertig"), ("Telegram Bot", "Fertig"),
    ]
    y = H - 180*mm
    for i, (name, typ) in enumerate(items):
        if i % 2 == 0:
            c.setFillColor(ROW_ALT)
            c.rect(20*mm, y - 2*mm, W - 40*mm, 8*mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(WHITE)
        c.drawString(22*mm, y + 1.5*mm, name)
        badge(c, W - 48*mm, y, typ, 26*mm, 5.5*mm)
        row_line(c, y - 2*mm)
        y -= 10*mm

    pnum(c, 9)
    c.showPage()


# ── BUILD ────────────────────────────────────────────────────────────────
out = "/Users/mathiaskunze/Downloads/ShortFlow-Dokumentation.pdf"
c = canvas.Canvas(out, pagesize=A4)
c.setTitle("ShortFlow — Dokumentation")
c.setAuthor("Mathias Kunze")

page_cover(c)
page_story(c)
page_brain(c)
page_tabelle(c)
page_machine(c)
page_settings(c)
page_iphone(c)
page_folder(c)
page_end(c)

c.save()
print(f"Gespeichert: {out}")
