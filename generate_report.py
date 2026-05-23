from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "ShortFlow - Markt- und Produktbericht | Mai 2026", align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"Seite {self.page_no()}", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

def section(pdf, title):
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(40, 40, 40)
    pdf.cell(0, 9, f"  {title}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

def subsection(pdf, title):
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

def body(pdf, text):
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(55, 55, 55)
    pdf.multi_cell(0, 6, text)

def bullet(pdf, items):
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(55, 55, 55)
    for item in items:
        pdf.multi_cell(0, 6, f"  - {item}")
        pdf.ln(1)

def risk_table(pdf, rows):
    pdf.ln(2)
    col1, col2 = 110, 75
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(col1, 7, " Risiko", fill=True)
    pdf.cell(col2, 7, " Einschaetzung", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    alt = False
    for risiko, grad in rows:
        pdf.set_fill_color(245, 245, 245) if alt else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(col1, 7, f" {risiko}", fill=True)
        pdf.cell(col2, 7, f" {grad}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        alt = not alt
    pdf.ln(2)

# --- Build PDF ---
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Title block
pdf.set_font("Helvetica", "B", 22)
pdf.set_text_color(20, 20, 20)
pdf.cell(0, 13, "ShortFlow", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(90, 90, 90)
pdf.cell(0, 7, "Markt- und Produktbericht  |  Mai 2026", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(3)
pdf.set_draw_color(180, 180, 180)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(6)

# Was ist ShortFlow
section(pdf, "Was ist ShortFlow")
body(pdf,
    "ShortFlow ist ein Desktop-Tool fuer die strukturierte Produktion von YouTube-Shorts-Serien. "
    "Es automatisiert den Planungsschritt: Ein Thema und eine gewuenschte Anzahl werden eingegeben, "
    "die ChatGPT-API generiert daraus strukturierte Inhalte (Hook, Text, Bildprompts, Titel, Beschreibung) "
    "als JSON, welches in eine Tabelle (.xlsx/.csv) und geordnete Bildpakete ueberfuehrt wird.\n\n"
    "ShortFlow ist kein Videoeditor. Es ersetzt Notion-Tabellen, Excel-Kalender und manuelle "
    "Prompt-Verwaltung. Output: fertige Ordnerstrukturen mit Bild-Assets, bereit zur Nachbearbeitung."
)

# Produktanalyse
section(pdf, "Produktanalyse")

subsection(pdf, "Staerken")
bullet(pdf, [
    "Klare Nische: Workflow-Automatisierung vor dem Schnitt, nicht der Schnitt selbst",
    "Loest ein echtes Reibungsproblem: Wer 10-20 Shorts plant, verliert ohne System den Ueberblick",
    "Kein Konkurrent adressiert genau diesen Schritt (Planung -> strukturierte Assets)",
    "Desktop-App: kein Datenschutzproblem, keine Serverkosten fuer den Nutzer",
])

subsection(pdf, "Schwaechen")
bullet(pdf, [
    "Keine Validierung durch echte Nutzer - bisher ein Tool fuer eine Person",
    "Setzt voraus, dass Creator serienmaessig produzieren - viele produzieren sporadisch",
    "Abhaengigkeit von ChatGPT-API: Kosten, Ausfaelle und Qualitaetsschwankungen ausserhalb der Kontrolle",
    "Kein Upload, kein Video, kein Audio: Nutzer muss nach ShortFlow noch erheblich weiterarbeiten",
])

# Markt
section(pdf, "Markteinschaetzung")

subsection(pdf, "Zielgruppe (realistisch)")
body(pdf,
    "Klein. Der deutschsprachige Markt fuer YouTube-Shorts-Creator, die (a) KI nutzen, "
    "(b) strukturiert in Serien denken und (c) bereit sind, ein Workflow-Tool zu kaufen, ist eng. "
    "Schaetzung: wenige Tausend Personen in DACH, davon ein Bruchteil zahlungswillig."
)

subsection(pdf, "Wettbewerber")
bullet(pdf, [
    "CapCut / Opus Clip: Andere Kategorie (Schnitt), kaum Ueberschneidung",
    "Notion + Excel: Eigentlicher Gegner - kostenlos, flexibel, bekannt. Wechselhuerde hoch",
    "KI-All-in-one-Tools: Langfristiges Risiko - wenn ChatGPT selbst Content-Pakete exportiert, faellt USP weg",
])

subsection(pdf, "Preismodell")
bullet(pdf, [
    "15 EUR/Monat Abo: schwer durchsetzbar fuer Nischentool ohne Community-Rueckhalt",
    "Einmaliger Kauf (49-79 EUR): glaubwuerdiger fuer Einzelpersonen, kein laufendes Commitment",
    "Demo-first ist richtig: Ohne kostenlose Testversion wird kaum jemand kaufen",
])

# Risiken
section(pdf, "Risiken")
risk_table(pdf, [
    ("Niemand braucht diesen Workflow", "Hoch - unvalidiert"),
    ("Zu kleine Zielgruppe fuer Skalierung", "Hoch"),
    ("ChatGPT-API-Kosten steigen", "Mittel"),
    ("Groesserer Player baut Feature nach", "Mittel  (12-24 Monate Puffer)"),
    ("Creator wechseln zu anderem Workflow", "Niedrig"),
])

# Teststrategie
section(pdf, "Teststrategie (Empfehlung)")
bullet(pdf, [
    "Selbsttest: 3 komplette Short-Serien mit ShortFlow produzieren - Reibungspunkte dokumentieren",
    "5 echte Creator ansprechen (Reddit, Discord) - Tool zeigen, Reaktion beobachten, kein Pitch",
    "Eine Frage stellen: 'Wuerdest du dafuer 15 EUR einmalig zahlen?' - nicht 'Findest du es gut?'",
    "Erst danach Monetarisierungsmodell festlegen",
])

# Fazit
section(pdf, "Fazit")
body(pdf,
    "ShortFlow loest ein reales Problem fuer eine sehr spitze Zielgruppe. Das Risiko liegt nicht im Produkt, "
    "sondern in der Marktgroesse und der fehlenden Validierung. Es ist kein skalierbares SaaS - es kann ein "
    "solides Indie-Tool werden, wenn die Zielgruppe den Workflow tatsaechlich uebernimmt. Der einzige Weg "
    "zur Gewissheit ist echter Nutzerkontakt, nicht Weiterentwicklung im Alleingang."
)

out = "/Users/mathiaskunze/Downloads/ShortFlow_Marktbericht_Mai2026.pdf"
pdf.output(out)
print(f"Fertig: {out}")
