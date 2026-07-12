from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

W, H = A4
IMG = "/Users/mathiaskunze/Downloads/ShortFlow/Bilder/"

BLACK      = HexColor("#0D0D0D")
DARK       = HexColor("#141414")
CARD       = HexColor("#1C1C1E")
PURPLE     = HexColor("#7F77DD")
PURPLE_DIM = HexColor("#534AB7")
WHITE      = HexColor("#FFFFFF")
GRAY       = HexColor("#888888")
GRAY_DIM   = HexColor("#444444")
GRAY_LIGHT = HexColor("#CCCCCC")


def bg(c, color=BLACK):
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def spaced(t):
    return "  ".join(t.upper())


def tag(c, text, x, y):
    c.setFont("Helvetica", 7)
    c.setFillColor(PURPLE)
    c.drawString(x, y, spaced(text))


def divider(c, x, y, w=35*mm):
    c.setStrokeColor(PURPLE)
    c.setLineWidth(1.5)
    c.line(x, y, x + w, y)


def pnum(c, n, total):
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY_DIM)
    c.drawString(20*mm, 12*mm, f"{n:02d} / {total:02d}")


def img(c, fname, x, y, w, h, radius=3*mm):
    try:
        ir = ImageReader(IMG + fname)
        iw, ih = ir.getSize()
        ratio = iw / ih
        # fit into w x h keeping aspect ratio
        if w / h > ratio:
            fw = h * ratio
            fh = h
            fx = x + (w - fw) / 2
            fy = y
        else:
            fw = w
            fh = w / ratio
            fx = x
            fy = y + (h - fh) / 2
        # rounded clip
        p = c.beginPath()
        p.roundRect(fx, fy, fw, fh, radius)
        c.clipPath(p, stroke=0)
        c.drawImage(ir, fx, fy, fw, fh)
        c.restoreState()
        c.saveState()
    except Exception as e:
        # fallback: gray box
        c.setFillColor(CARD)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=0)
        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY_DIM)
        c.drawCentredString(x + w/2, y + h/2, fname)


def img_simple(c, fname, x, y, w, h):
    """Draw image without clipping (simpler, more reliable)"""
    try:
        ir = ImageReader(IMG + fname)
        iw, ih = ir.getSize()
        ratio = iw / ih
        if w / h > ratio:
            fw = h * ratio
            fh = h
            fx = x + (w - fw) / 2
            fy = y
        else:
            fw = w
            fh = w / ratio
            fx = x
            fy = y + (h - fh) / 2
        c.drawImage(ir, fx, fy, fw, fh)
    except Exception as e:
        c.setFillColor(CARD)
        c.roundRect(x, y, w, h, 2*mm, fill=1, stroke=0)
        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY_DIM)
        c.drawCentredString(x + w/2, y + h/2, fname)


def img_frame(c, fname, x, y, w, h, label=None):
    """Image with purple frame and optional label"""
    c.setFillColor(CARD)
    c.roundRect(x - 2*mm, y - 2*mm, w + 4*mm, h + 4*mm + (6*mm if label else 0), 3*mm, fill=1, stroke=0)
    img_simple(c, fname, x, y, w, h)
    if label:
        c.setFont("Helvetica", 7)
        c.setFillColor(PURPLE)
        c.drawCentredString(x + w/2, y - 5*mm, label)


TOTAL = 9

# ── 1. COVER ────────────────────────────────────────────────────────────
def page_cover(c):
    bg(c)
    c.setStrokeColor(PURPLE)
    c.setLineWidth(2)
    c.line(20*mm, H - 18*mm, 55*mm, H - 18*mm)

    tag(c, "Eine App · Eine Geschichte", 20*mm, H - 29*mm)

    c.setFont("Helvetica-Bold", 58)
    c.setFillColor(WHITE)
    c.drawString(19*mm, H - 72*mm, "Short")
    c.setFillColor(PURPLE)
    c.drawString(19*mm, H - 97*mm, "Flow")

    c.setFont("Helvetica", 13)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 114*mm, "Von der Idee zum Short.")
    divider(c, 20*mm, H - 124*mm, 28*mm)

    # small preview strip of screenshots at bottom
    imgs = ["Bild03.png", "Bild02.png", "Bild07.png"]
    strip_y = 38*mm
    strip_w = (W - 40*mm - 8*mm) / 3
    for i, im in enumerate(imgs):
        x = 20*mm + i * (strip_w + 4*mm)
        c.setFillColor(CARD)
        c.roundRect(x, strip_y, strip_w, 38*mm, 2*mm, fill=1, stroke=0)
        img_simple(c, im, x + 1*mm, strip_y + 1*mm, strip_w - 2*mm, 36*mm)

    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY_DIM)
    c.drawString(20*mm, 22*mm, "Mathias Kunze · WTF_Wissen_Official · 2026")
    c.showPage()


# ── 2. GESCHICHTE ───────────────────────────────────────────────────────
def page_story(c):
    bg(c)
    tag(c, "Die Geschichte", 20*mm, H - 28*mm)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 50*mm, "Wie ShortFlow")
    c.drawString(20*mm, H - 65*mm, "entstanden ist.")
    divider(c, 20*mm, H - 77*mm)

    paras = [
        "Ich hatte die Idee, ein bisschen Taschengeld zu verdienen. Nach langem Googeln",
        "bin ich irgendwie bei \"Faceless YouTube Kanal\" gelandet. Psychologie-Content,",
        "KI-Stimme, das übliche.",
        "",
        "Das Problem war die Fleißarbeit. Jeden Bildprompt einzeln in Adobe Firefly",
        "kopieren, für jeden Short einen Ordner erstellen, jedes Bild umbenennen.",
        "30 Minuten pro Short. Das hat ewig gedauert.",
        "",
        "Also fing ich an das zu automatisieren. Erst ein Python-Script namens",
        "\"SchnelleBilder\": Prompts aus Tabelle lesen → fal.ai → Bilder runterladen",
        "→ umbenennen → in Ordner ablegen. Was vorher 30 Min pro Short war:",
        "10 Minuten für den ganzen Monat.",
        "",
        "Dann wurde ChatGPT unzuverlässiger. Also baute ich mit Claude Code eine",
        "eigene App. Tage, Wochen, Monate. Mein Overthinker-Kopf brauchte einen",
        "Namen: ShortFlow war geboren.",
        "",
        "Zwischendurch wollte ich die App verkaufen. Eine KI-Analyse sagte mir klar:",
        "wird nicht funktionieren. Das tat weh. Egal — die App läuft für mich und",
        "das reicht. Zum Aufgeben ist es zu spät.",
    ]
    c.setFont("Helvetica", 9.5)
    c.setFillColor(GRAY_LIGHT)
    y = H - 91*mm
    for line in paras:
        c.drawString(20*mm, y, line)
        y -= 5.2*mm

    # Quote
    c.setFillColor(CARD)
    c.roundRect(20*mm, 30*mm, W - 40*mm, 20*mm, 3*mm, fill=1, stroke=0)
    c.setStrokeColor(PURPLE)
    c.setLineWidth(2)
    c.line(20*mm, 30*mm, 20*mm, 50*mm)
    c.setFont("Helvetica-Oblique", 9.5)
    c.setFillColor(WHITE)
    c.drawString(26*mm, 43*mm, "\"Short154 ist fertig. Zum Aufgeben ist es zu spät.\"")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(26*mm, 36*mm, "Mathias Kunze, WTF_Wissen_Official")

    pnum(c, 2, TOTAL)
    c.showPage()


# ── 3. BRAIN TAB ────────────────────────────────────────────────────────
def page_brain(c):
    bg(c)
    tag(c, "Schritt 01 · Brain", 20*mm, H - 28*mm)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 50*mm, "Thema rein.")
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 65*mm, "Tabelle raus.")
    divider(c, 20*mm, H - 77*mm)

    c.setFont("Helvetica", 9.5)
    c.setFillColor(GRAY_LIGHT)
    lines = [
        "Thema eingeben, Anzahl wählen — ShortFlow generiert Hooks, Texte,",
        "Bildprompts, Titel und Beschreibungen. Einzeln oder als ganzer Monat."
    ]
    y = H - 90*mm
    for l in lines:
        c.drawString(20*mm, y, l)
        y -= 5.5*mm

    # Big screenshot
    img_simple(c, "Bild03.png", 20*mm, H - 210*mm, W - 40*mm, 108*mm)
    c.setStrokeColor(GRAY_DIM)
    c.setLineWidth(0.5)
    c.roundRect(20*mm, H - 210*mm, W - 40*mm, 108*mm, 2*mm, stroke=1, fill=0)

    # Caption
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY_DIM)
    c.drawCentredString(W/2, H - 217*mm, "Brain-Tab — Thema \"Biologie\", 2 Shorts generiert")

    # Features
    feats = [
        ("Einzeln", "Wenige Shorts auf Abruf"),
        ("Monat", "Ganzen Monat auf einmal, mit Datum + Wochentag"),
        ("Weiterzählen", "Erkennt vorhandene Shorts und zählt korrekt weiter"),
    ]
    y = H - 232*mm
    for title, desc in feats:
        c.setFillColor(PURPLE)
        c.circle(23*mm, y + 1.5*mm, 1.2*mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(WHITE)
        c.drawString(27*mm, y, title + " —")
        c.setFont("Helvetica", 9)
        c.setFillColor(GRAY)
        tw = c.stringWidth(title + " — ", "Helvetica-Bold", 9)
        c.drawString(27*mm + tw, y, desc)
        y -= 6.5*mm

    pnum(c, 3, TOTAL)
    c.showPage()


# ── 4. DIE TABELLE — VORHER / NACHHER ───────────────────────────────────
def page_tabelle(c):
    bg(c)
    tag(c, "Das Herzstück", 20*mm, H - 28*mm)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 50*mm, "Vorher. Nachher.")
    divider(c, 20*mm, H - 62*mm)

    half = (W - 44*mm) / 2

    # VORHER
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GRAY_DIM)
    c.drawString(20*mm, H - 76*mm, spaced("Vorher"))
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(20*mm, H - 82*mm, "Numbers — alles manuell kopieren")
    img_simple(c, "Bild01.png", 20*mm, H - 185*mm, half, 95*mm)
    c.setStrokeColor(GRAY_DIM)
    c.setLineWidth(0.5)
    c.rect(20*mm, H - 185*mm, half, 95*mm, stroke=1, fill=0)

    # NACHHER
    x2 = 20*mm + half + 4*mm
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(PURPLE)
    c.drawString(x2, H - 76*mm, spaced("Nachher"))
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(x2, H - 82*mm, "ShortFlow HTML — 1 Klick zum Kopieren")
    img_simple(c, "Bild02.png", x2, H - 185*mm, half, 95*mm)
    c.setStrokeColor(PURPLE_DIM)
    c.setLineWidth(0.5)
    c.rect(x2, H - 185*mm, half, 95*mm, stroke=1, fill=0)

    # Info boxes
    infos = [
        ("30 Min / Short", "manuell in Firefly", GRAY_DIM),
        ("10 Min / Monat", "vollautomatisch", PURPLE),
    ]
    y_info = H - 210*mm
    for i, (val, sub, col) in enumerate(infos):
        xi = 20*mm + i * (half + 4*mm)
        c.setFillColor(CARD)
        c.roundRect(xi, y_info, half, 16*mm, 2*mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(col)
        c.drawString(xi + 4*mm, y_info + 9*mm, val)
        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY)
        c.drawString(xi + 4*mm, y_info + 3*mm, sub)

    # Description
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY_LIGHT)
    desc = [
        "Die HTML-Tabelle hat Kopier-Buttons mit visuellem Status-System:",
        "1x klicken = leicht transparent (teilweise fertig)  ·  alles kopiert = dunkel (Short fertig)",
        "Zwei Versionen: Desktop-Ansicht für den iMac, iPhone-Ansicht für Instagram."
    ]
    y = H - 232*mm
    for l in desc:
        c.drawString(20*mm, y, l)
        y -= 5.5*mm

    pnum(c, 4, TOTAL)
    c.showPage()


# ── 5. MACHINE TAB ──────────────────────────────────────────────────────
def page_machine(c):
    bg(c)
    tag(c, "Schritt 02 · Machine", 20*mm, H - 28*mm)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 50*mm, "Medien-Paket")
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 65*mm, "schnüren.")
    divider(c, 20*mm, H - 77*mm)

    c.setFont("Helvetica", 9.5)
    c.setFillColor(GRAY_LIGHT)
    lines = [
        "CSV laden, Output-Ordner wählen, Button klicken. ShortFlow schickt",
        "jeden Prompt an fal.ai, lädt die Bilder runter und legt alles ab."
    ]
    y = H - 90*mm
    for l in lines:
        c.drawString(20*mm, y, l)
        y -= 5.5*mm

    img_simple(c, "Bild04.png", 20*mm, H - 210*mm, W - 40*mm, 108*mm)
    c.setStrokeColor(GRAY_DIM)
    c.setLineWidth(0.5)
    c.roundRect(20*mm, H - 210*mm, W - 40*mm, 108*mm, 2*mm, stroke=1, fill=0)

    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY_DIM)
    c.drawCentredString(W/2, H - 217*mm, "Machine-Tab — Bildgenerierung läuft, Log zeigt Fortschritt in Echtzeit")

    # Stat bar
    c.setFillColor(CARD)
    c.roundRect(20*mm, 30*mm, W - 40*mm, 20*mm, 3*mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(PURPLE)
    c.drawString(30*mm, 42*mm, "10 Bilder pro Short")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(30*mm, 35*mm, "Automatisch generiert, umbenannt und in den richtigen Ordner abgelegt")

    pnum(c, 5, TOTAL)
    c.showPage()


# ── 6. SETTINGS ─────────────────────────────────────────────────────────
def page_settings(c):
    bg(c)
    tag(c, "Einmalig einrichten", 20*mm, H - 28*mm)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 50*mm, "Settings.")
    divider(c, 20*mm, H - 62*mm)

    c.setFont("Helvetica", 9.5)
    c.setFillColor(GRAY_LIGHT)
    lines = [
        "Einmalig API-Keys eintragen — danach läuft alles auf Knopfdruck.",
        "Musik-Zuordnung bestimmt welcher Track zu welcher Stimmung passt."
    ]
    y = H - 75*mm
    for l in lines:
        c.drawString(20*mm, y, l)
        y -= 5.5*mm

    img_simple(c, "Bild05.png", 20*mm, H - 200*mm, W - 40*mm, 108*mm)
    c.setStrokeColor(GRAY_DIM)
    c.setLineWidth(0.5)
    c.roundRect(20*mm, H - 200*mm, W - 40*mm, 108*mm, 2*mm, stroke=1, fill=0)

    # Keys overview
    keys = ["OpenAI / Gemini API-Key", "fal.ai Bildgenerator-Key", "Netlify Token + Site-ID", "Telegram Bot-Token + Chat-ID"]
    y = H - 218*mm
    for i, key in enumerate(keys):
        xi = 20*mm + (i % 2) * (half_w := (W - 44*mm) / 2 + 2*mm)
        if i % 2 == 0 and i > 0:
            y -= 8*mm
        c.setFillColor(CARD)
        c.roundRect(xi, y - 1*mm, half_w - 2*mm, 7*mm, 1.5*mm, fill=1, stroke=0)
        c.setFillColor(PURPLE)
        c.circle(xi + 4*mm, y + 2.5*mm, 1*mm, fill=1, stroke=0)
        c.setFont("Helvetica", 8.5)
        c.setFillColor(GRAY_LIGHT)
        c.drawString(xi + 7*mm, y + 0.5*mm, key)

    pnum(c, 6, TOTAL)
    c.showPage()


# ── 7. IPHONE / TELEGRAM ────────────────────────────────────────────────
def page_iphone(c):
    bg(c)
    tag(c, "Schritt 03 · iPhone Export", 20*mm, H - 28*mm)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 50*mm, "Direkt aufs")
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 65*mm, "iPhone.")
    divider(c, 20*mm, H - 77*mm)

    c.setFont("Helvetica", 9.5)
    c.setFillColor(GRAY_LIGHT)
    lines = [
        "\"iPhone IG Export\" klicken → HTML auf Netlify → Telegram-Bot schickt",
        "Link per DM → iPhone Safari öffnen → 1-Tap kopieren für Instagram."
    ]
    y = H - 90*mm
    for l in lines:
        c.drawString(20*mm, y, l)
        y -= 5.5*mm

    half = (W - 44*mm) / 2

    # Telegram screenshot
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GRAY_DIM)
    c.drawString(20*mm, H - 108*mm, spaced("Telegram Bot"))
    img_simple(c, "Bild06.png", 20*mm, H - 210*mm, half, 95*mm)
    c.setStrokeColor(GRAY_DIM)
    c.setLineWidth(0.5)
    c.rect(20*mm, H - 210*mm, half, 95*mm, stroke=1, fill=0)

    # iPhone Safari screenshot
    x2 = 20*mm + half + 4*mm
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(PURPLE)
    c.drawString(x2, H - 108*mm, spaced("iPhone Safari"))
    img_simple(c, "Bild07.png", x2, H - 210*mm, half, 95*mm)
    c.setStrokeColor(PURPLE_DIM)
    c.setLineWidth(0.5)
    c.rect(x2, H - 210*mm, half, 95*mm, stroke=1, fill=0)

    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY_DIM)
    c.drawString(20*mm, H - 216*mm, "Alle Links landen automatisch im Telegram-Chat  ·  Seite läuft auf Netlify")

    # Flow steps
    steps = ["1. Export klicken", "2. → Netlify", "3. → Telegram DM", "4. → Safari kopieren"]
    step_w = (W - 40*mm) / 4
    y_s = H - 237*mm
    for i, step in enumerate(steps):
        xi = 20*mm + i * step_w
        c.setFillColor(PURPLE if i % 2 == 0 else CARD)
        c.roundRect(xi, y_s, step_w - 2*mm, 10*mm, 1.5*mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold" if i % 2 == 0 else "Helvetica", 8)
        c.setFillColor(WHITE)
        c.drawCentredString(xi + (step_w - 2*mm)/2, y_s + 3.5*mm, step)

    pnum(c, 7, TOTAL)
    c.showPage()


# ── 8. ORDNERSTRUKTUR ───────────────────────────────────────────────────
def page_folder(c):
    bg(c)
    tag(c, "Ausgabe · Dateisystem", 20*mm, H - 28*mm)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 50*mm, "Alles an")
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 65*mm, "seinem Platz.")
    divider(c, 20*mm, H - 77*mm)

    c.setFont("Helvetica", 9.5)
    c.setFillColor(GRAY_LIGHT)
    c.drawString(20*mm, H - 90*mm, "ShortFlow legt die gesamte Ordnerstruktur automatisch an.")

    # 4 screenshots in 2x2 grid
    half_w = (W - 44*mm) / 2
    half_h = 72*mm
    grid = [
        ("Bild08.png", "WTFWissen/Shorts/ — Themen-Ebene"),
        ("Bild09.png", "Thema → Monats-Ebene"),
        ("Bild10.png", "Monat → Short-Ordner + HTML-Tabellen"),
        ("Bild11.png", "Short178 — 10 Bilder + prompts.txt"),
    ]
    for i, (fname, label) in enumerate(grid):
        col = i % 2
        row = i // 2
        xi = 20*mm + col * (half_w + 4*mm)
        yi = H - 110*mm - row * (half_h + 14*mm)

        img_simple(c, fname, xi, yi, half_w, half_h)
        c.setStrokeColor(GRAY_DIM)
        c.setLineWidth(0.5)
        c.rect(xi, yi, half_w, half_h, stroke=1, fill=0)

        c.setFont("Helvetica", 7.5)
        c.setFillColor(GRAY_DIM)
        c.drawString(xi, yi - 4*mm, label)

    # Bottom note
    c.setFillColor(CARD)
    c.roundRect(20*mm, 20*mm, W - 40*mm, 15*mm, 2*mm, fill=1, stroke=0)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRAY)
    c.drawString(26*mm, 29*mm, "Audio (.mp3) und Premiere-Projektfile werden manuell in den Short-Ordner gezogen.")

    pnum(c, 8, TOTAL)
    c.showPage()


# ── 9. ABSCHLUSS ────────────────────────────────────────────────────────
def page_end(c):
    bg(c, BLACK)

    c.setStrokeColor(PURPLE)
    c.setLineWidth(2)
    c.line(20*mm, H - 18*mm, 55*mm, H - 18*mm)

    tag(c, "Stand · Juni 2026", 20*mm, H - 30*mm)

    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(WHITE)
    c.drawString(20*mm, H - 65*mm, "Short154")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H - 80*mm, "ist fertig.")

    divider(c, 20*mm, H - 92*mm)

    stats = [
        ("154+", "generierte Shorts"),
        ("6", "Monate aktiv"),
        ("4", "eigene Musiktitel"),
        ("1", "App. Von Grund auf."),
    ]
    y = H - 115*mm
    for val, label in stats:
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(PURPLE)
        c.drawString(20*mm, y, val)
        c.setFont("Helvetica", 10)
        c.setFillColor(GRAY)
        c.drawString(20*mm, y - 7*mm, label)
        y -= 24*mm

    # Final quote
    c.setFillColor(CARD)
    c.roundRect(20*mm, 55*mm, W - 40*mm, 35*mm, 3*mm, fill=1, stroke=0)
    c.setStrokeColor(PURPLE)
    c.setLineWidth(2)
    c.line(20*mm, 55*mm, 20*mm, 90*mm)
    c.setFont("Helvetica-Oblique", 10.5)
    c.setFillColor(WHITE)
    c.drawString(26*mm, 78*mm, "\"Es gibt Automatisierungen, die das alles können und")
    c.drawString(26*mm, 71*mm, "sogar selbst posten. Ich will die Kontrolle behalten.")
    c.drawString(26*mm, 64*mm, "Ich schneide jeden Clip selbst.\"")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(26*mm, 58*mm, "Mathias Kunze")

    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY_DIM)
    c.drawString(20*mm, 22*mm, "WTF_Wissen_Official · YouTube · Instagram · 2026")
    pnum(c, 9, TOTAL)
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
