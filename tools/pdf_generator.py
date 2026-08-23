#!/usr/bin/env python3
"""
Bit & Byte – PDF Generator
Erzeugt eine minimalistische, saubere PDF-Zeitung mit fpdf2.
Keine Quellen im PDF – nur auf der GitHub-Pages-Seite.
"""

from fpdf import FPDF
from datetime import datetime
import os
import textwrap

class BitBytePDF(FPDF):
    def __init__(self, issue_title, issue_date, articles, output_path):
        super().__init__('P', 'mm', 'A4')
        self.issue_title = issue_title
        self.issue_date = issue_date
        self.articles = articles  # list of dicts: {title, body, category}
        self.output_path = output_path
        self._setup_fonts()

    def _setup_fonts(self):
        """Dejavu wird mit fpdf2 mitgeliefert – perfekt für Minimalismus."""
        self.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        self.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')

    def header(self):
        if self.page_no() == 1:
            return  # Custom first-page header
        self.set_font('DejaVu', 'B', 8)
        self.set_text_color(180, 180, 180)
        self.cell(0, 5, f'Bit & Byte – {self.issue_title}', align='L')
        self.cell(0, 5, f'{self.issue_date}', align='R', new_x="LMARGIN", new_y="NEXT")
        self.line(10, 15, 200, 15)
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 7)
        self.set_text_color(180, 180, 180)
        self.cell(0, 10, f'Seite {self.page_no()}/{{nb}}', align='C')

    def generate(self):
        self.alias_nb_pages()
        self.set_auto_page_break(True, 20)

        # ========== TITELSEITE ==========
        self.add_page()
        self.ln(40)
        self.set_font('DejaVu', 'B', 36)
        self.set_text_color(0, 200, 83)
        self.cell(0, 15, 'Bit & Byte', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.set_font('DejaVu', '', 14)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, self.issue_title, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(3)
        self.set_font('DejaVu', '', 11)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f'Ausgabe: {self.issue_date}', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)
        # Green divider
        self.set_draw_color(0, 200, 83)
        self.set_line_width(0.5)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(15)

        # Kategorien-Übersicht auf der Titelseite
        self.set_font('DejaVu', '', 10)
        self.set_text_color(100, 100, 100)
        categories = [a['category'] for a in self.articles if a.get('category')]
        col1 = categories[::2]
        col2 = categories[1::2]
        y_start = self.get_y()
        x_left = 30
        x_right = 110
        self.set_font('DejaVu', '', 9)
        for i in range(max(len(col1), len(col2))):
            self.set_xy(x_left, y_start + i * 6)
            if i < len(col1):
                self.cell(80, 6, f'• {col1[i]}')
            self.set_xy(x_right, y_start + i * 6)
            if i < len(col2):
                self.cell(80, 6, f'• {col2[i]}')

        # ========== ARTIKELSEITEN ==========
        for article in self.articles:
            self.add_page()
            self.render_article(article)

        self.output(self.output_path)
        return self.output_path

    def render_article(self, article):
        title = article.get('title', '')
        body = article.get('body', '')
        category = article.get('category', '')

        # Kategorie-Badge
        if category:
            self.set_font('DejaVu', 'B', 9)
            self.set_text_color(0, 200, 83)
            self.cell(0, 7, f'[{category}]', new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

        # Titel
        self.set_font('DejaVu', 'B', 16)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 8, title)
        self.ln(3)

        # Dünne Linie unter Titel
        self.set_draw_color(0, 200, 83)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

        # Body
        self.set_font('DejaVu', '', 10)
        self.set_text_color(60, 60, 60)

        for paragraph in body.split('\n\n'):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            # Wrap text manually for better control
            wrapped = textwrap.fill(paragraph, width=85)
            self.multi_cell(0, 5.5, wrapped)
            self.ln(2)


def create_hello_world_pdf():
    """Erzeugt die Hello-World-Beispiel-PDF."""
    articles = [
        {
            'title': '👋 Willkommen bei Bit & Byte!',
            'category': '📰 Editorial',
            'body': (
                'Herzlich willkommen zur ersten Ausgabe von Bit & Byte – '
                'deiner wöchentlichen Tech-Zeitung!\n\n'
                'Jeden Samstag um 8:00 Uhr erscheint eine neue Ausgabe mit '
                'den spannendsten Themen aus der Welt der Technologie. Von '
                'KI-Modellen über Linux-Distributionen bis hin zu '
                'Sicherheitslücken – wir haben alles im Blick.\n\n'
                'Unser Versprechen: Keine Fake News. Jeder Artikel wird '
                'sorgfältig recherchiert. Alle Quellen findest du auf der '
                'GitHub-Pages-Seite – im PDF selbst stehen nur die Artikel, '
                'damit du sie sauber lesen und ausdrucken kannst.\n\n'
                'Viel Spaß mit Bit & Byte! 🚀'
            )
        },
        {
            'title': '🤖 KI-Modelle der Woche',
            'category': '🤖 KI-Modelle',
            'body': (
                'Die Woche brachte wieder einige spannende Entwicklungen im '
                'KI-Bereich. Während große Labs wie OpenAI, Google DeepMind '
                'und Meta weiter an ihren Modellen arbeiten, entstehen auch '
                'im Open-Source-Bereich interessante Projekte.\n\n'
                'Highlights: Neue Optimierungen bei lokalen LLMs, Fortschritte '
                'bei multimodalen Modellen und spannende Papers zu '
                'Effizienzsteigerungen im Training.\n\n'
                '(Dies ist ein Beispieltext – die echten Ausgaben enthalten '
                'aktuelle, recherchierte Inhalte mit Quellenangaben auf der '
                'Webseite.)'
            )
        },
        {
            'title': '🐧 Distro des Monats: Ubuntu 24.04 LTS',
            'category': '🐧 Distro des Monats',
            'body': (
                'Ubuntu 24.04 LTS (»Noble Numbat«) ist seit April 2024 '
                'verfügbar und bringt viele Verbesserungen mit. Der GNOME-Desktop '
                'wurde auf Version 46 aktualisiert, der Linux-Kernel auf 6.8.\n\n'
                'Besonders hervorzuheben: Die verbesserte Unterstützung für '
                'Fraktionen (Wayland), ein neues Firmware-Update-Tool (Firmware '
                'Updater 1.0) und die Integration von TPM-basierter '
                'Festplattenverschlüsselung.\n\n'
                'Mit 12 Jahren Support ist Ubuntu 24.04 LTS eine der '
                'langlebigsten Distributionen und eignet sich perfekt für '
                'Server und Workstations.\n\n'
                '(Dies ist ein Beispieltext.)'
            )
        },
        {
            'title': '🔒 Sicherheitslücke einfach erklärt: CVE-2024-xxx',
            'category': '🔒 Sicherheitslücke',
            'body': (
                'Jede Woche werden Dutzende Sicherheitslücken gemeldet. '
                'Hier erklären wir eine davon so einfach, dass jeder sie '
                'versteht.\n\n'
                'Stell dir vor, du hast ein Schloss an deiner Haustür. '
                'Eine Sicherheitslücke ist wie ein Trick, mit dem jemand '
                'dieses Schloss öffnen kann, ohne den richtigen Schlüssel '
                'zu haben.\n\n'
                'In dieser Woche geht es um eine Schwachstelle in XYZ, '
                'die es Angreifern ermöglicht, Code aus der Ferne '
                'auszuführen. Die gute Nachricht: Der Hersteller hat '
                'bereits einen Patch veröffentlicht.\n\n'
                '(Dies ist ein Beispieltext.)'
            )
        },
    ]

    pdf = BitBytePDF(
        issue_title='Hello World! 👋',
        issue_date='August 2026 · Beispielausgabe',
        articles=articles,
        output_path='/home/ansible/bit-und-byte/docs/pdf/Bit_Byte_Woche_Hello_World.pdf'
    )
    pdf.generate()
    print(f'✅ PDF erstellt: {pdf.output_path}')
    return pdf.output_path


if __name__ == '__main__':
    create_hello_world_pdf()