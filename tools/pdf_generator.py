#!/usr/bin/env python3
"""
Bit & Byte – PDF Generator (Papiersparendes Kachel-Design)
Weißer Hintergrund, schwarzer Text, kompakt, Kacheln mit dünnen Rahmen.
"""

from fpdf import FPDF
from datetime import datetime
import os
import textwrap

# ── Farbreduzierte Palette ───────────────────────────────────
GREEN       = (34, 139, 34)   # ForestGreen für Akzente
GREEN_LIGHT = (230, 245, 230) # Hellgrün für Card-Hintergrund
DARK_GRAY   = (60, 60, 60)    # Textfarbe (fast schwarz)
GRAY        = (140, 140, 140) # Meta-Infos
LIGHT_GRAY  = (235, 235, 235) # Card-Rahmen/Hintergrund
WHITE       = (255, 255, 255)
BLACK       = (30, 30, 30)

CAT_COLORS = {
    'ki': (0, 90, 180), 'github': (180, 100, 0), 'distro': (180, 70, 0),
    'hack': (180, 20, 20), 'sicherheit': (0, 120, 120), 'wie funktioniert': (100, 60, 180),
    'docker': (0, 120, 180), 'ios': (90, 90, 90), 'mythen': (180, 90, 0),
    'messen': (130, 0, 130), 'weltall': (0, 60, 150), 'studie': (150, 40, 100),
    'deep': (34, 139, 34), 'editorial': (80, 80, 80),
}

def get_cat_color(category):
    for key, color in CAT_COLORS.items():
        if key in category.lower():
            return color
    return GREEN


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
        pass

    def footer(self):
        self.set_y(-12)
        self.set_font('DejaVu', '', 7)
        self.set_text_color(*GRAY)
        self.cell(0, 8, f'Bit & Byte – {self.issue_title} | S. {self.page_no()}/{{nb}}', align='C')

    def _badge_w(self, category):
        return self.get_string_width(category) + 5

    def generate(self):
        self.alias_nb_pages()
        self.set_auto_page_break(True, 15)
        self.set_margins(12, 10, 12)

        # ═══════════════ TITELSEITE ═══════════════════════════
        self.add_page()
        self.set_fill_color(*WHITE)
        self.rect(0, 0, 210, 297, style='F')

        # Grüner Strich oben
        self.set_fill_color(*GREEN)
        self.rect(0, 0, 210, 2.5, style='F')

        self.ln(30)

        # Titel
        self.set_font('DejaVu', 'B', 32)
        self.set_text_color(*BLACK)
        self.cell(0, 14, 'Bit & Byte', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_font('DejaVu', '', 10)
        self.set_text_color(*GRAY)
        self.cell(0, 6, 'Wöchentliche Tech-Zeitung', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_draw_color(*GREEN)
        self.set_line_width(0.3)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(8)

        # Ausgabe-Kachel
        cx, cw = 25, 160
        self.set_fill_color(*LIGHT_GRAY)
        self.set_draw_color(*GREEN)
        self.rect(cx, self.get_y(), cw, 22, style='DF')

        self.set_xy(cx + 10, self.get_y() + 4)
        self.set_font('DejaVu', 'B', 13)
        self.set_text_color(*BLACK)
        self.cell(140, 6, self.issue_title, new_x="LMARGIN", new_y="NEXT")
        self.set_xy(cx + 10, self.get_y() + 4)
        self.set_font('DejaVu', '', 9)
        self.set_text_color(*GRAY)
        self.cell(140, 6, f'Erschienen: {self.issue_date}', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

        self.set_y(self.get_y() + 3)

        # Kategorien (kompakt, 2-spaltig)
        categories = [a.get('category', '') for a in self.articles if a.get('category')]
        col1 = categories[::2]
        col2 = categories[1::2]

        self.set_font('DejaVu', 'B', 8)
        self.set_text_color(*GRAY)
        self.cell(0, 5, 'THEMEN DIESER AUSGABE:', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        self.set_font('DejaVu', '', 8.5)
        max_rows = max(len(col1), len(col2))
        for i in range(max_rows):
            y = self.get_y()
            if i < len(col1):
                self.set_fill_color(*get_cat_color(col1[i]))
                self.rect(25, y + 1, 3, 5, style='F')
                self.set_xy(31, y)
                self.set_text_color(*DARK_GRAY)
                self.cell(75, 7, col1[i][:40])
            if i < len(col2):
                self.set_fill_color(*get_cat_color(col2[i]))
                self.rect(105, y + 1, 3, 5, style='F')
                self.set_xy(111, y)
                self.set_text_color(*DARK_GRAY)
                self.cell(75, 7, col2[i][:40])
            self.set_y(y + 6)

        self.ln(8)
        self.set_font('DejaVu', '', 7)
        self.set_text_color(*GRAY)
        self.cell(0, 4, 'Quellen: https://bobbobinson007.github.io/bit-und-byte/', align='C')

        # ═══════════════ ARTIKEL-KACHELN ══════════════════════
        for article in self.articles:
            self.add_page()
            self.render_card(article)

        self.output(self.output_path)
        print(f'✅ PDF erstellt: {self.output_path} ({os.path.getsize(self.output_path)/1024:.1f} KB)')
        return self.output_path

    def render_card(self, article):
        title = article.get('title', '')
        body = article.get('body', '')
        category = article.get('category', '')

        # Weißer Hintergrund
        self.set_fill_color(*WHITE)
        self.rect(0, 0, 210, 297, style='F')

        # Grüner Strich oben
        self.set_fill_color(*GREEN)
        self.rect(0, 0, 210, 2, style='F')

        # ─── Kategorie-Badge oben ───
        color = get_cat_color(category)
        self.set_fill_color(*color)
        badge_w = min(self._badge_w(category) + 6, 80)
        self.rect(12, 8, badge_w, 6, style='F')
        self.set_xy(15, 8.5)
        self.set_font('DejaVu', 'B', 7)
        self.set_text_color(*WHITE)
        self.cell(badge_w - 6, 5, category[:40])

        # ─── Kachel-Card ───
        card_x = 12
        card_y = 18
        card_w = 186

        # Hintergrund der Kachel
        self.set_fill_color(248, 248, 250)
        self.set_draw_color(210, 210, 215)
        self.rect(card_x, card_y, card_w, 268, style='DF')

        # Grüner Rand links
        self.set_fill_color(*GREEN)
        self.rect(card_x, card_y, 2.5, 268, style='F')

        # ─── Titel ───
        inner_x = card_x + 10
        inner_w = card_w - 16

        self.set_xy(inner_x, card_y + 7)
        self.set_font('DejaVu', 'B', 13)
        self.set_text_color(*BLACK)
        self.multi_cell(inner_w, 7, title)
        y = self.get_y() + 1

        # Dünne Trennlinie
        self.set_draw_color(200, 200, 205)
        self.line(inner_x, y, inner_x + inner_w - 4, y)
        y += 4

        # ─── Body (kompakt, papiersparend) ───
        self.set_xy(inner_x, y)
        self.set_font('DejaVu', '', 9)
        self.set_text_color(*DARK_GRAY)

        for paragraph in body.split('\n\n'):
            para = paragraph.strip()
            if not para:
                continue
            wrapped = textwrap.fill(para, width=80)
            self.set_x(inner_x)
            self.multi_cell(inner_w - 2, 4.8, wrapped)
            self.ln(1.2)
            if self.get_y() > 275:
                break


def create_hello_world_pdf():
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
                'langlebigsten Distributionen und eignet sich perfekt für '
                'Server und Workstations.'
            )
        },
        {
            'title': 'Sicherheitslücke einfach erklärt',
            'category': '🔒 Sicherheitslücke',
            'body': (
                'Jede Woche werden Dutzende Sicherheitslücken gemeldet. '
                'Hier erklären wir eine davon so einfach, dass jeder sie '
                'versteht.\n\n'
                'Stell dir vor, du hast ein Schloss an deiner Haustür. '
                'Eine Sicherheitslücke ist wie ein Trick, mit dem jemand '
                'dieses Schloss öffnen kann, ohne den richtigen Schlüssel '
                'zu haben.\n\n'
                'In dieser Woche geht es um eine Schwachstelle, die es '
                'Angreifern ermöglicht, Code aus der Ferne auszuführen. '
                'Der Hersteller hat bereits einen Patch veröffentlicht.'
            )
        },
    ]

    pdf = BitBytePDF(
        issue_title='Hello World!',
        issue_date='August 2026',
        articles=articles,
        output_path='/home/ansible/bit-und-byte/docs/pdf/Bit_Byte_Woche_Hello_World.pdf'
    )
    pdf.generate()
    return pdf.output_path


if __name__ == '__main__':
    create_hello_world_pdf()