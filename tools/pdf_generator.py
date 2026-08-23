#!/usr/bin/env python3
"""
Bit & Byte – PDF Generator (Kachel-Design)
Erzeugt eine minimalistische, KACHEL-basierte PDF-Zeitung mit fpdf2.
Keine Quellen im PDF – nur auf der GitHub-Pages-Seite.

Design: Kacheln (Cards) pro Artikel, hoher Kontrast, grüne Akzente
"""

from fpdf import FPDF
from datetime import datetime
import os
import textwrap

# ── Farbpalette ──────────────────────────────────────────────
GREEN_PRIMARY   = (15, 157, 88)    # Kräftiges Grün
GREEN_DARK      = (10, 110, 60)    # Dunkelgrün
GREEN_LIGHT     = (220, 245, 230)  # Hellgrün (Hintergrund)
DARK_BG         = (28, 28, 30)     # Fast-Schwarz
DARK_CARD       = (38, 38, 42)     # Karten-Hintergrund
DARK_SECONDARY  = (48, 48, 52)     # Leicht heller
TEXT_WHITE       = (240, 240, 245) # Heller Text
TEXT_MUTED       = (160, 160, 170) # Gedämpfter Text
CAT_COLORS = {
    'KI': (0, 120, 200),
    'GitHub': (200, 120, 0),
    'Distro': (200, 80, 0),
    'Hack': (200, 30, 30),
    'Sicherheit': (0, 150, 150),
    'Wie funktioniert': (120, 80, 200),
    'Docker': (0, 150, 200),
    'iOS': (100, 100, 100),
    'Mythen': (200, 100, 0),
    'Messen': (150, 0, 150),
    'Weltall': (0, 80, 180),
    'Studie': (180, 60, 120),
    'Deep Dive': (15, 157, 88),
    'Editorial': (80, 80, 80),
}

def get_cat_color(category):
    """Wählt Farbe basierend auf Kategorie-Name."""
    for key, color in CAT_COLORS.items():
        if key.lower() in category.lower():
            return color
    return GREEN_PRIMARY  # Fallback


class BitBytePDF(FPDF):
    def __init__(self, issue_title, issue_date, articles, output_path):
        super().__init__('P', 'mm', 'A4')
        self.issue_title = issue_title
        self.issue_date = issue_date
        self.articles = articles
        self.output_path = output_path
        self._setup_fonts()

    def _setup_fonts(self):
        self.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        self.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')

    def header(self):
        pass  # Custom per page

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 7)
        self.set_text_color(*TEXT_MUTED)
        self.cell(0, 10, f'Bit & Byte – {self.issue_title} | Seite {self.page_no()}/{{nb}}', align='C')

    def _draw_category_badge(self, category, x, y, w):
        """Kategorie-Badge als farbigen Kasten."""
        color = get_cat_color(category)
        self.set_fill_color(*color)
        self.set_draw_color(*color)
        badge_w = self.get_string_width(category) + 6
        self.rect(x, y, min(badge_w, w - 4), 5.5, style='F')
        self.set_xy(x + 3, y + 0.5)
        self.set_font('DejaVu', 'B', 7)
        self.set_text_color(255, 255, 255)
        self.cell(min(badge_w - 6, w - 10), 4.5, category[:30])
        return y + 7

    def _draw_card_header(self, title, category, x, y, w):
        """Zeichnet den oberen Teil einer Karte mit Badge + Titel."""
        y = self._draw_category_badge(category, x + 4, y + 3, w)

        # Titel
        self.set_xy(x + 4, y + 2)
        self.set_font('DejaVu', 'B', 12)
        self.set_text_color(*TEXT_WHITE)
        # Titel wrappen
        wrapped = textwrap.fill(title, width=55)
        self.multi_cell(w - 8, 6, wrapped)
        return self.get_y()

    def generate(self):
        self.alias_nb_pages()
        self.set_auto_page_break(True, 20)

        # ═══════════════════ TITELSEITE ═══════════════════════
        self.add_page()
        # Hintergrund – dunkel
        self.set_fill_color(*DARK_BG)
        self.rect(0, 0, 210, 297, style='F')

        # Header-Linie oben (grün)
        self.set_fill_color(*GREEN_PRIMARY)
        self.rect(0, 0, 210, 3, style='F')

        # Titel
        self.ln(55)
        self.set_font('DejaVu', 'B', 44)
        self.set_text_color(*GREEN_PRIMARY)
        self.cell(0, 18, 'Bit & Byte', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_font('DejaVu', '', 10)
        self.set_text_color(*TEXT_MUTED)
        self.cell(0, 8, 'Wöchentliche Tech-Zeitung', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(15)

        # Ausgabe-Box
        card_x = 25
        card_w = 160
        card_y = self.get_y()
        self.set_fill_color(*DARK_CARD)
        self.rect(card_x, card_y, card_w, 30, style='F')
        # Grüner Rand links
        self.set_fill_color(*GREEN_PRIMARY)
        self.rect(card_x, card_y, 3, 30, style='F')

        self.set_xy(card_x + 12, card_y + 5)
        self.set_font('DejaVu', 'B', 13)
        self.set_text_color(*TEXT_WHITE)
        self.cell(0, 7, self.issue_title, new_x="LMARGIN", new_y="NEXT")
        self.set_xy(card_x + 12, card_y + 15)
        self.set_font('DejaVu', '', 9)
        self.set_text_color(*TEXT_MUTED)
        self.cell(0, 7, f'Ausgabe vom {self.issue_date}', new_x="LMARGIN", new_y="NEXT")

        self.set_y(card_y + 40)

        # Kategorie-Leiste (Card-ähnlich)
        cat_y = self.get_y()
        self.set_fill_color(*DARK_CARD)
        self.rect(card_x, cat_y, card_w, 50, style='F')
        self.set_fill_color(*GREEN_DARK)
        self.rect(card_x, cat_y, 3, 50, style='F')

        categories = [a.get('category', '') for a in self.articles if a.get('category')]
        col1 = categories[::2]
        col2 = categories[1::2]

        self.set_xy(card_x + 12, cat_y + 5)
        self.set_font('DejaVu', 'B', 8)
        self.set_text_color(*TEXT_MUTED)
        self.cell(0, 5, 'DIESE AUSGABE:', new_x="LMARGIN", new_y="NEXT")

        self.set_font('DejaVu', '', 8)
        self.set_text_color(*TEXT_WHITE)
        for i in range(max(len(col1), len(col2))):
            if i < len(col1):
                self.set_xy(card_x + 12, cat_y + 12 + i * 6)
                # Badge-Punkt
                self.set_fill_color(*get_cat_color(col1[i]))
                self.circle(self.get_x() + 2, self.get_y() + 2.5, 1.5, style='F')
                self.set_xy(card_x + 18, cat_y + 12 + i * 6)
                self.cell(65, 6, col1[i][:35])
            if i < len(col2):
                self.set_xy(card_x + 85, cat_y + 12 + i * 6)
                self.set_fill_color(*get_cat_color(col2[i]))
                self.circle(self.get_x() + 2, self.get_y() + 2.5, 1.5, style='F')
                self.set_xy(card_x + 91, cat_y + 12 + i * 6)
                self.cell(65, 6, col2[i][:35])

        self.set_y(cat_y + 70)

        # Footer-Text auf Titelseite
        self.set_font('DejaVu', '', 7)
        self.set_text_color(*TEXT_MUTED)
        self.cell(0, 5, 'Quellen auf GitHub: https://github.com/BobBobinson007/bit-und-byte', align='C', new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, 'PDF generiert am ' + datetime.now().strftime('%d.%m.%Y %H:%M UTC'), align='C')

        # ═══════════════════ ARTIKELSEITEN (KACHELN) ══════════════════
        for i, article in enumerate(self.articles):
            self.add_page()
            self.render_article_card(article, i)

        self.output(self.output_path)
        print(f'✅ PDF erstellt: {self.output_path}')
        return self.output_path

    def render_article_card(self, article, idx):
        """Zeichnet einen Artikel als Kachel/Card."""
        title = article.get('title', '')
        body = article.get('body', '')
        category = article.get('category', '')

        # Hintergrund – dunkel
        self.set_fill_color(*DARK_BG)
        self.rect(0, 0, 210, 297, style='F')

        # Grüne Linie oben
        self.set_fill_color(*GREEN_PRIMARY)
        self.rect(0, 0, 210, 2.5, style='F')

        # ─── Kategorie-Leiste ───
        self.set_fill_color(*DARK_SECONDARY)
        self.rect(10, 10, 190, 10, style='F')
        color = get_cat_color(category)
        self.set_fill_color(*color)
        self.rect(10, 10, 4, 10, style='F')

        self.set_xy(20, 12)
        self.set_font('DejaVu', 'B', 8)
        self.set_text_color(*color)
        self.cell(170, 6, f'  {category}', align='L')

        # ─── Artikel-Kachel ───
        card_y = 25
        card_h = 260  # Maximale Höhe, wird dynamisch

        # Kachel-Hintergrund
        self.set_fill_color(*DARK_CARD)
        self.set_draw_color(*DARK_SECONDARY)
        self.rect(10, card_y, 190, card_h, style='F', round_corners=True)
        # Grüner Rand links
        self.set_fill_color(*GREEN_DARK)
        self.rect(10, card_y, 2.5, card_h, style='F')

        # ─── Titel in der Kachel ───
        inner_x = 22
        inner_w = 168

        self.set_xy(inner_x, card_y + 8)
        self.set_font('DejaVu', 'B', 14)
        self.set_text_color(*TEXT_WHITE)
        self.multi_cell(inner_w, 7.5, title)
        current_y = self.get_y() + 2

        # Trennlinie
        self.set_draw_color(*DARK_SECONDARY)
        self.line(inner_x, current_y, inner_x + inner_w - 6, current_y)
        current_y += 5

        # ─── Body in der Kachel ───
        self.set_xy(inner_x, current_y)
        self.set_font('DejaVu', '', 9)
        self.set_text_color(*TEXT_WHITE)

        for paragraph in body.split('\n\n'):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            wrapped = textwrap.fill(paragraph, width=75)
            self.set_x(inner_x)
            self.multi_cell(inner_w - 4, 5, wrapped)
            self.ln(1.5)

            if self.get_y() > 265:
                break

    def circle(self, x, y, r, style=''):
        """Hilfsfunktion für kleine Punkte."""
        self.ellipse(x - r, y - r, r * 2, r * 2, style=style)


def create_hello_world_pdf():
    """Erzeugt die Hello-World-Beispiel-PDF im neuen Kachel-Design."""
    articles = [
        {
            'title': 'Willkommen bei Bit & Byte!',
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
                'Viel Spaß mit Bit & Byte!'
            )
        },
        {
            'title': 'KI-Modelle der Woche',
            'category': '🤖 KI-Modelle',
            'body': (
                'Die Woche brachte wieder einige spannende Entwicklungen im '
                'KI-Bereich. Während große Labs wie OpenAI, Google DeepMind '
                'und Meta weiter an ihren Modellen arbeiten, entstehen auch '
                'im Open-Source-Bereich interessante Projekte.\n\n'
                'Highlights: Neue Optimierungen bei lokalen LLMs, Fortschritte '
                'bei multimodalen Modellen und spannende Papers zu '
                'Effizienzsteigerungen im Training.'
            )
        },
        {
            'title': 'Distro des Monats: Ubuntu 24.04 LTS',
            'category': '🐧 Distro des Monats',
            'body': (
                'Ubuntu 24.04 LTS (»Noble Numbat«) ist seit April 2024 '
                'verfügbar und bringt viele Verbesserungen mit. Der GNOME-Desktop '
                'wurde auf Version 46 aktualisiert, der Linux-Kernel auf 6.8.\n\n'
                'Besonders hervorzuheben: Die verbesserte Unterstützung für '
                'Wayland, ein neues Firmware-Update-Tool und die Integration '
                'von TPM-basierter Festplattenverschlüsselung.\n\n'
                'Mit 12 Jahren Support ist Ubuntu 24.04 LTS eine der '
                'langlebigsten Distributionen.'
            )
        },
        {
            'title': 'Sicherheitslücke einfach erklärt: CVE-2024-xxx',
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
                'auszuführen. Der Hersteller hat bereits einen Patch '
                'veröffentlicht.'
            )
        },
    ]

    pdf = BitBytePDF(
        issue_title='Hello World!',
        issue_date='August 2026 · Beispielausgabe',
        articles=articles,
        output_path='/home/ansible/bit-und-byte/docs/pdf/Bit_Byte_Woche_Hello_World.pdf'
    )
    pdf.generate()
    return pdf.output_path


if __name__ == '__main__':
    create_hello_world_pdf()