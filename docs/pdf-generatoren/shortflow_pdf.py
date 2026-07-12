from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

W, H = A4

BLACK     = HexColor("#0D0D0D")
DARK      = HexColor("#141414")
CARD      = HexColor("#1C1C1E")
PURPLE    = HexColor("#7F77DD")
PURPLE_DIM = HexColor("#534AB7")
WHITE     = HexColor("#FFFFFF")
GRAY      = HexColor("#888888")
GRAY_DIM  = HexColor("#444444")
OFF_WHITE = HexColor("#F0EFF8")


def draw_page_bg(c, color=BLACK):
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def spaced(text):
    return "  ".join(text.upper())


def tag(c, text, x, y, color=PURPLE):
    c.setFont("Helvetica", 7)
    c.setFillColor(color)
    c.drawString(x, y, spaced(text))


def divider(c, x, y, w=40*mm, color=PURPLE):
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    c.line(x, y, x + w, y)


def page_number(c, num, total):
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY_DIM)
    c.drawString(20*mm, 12*mm, f"{num:02d} / {total:02d}")


# ── COVER ──────────────────────────────────────────────────────────────
def cover(c):
    draw_page_bg(c, BLACK)

    # Purple accent line top
    c.setStrokeColor(PURPLE)
    c.setLineWidth(2)
    c.line(20*mm, H - 18*mm, 60*mm, H - 18*mm)

    # Tag
    tag(c, "Eine App · Eine Geschichte", 20*mm, H - 30*mm)

    # Title
    c.setFont("Helvetica-Bold", 52)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 70*mm, "Short")
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 93*mm, "Flow")

    # Subtitle
    c.setFont("Helvetica", 13)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 112*mm, "Von der Idee zum Short.")

    # Divider
    divider(c, 20*mm, H - 125*mm, 30*mm)

    # Bottom info
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY_DIM)
    c.drawString(20*mm, 25*mm, "Mathias Kunze · WTF_Wissen_Official · 2026")

    c.showPage()


# ── STORY PAGE ──────────────────────────────────────────────────────────
def story_page(c):
    draw_page_bg(c, BLACK)

    tag(c, "Die Geschichte", 20*mm, H - 28*mm)

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 48*mm, "Wie ShortFlow")
    c.drawString(20*mm, H - 62*mm, "entstanden ist.")

    divider(c, 20*mm, H - 74*mm)

    text_lines = [
        "Ich hatte die Idee, ein bisschen Taschengeld zu verdienen. Nach langem",
        "Googeln bin ich irgendwie bei \"Faceless YouTube Kanal\" gelandet.",
        "Psychologie-Content, KI-Stimme, das übliche.",
        "",
        "Das Problem war die Fleißarbeit. Jeden Bildprompt einzeln in Adobe",
        "Firefly kopieren, für jeden Short einen Ordner erstellen, jedes Bild",
        "umbenennen. 30 Minuten pro Short. Das hat ewig gedauert.",
        "",
        "Also fing ich an das zu automatisieren. Erst ein kleines Python-Script",
        "namens \"SchnelleBilder\" — es las die Prompts aus meiner Tabelle, schickte",
        "sie zu fal.ai, lud die Bilder runter, benannte sie um und legte alles ab.",
        "Was vorher 30 Minuten pro Short war: 10 Minuten für den ganzen Monat.",
        "",
        "Dann wurde ChatGPT unzuverlässiger. Texte zu lang, zu kurz, vergaß wie",
        "die Tabelle aussehen soll. Ich hab stundenlang diskutiert.",
        "",
        "Also baute ich mit Claude Code eine App. Tage, Wochen, Monate.",
        "Mein Overthinker-Kopf brauchte einen Namen: ShortFlow war geboren.",
    ]

    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#CCCCCC"))
    y = H - 90*mm
    for line in text_lines:
        c.drawString(20*mm, y, line)
        y -= 5.5*mm

    # Quote block
    c.setFillColor(CARD)
    c.rect(20*mm, 28*mm, W - 40*mm, 22*mm, fill=1, stroke=0)
    c.setStrokeColor(PURPLE)
    c.setLineWidth(2)
    c.line(20*mm, 28*mm, 20*mm, 50*mm)

    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(OFF_WHITE)
    c.drawString(26*mm, 42*mm, "\"Zum Aufgeben ist es zu spät. Die App läuft sehr gut")
    c.drawString(26*mm, 35*mm, "und Short154 ist fertig.\"")

    page_number(c, 2, 8)
    c.showPage()


# ── WHAT IS SHORTFLOW ──────────────────────────────────────────────────
def what_page(c):
    draw_page_bg(c, BLACK)

    tag(c, "Überblick", 20*mm, H - 28*mm)

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 48*mm, "Was ShortFlow")
    c.drawString(20*mm, H - 62*mm, "macht.")

    divider(c, 20*mm, H - 74*mm)

    features = [
        ("Hooks & Texte", "KI generiert Hooks, Texte und Beschreibungen zu jedem Thema."),
        ("Bildprompts", "Automatisch erstellte Prompts, passend zur Stimmung des Shorts."),
        ("Bildgenerierung", "fal.ai generiert alle 10 Bilder und legt sie in die richtigen Ordner."),
        ("Ordnerstruktur", "Automatisch sortiert nach Thema und Monat auf dem iMac."),
        ("Desktop-Tabelle", "HTML-Tabelle mit Kopier-Buttons und visuellem Fortschritts-Status."),
        ("iPhone Export", "Über Netlify + Telegram-Bot direkt aufs Handy für Instagram."),
    ]

    y = H - 90*mm
    for i, (title, desc) in enumerate(features):
        # Card background
        c.setFillColor(CARD)
        c.roundRect(20*mm, y - 14*mm, W - 40*mm, 18*mm, 3*mm, fill=1, stroke=0)

        # Number
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(PURPLE)
        c.drawString(26*mm, y - 3*mm, f"{i+1:02d}")

        # Title
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(WHITE)
        c.drawString(36*mm, y - 3*mm, title)

        # Description
        c.setFont("Helvetica", 9)
        c.setFillColor(GRAY)
        c.drawString(36*mm, y - 9*mm, desc)

        y -= 22*mm

    page_number(c, 3, 8)
    c.showPage()


# ── BRAIN TAB ──────────────────────────────────────────────────────────
def brain_page(c):
    draw_page_bg(c, BLACK)

    tag(c, "Schritt 01 · Brain", 20*mm, H - 28*mm)

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 48*mm, "Thema rein.")
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 62*mm, "Tabelle raus.")

    divider(c, 20*mm, H - 74*mm)

    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#CCCCCC"))
    desc = [
        "Im Brain-Tab gibt man ein Thema ein und wählt, ob man einzelne Shorts",
        "oder einen ganzen Monat generieren möchte. Danach übernimmt die KI:",
        "Hooks, Texte, Bildprompts, Titel und Beschreibungen werden automatisch",
        "erstellt und in einer Tabelle gespeichert."
    ]
    y = H - 88*mm
    for line in desc:
        c.drawString(20*mm, y, line)
        y -= 5.5*mm

    # Mock UI card
    c.setFillColor(CARD)
    c.roundRect(20*mm, H - 175*mm, W - 40*mm, 72*mm, 4*mm, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GRAY)
    c.drawString(26*mm, H - 118*mm, "THEMA")
    c.setFillColor(HexColor("#2C2C2E"))
    c.roundRect(26*mm, H - 132*mm, 80*mm, 10*mm, 2*mm, fill=1, stroke=0)
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#AAAAAA"))
    c.drawString(29*mm, H - 129*mm, "Psychologie")

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GRAY)
    c.drawString(115*mm, H - 118*mm, "SHORTS")
    c.setFillColor(HexColor("#2C2C2E"))
    c.roundRect(115*mm, H - 132*mm, 25*mm, 10*mm, 2*mm, fill=1, stroke=0)
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#AAAAAA"))
    c.drawString(118*mm, H - 129*mm, "31")

    c.setFillColor(PURPLE)
    c.roundRect(148*mm, H - 133*mm, 35*mm, 12*mm, 2*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(WHITE)
    c.drawCentredString(165*mm, H - 128*mm, "GENERIEREN")

    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY_DIM)
    c.drawString(26*mm, H - 148*mm, "✓ Projekte: 1     ✓ Shorts: 154     ✓ Nächster Short: Short155")

    # Bottom info box
    c.setFillColor(HexColor("#1A1A2E"))
    c.roundRect(20*mm, 35*mm, W - 40*mm, 28*mm, 3*mm, fill=1, stroke=0)
    c.setStrokeColor(PURPLE_DIM)
    c.setLineWidth(1)
    c.roundRect(20*mm, 35*mm, W - 40*mm, 28*mm, 3*mm, fill=0, stroke=1)

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(PURPLE)
    c.drawString(26*mm, 56*mm, "Monat-Modus")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(26*mm, 49*mm, "Generiert einen vollständigen Monat auf einmal — inklusive")
    c.drawString(26*mm, 43*mm, "Datum, Wochentag und passender Musikzuordnung.")

    page_number(c, 4, 8)
    c.showPage()


# ── DIE TABELLE ─────────────────────────────────────────────────────────
def table_page(c):
    draw_page_bg(c, BLACK)

    tag(c, "Das Herzstück", 20*mm, H - 28*mm)

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 48*mm, "Die Tabelle.")

    divider(c, 20*mm, H - 60*mm)

    # Before/After
    for col, (label, sublabel, color) in enumerate([
        ("Vorher", "Numbers — alles manuell", GRAY_DIM),
        ("Nachher", "ShortFlow HTML mit Kopier-Buttons", PURPLE),
    ]):
        x = 20*mm + col * 90*mm
        c.setFillColor(CARD)
        c.roundRect(x, H - 155*mm, 82*mm, 82*mm, 3*mm, fill=1, stroke=0)

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(color)
        c.drawString(x + 6*mm, H - 82*mm, label.upper())

        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY)
        c.drawString(x + 6*mm, H - 88*mm, sublabel)

        # Mini table mockup
        cols_w = [10, 10, 18, 28, 16] if col == 0 else [10, 10, 14, 30, 18]
        headers = ["Short", "Datum", "Hook", "Text", "Status"]
        yt = H - 98*mm
        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(GRAY_DIM)
        xc = x + 4*mm
        for h, w in zip(headers, cols_w):
            c.drawString(xc, yt, h)
            xc += w * 0.6*mm + 3*mm

        for row in range(3):
            yt -= 8*mm
            c.setFillColor(HexColor("#222224") if row % 2 == 0 else CARD)
            c.rect(x + 4*mm, yt - 2*mm, 74*mm, 7*mm, fill=1, stroke=0)
            c.setFont("Helvetica", 6)
            c.setFillColor(HexColor("#AAAAAA"))
            c.drawString(x + 6*mm, yt + 1*mm, f"Short{154+row}")

            if col == 1:
                btn_color = PURPLE if row < 2 else HexColor("#333355")
                c.setFillColor(btn_color)
                c.roundRect(x + 60*mm, yt - 1*mm, 14*mm, 5*mm, 1*mm, fill=1, stroke=0)
                c.setFont("Helvetica-Bold", 5)
                c.setFillColor(WHITE)
                c.drawCentredString(x + 67*mm, yt + 1.5*mm, "Kopieren" if row < 2 else "Fertig")

    # Feature list
    y = H - 172*mm
    items = [
        "Einmal klicken → Text wird leicht transparent (teilweise fertig)",
        "Alles kopiert → Zeile wird dunkel (Short komplett abgehakt)",
        "Zwei Versionen: Desktop-Ansicht und iPhone/Instagram-Ansicht",
    ]
    for item in items:
        c.setFillColor(PURPLE)
        c.circle(23*mm, y + 1.5*mm, 1*mm, fill=1, stroke=0)
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#CCCCCC"))
        c.drawString(27*mm, y, item)
        y -= 7*mm

    page_number(c, 5, 8)
    c.showPage()


# ── MACHINE TAB ─────────────────────────────────────────────────────────
def machine_page(c):
    draw_page_bg(c, BLACK)

    tag(c, "Schritt 02 · Machine", 20*mm, H - 28*mm)

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 48*mm, "Medien-Paket")
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 62*mm, "schnüren.")

    divider(c, 20*mm, H - 74*mm)

    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#CCCCCC"))
    desc = [
        "Im Machine-Tab lädt man die generierte CSV-Tabelle und startet",
        "\"Medien-Paket schnüren\". ShortFlow sendet jeden Bildprompt an fal.ai,",
        "wartet auf die Generierung, lädt die Bilder herunter, benennt sie um",
        "und legt sie in die richtigen Short-Ordner ab."
    ]
    y = H - 88*mm
    for line in desc:
        c.drawString(20*mm, y, line)
        y -= 5.5*mm

    # Flow diagram
    steps = [
        ("CSV laden", "Tabelle mit allen\nPrompts einlesen"),
        ("fal.ai", "KI generiert\njedes Bild"),
        ("Umbenennen", "Bild01 bis\nBild10"),
        ("Ablegen", "In den richtigen\nShort-Ordner"),
    ]
    box_w = 38*mm
    gap = 5*mm
    total = len(steps) * box_w + (len(steps)-1) * gap
    start_x = (W - total) / 2

    y_box = H - 160*mm
    for i, (title, sub) in enumerate(steps):
        x = start_x + i * (box_w + gap)
        c.setFillColor(CARD)
        c.roundRect(x, y_box, box_w, 28*mm, 3*mm, fill=1, stroke=0)

        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(PURPLE if i in (1, 3) else WHITE)
        c.drawCentredString(x + box_w/2, y_box + 20*mm, title)

        c.setFont("Helvetica", 7.5)
        c.setFillColor(GRAY)
        for j, line in enumerate(sub.split("\n")):
            c.drawCentredString(x + box_w/2, y_box + 13*mm - j*5*mm, line)

        if i < len(steps)-1:
            arr_x = x + box_w + 1.5*mm
            arr_y = y_box + 14*mm
            c.setStrokeColor(PURPLE_DIM)
            c.setLineWidth(1)
            c.line(arr_x, arr_y, arr_x + gap - 3*mm, arr_y)
            c.setFillColor(PURPLE_DIM)
            p = c.beginPath()
            p.moveTo(arr_x + gap - 3*mm, arr_y + 1.5*mm)
            p.lineTo(arr_x + gap - 3*mm, arr_y - 1.5*mm)
            p.lineTo(arr_x + gap, arr_y)
            p.close()
            c.drawPath(p, fill=1, stroke=0)

    # Stat
    c.setFillColor(CARD)
    c.roundRect(20*mm, 35*mm, W - 40*mm, 28*mm, 3*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(PURPLE)
    c.drawString(30*mm, 48*mm, "30 Min  →  10 Min")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(30*mm, 41*mm, "Pro Short manuell  →  für den ganzen Monat automatisch")

    page_number(c, 6, 8)
    c.showPage()


# ── ORDNERSTRUKTUR ──────────────────────────────────────────────────────
def folder_page(c):
    draw_page_bg(c, BLACK)

    tag(c, "Ausgabe · Dateisystem", 20*mm, H - 28*mm)

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 48*mm, "Alles an seinem")
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 62*mm, "Platz.")

    divider(c, 20*mm, H - 74*mm)

    # Folder tree
    tree = [
        (0, "WTFWissen/Shorts/", True),
        (1, "Psychologie'26/", True),
        (2, "02.Februar'26/", True),
        (3, "Short24/ … Short55/", False),
        (2, "07.Juli'26/", True),
        (3, "Short147/ … Short177/", False),
        (4, "Bild01.png … Bild10.png", False),
        (4, "prompts.txt", False),
        (4, "Short147.mp3  (manuell)", False),
        (4, "Short147.mp4  (manuell)", False),
        (3, "Psychologie-Short-Tabelle.html", False),
        (3, "Psychologie26-Short-T...e-IG.html", False),
    ]

    y = H - 90*mm
    c.setFont("Helvetica", 9)
    for depth, name, is_dir in tree:
        x = 20*mm + depth * 8*mm
        if depth == 0:
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 9)
        elif is_dir:
            c.setFillColor(PURPLE)
            c.setFont("Helvetica-Bold", 9)
        else:
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 9)
        prefix = "▸ " if is_dir else "· "
        c.drawString(x, y, prefix + name)
        y -= 6.5*mm

    # Note
    c.setFillColor(CARD)
    c.roundRect(20*mm, 35*mm, W - 40*mm, 22*mm, 3*mm, fill=1, stroke=0)
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(26*mm, 49*mm, "ShortFlow legt Ordner, Bilder und Tabellen automatisch an.")
    c.drawString(26*mm, 43*mm, "Audio und Premiere-Projektfile werden manuell hinzugefügt.")

    page_number(c, 7, 8)
    c.showPage()


# ── IPHONE / TELEGRAM ──────────────────────────────────────────────────
def iphone_page(c):
    draw_page_bg(c, BLACK)

    tag(c, "Schritt 03 · iPhone Export", 20*mm, H - 28*mm)

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 48*mm, "Direkt aufs")
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 62*mm, "iPhone.")

    divider(c, 20*mm, H - 74*mm)

    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#CCCCCC"))
    desc = [
        "\"iPhone IG Export\" klicken → ShortFlow generiert eine mobile HTML-Seite,",
        "lädt sie auf Netlify hoch und schickt den Link per Telegram-Bot als DM.",
        "Im iPhone Safari öffnet sich die Seite — alle Texte per 1-Tap kopierbar."
    ]
    y = H - 88*mm
    for line in desc:
        c.drawString(20*mm, y, line)
        y -= 5.5*mm

    # Flow
    steps = ["iPhone IG Export klicken", "HTML → Netlify", "Telegram Bot sendet Link", "Safari öffnen & kopieren"]
    y_s = H - 130*mm
    for i, step in enumerate(steps):
        c.setFillColor(PURPLE if i % 2 == 0 else CARD)
        c.roundRect(20*mm, y_s, W - 40*mm, 12*mm, 2*mm, fill=1, stroke=0)
        c.setFont("Helvetica", 9)
        c.setFillColor(WHITE)
        c.drawString(28*mm, y_s + 4*mm, f"{i+1}.  {step}")
        y_s -= 16*mm

    # Settings reminder
    c.setFillColor(HexColor("#1A1A2E"))
    c.roundRect(20*mm, 35*mm, W - 40*mm, 40*mm, 3*mm, fill=1, stroke=0)
    c.setStrokeColor(PURPLE_DIM)
    c.setLineWidth(1)
    c.roundRect(20*mm, 35*mm, W - 40*mm, 40*mm, 3*mm, fill=0, stroke=1)

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(PURPLE)
    c.drawString(26*mm, 68*mm, "Einmalig in den Settings eintragen:")
    items = ["Netlify Token", "Telegram Bot Token", "Telegram Chat-ID"]
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    for i, item in enumerate(items):
        c.drawString(26*mm + i * 55*mm, 60*mm, "· " + item)

    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY_DIM)
    c.drawString(26*mm, 43*mm, "Danach läuft alles mit einem Klick — für jeden neuen Monat.")

    page_number(c, 8, 8)
    c.showPage()


# ── MAIN ────────────────────────────────────────────────────────────────
out = "/Users/mathiaskunze/Downloads/ShortFlow-Dokumentation.pdf"
c = canvas.Canvas(out, pagesize=A4)
c.setTitle("ShortFlow — Dokumentation")
c.setAuthor("Mathias Kunze")

cover(c)
story_page(c)
what_page(c)
brain_page(c)
table_page(c)
machine_page(c)
folder_page(c)
iphone_page(c)

c.save()
print(f"Gespeichert: {out}")
