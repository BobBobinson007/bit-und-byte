#!/usr/bin/env python3
"""
Bit & Byte – GitHub Pages Article Generator
Erzeugt die HTML-Artikel-Seiten mit allen Quellen für die GitHub-Pages-Seite.

Jeder Artikel bekommt:
- Sauberes, minimalistisches HTML
- Alle Quellen (URLs, Zugriffsdatum, Zitat)
- Optional: eingebettete Videos, Podcast-Empfehlungen
- Keine KI-generierten Bilder – nur echte Bilder aus dem Internet
"""

import os
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
ISSUES_DIR = os.path.join(DOCS_DIR, 'issues')

HTML_HEAD = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bit & Byte – {issue_title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #1a1a1a; line-height: 1.6; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        .back {{ margin-bottom: 1rem; display: inline-block; color: #00c853; text-decoration: none; font-size: 0.9rem; }}
        .back:hover {{ text-decoration: underline; }}
        .issue {{ background: #fff; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        .issue h1 {{ font-size: 2rem; margin-bottom: 0.3rem; }}
        .issue .meta {{ color: #999; font-size: 0.9rem; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #00c853; }}
        .article {{ margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid #eee; }}
        .article:last-child {{ border-bottom: none; margin-bottom: 0; }}
        .article .cat-badge {{ display: inline-block; background: #e8f5e9; color: #2e7d32; padding: 0.15rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem; }}
        .article h2 {{ font-size: 1.3rem; margin-bottom: 0.5rem; color: #333; }}
        .article p {{ margin-bottom: 0.8rem; color: #444; }}
        .article .sources {{ margin-top: 1rem; padding: 0.8rem; background: #f9f9f9; border-radius: 8px; }}
        .article .sources h4 {{ font-size: 0.9rem; color: #666; margin-bottom: 0.5rem; }}
        .article .source-item {{ font-size: 0.85rem; padding: 0.3rem 0; }}
        .article .source-item a {{ color: #00c853; text-decoration: none; }}
        .article .source-item a:hover {{ text-decoration: underline; }}
        .article .source-item .access {{ color: #aaa; font-size: 0.8rem; }}
        .article .media-link {{ display: inline-block; background: #e3f2fd; padding: 0.3rem 0.7rem; border-radius: 6px; color: #1565c0; text-decoration: none; font-size: 0.85rem; margin: 0.2rem; }}
        .article .media-link:hover {{ background: #bbdefb; }}
        .pdf-download {{ text-align: center; padding: 1.5rem; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-top: 2rem; }}
        .pdf-download a {{ display: inline-block; padding: 0.8rem 2rem; background: #00c853; color: #fff; border-radius: 8px; text-decoration: none; font-weight: 600; }}
        .pdf-download a:hover {{ background: #00a844; }}
        footer {{ text-align: center; padding: 2rem 0; color: #999; font-size: 0.85rem; }}
        img {{ max-width: 100%; border-radius: 8px; margin: 1rem 0; }}
        blockquote {{ border-left: 3px solid #00c853; padding-left: 1rem; margin: 1rem 0; color: #555; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back">← Zurück zur Übersicht</a>
'''

HTML_FOOT = '''
        <div class="pdf-download">
            <a href="/pdf/{pdf_filename}" target="_blank">📄 PDF dieser Ausgabe herunterladen</a>
        </div>
        <footer>
            Bit & Byte · Ausgabe {issue_id} · Quellen geprüft am {issue_date}
        </footer>
    </div>
</body>
</html>'''


class ArticlePageGenerator:
    """Generiert die HTML-Seiten für jede Ausgabe."""

    def __init__(self, issue_id, issue_title, issue_date, articles, pdf_filename):
        """
        articles: Liste von Dictionaries mit:
            - category (str)
            - title (str)
            - body (str, Markdown-artig)
            - sources (list of dicts: url, title, accessed, citation)
            - media (list of dicts: type, url, title, channel) – optional
            - image_url (str) – optional, echte Bilder-URLs
        """
        self.issue_id = issue_id
        self.issue_title = issue_title
        self.issue_date = issue_date
        self.articles = articles
        self.pdf_filename = pdf_filename

    def _escape_html(self, text):
        """Einfaches HTML-Escaping."""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        return text

    def _format_body(self, body):
        """Wandelt einfachen Text mit Markdown-Elementen in HTML um."""
        lines = body.split('\n')
        html_parts = []
        in_list = False
        in_blockquote = False

        for line in lines:
            # Überschriften (simple detection)
            if line.startswith('## '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                html_parts.append(f'<h3>{self._escape_html(line[3:])}</h3>')
            elif line.startswith('### '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                html_parts.append(f'<h4>{self._escape_html(line[4:])}</h4>')
            # Blockquote
            elif line.startswith('> '):
                if not in_blockquote:
                    html_parts.append('<blockquote>')
                    in_blockquote = True
                html_parts.append(self._escape_html(line[2:]) + '<br>')
            # Listen
            elif line.startswith('- ') or line.startswith('* '):
                if not in_list:
                    html_parts.append('<ul>')
                    in_list = True
                html_parts.append(f'<li>{self._escape_html(line[2:])}</li>')
            # Leerzeile
            elif line.strip() == '':
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                if in_blockquote:
                    html_parts.append('</blockquote>')
                    in_blockquote = False
                continue
            # Normaler Paragraph
            else:
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                if in_blockquote:
                    html_parts.append('</blockquote>')
                    in_blockquote = False
                # Inline-Links erkennen
                text = self._escape_html(line)
                html_parts.append(f'<p>{text}</p>')

        if in_list:
            html_parts.append('</ul>')
        if in_blockquote:
            html_parts.append('</blockquote>')

        return '\n'.join(html_parts)

    def generate(self):
        """Generiert die komplette HTML-Seite."""
        parts = [HTML_HEAD.format(issue_title=self._escape_html(self.issue_title))]

        # Issue-Header
        parts.append(f'''
        <div class="issue">
            <h1>{self._escape_html(self.issue_title)}</h1>
            <div class="meta">Ausgabe {self.issue_id} · {self.issue_date}</div>
        ''')

        # Artikel
        for i, article in enumerate(self.articles):
            parts.append('<div class="article">')
            if article.get('category'):
                parts.append(f'<span class="cat-badge">{self._escape_html(article["category"])}</span>')
            parts.append(f'<h2>{self._escape_html(article["title"])}</h2>')

            # Optional: Bild
            if article.get('image_url'):
                img_url = article['image_url']
                img_caption = self._escape_html(article.get('image_caption', ''))
                parts.append(f'<img src="{img_url}" alt="{img_caption}">')
                if article.get('image_source'):
                    parts.append(f'<p style="font-size:0.8rem;color:#999;margin-top:-0.5rem;">Quelle: {self._escape_html(article["image_source"])}</p>')

            # Optional: Medien-Links
            if article.get('media'):
                parts.append('<p>')
                for m in article['media']:
                    icon = '🎬' if m['type'] == 'video' else '🎙️'
                    channel = f' · {self._escape_html(m.get("channel", ""))}' if m.get('channel') else ''
                    parts.append(f'<a href="{m["url"]}" class="media-link" target="_blank">{icon} {self._escape_html(m["title"])}{channel}</a> ')
                parts.append('</p>')

            # Body
            parts.append(self._format_body(article['body']))

            # Quellen
            if article.get('sources'):
                parts.append('<div class="sources">')
                parts.append('<h4>📚 Quellen</h4>')
                for j, src in enumerate(article['sources']):
                    src_title = self._escape_html(src.get('title', src['url']))
                    accessed = f'<span class="access">(abgerufen: {src.get("accessed", self.issue_date)})</span>'
                    citation = ''
                    if src.get('citation'):
                        citation = f'<br><span style="color:#888;font-size:0.8rem;">{self._escape_html(src["citation"])}</span>'
                    parts.append(f'<div class="source-item">[{j+1}] <a href="{src["url"]}" target="_blank">{src_title}</a> {accessed}{citation}</div>')
                parts.append('</div>')

            parts.append('</div>')

        parts.append('</div>')  # close issue div

        # Footer mit PDF-Download
        parts.append(HTML_FOOT.format(
            pdf_filename=self.pdf_filename,
            issue_id=self._escape_html(self.issue_id),
            issue_date=self.issue_date
        ))

        return '\n'.join(parts)

    def save(self, output_dir=None):
        """Speichert die Seite im docs/issues/ Verzeichnis."""
        if output_dir is None:
            output_dir = os.path.join(ISSUES_DIR, self.issue_id)

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'index.html')
        html = self.generate()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'✅ Artikel-Seite erstellt: {output_path}')
        return output_path


def update_main_index(issues_list):
    """
    Aktualisiert die Haupt-index.html mit der aktuellen Ausgabe.
    issues_list: Liste von Dictionaries mit id, title, date, pdf_filename
    """
    # Das wird von der Pipeline aufgerufen nach jeder neuen Ausgabe
    # Wir modifizieren das #latest-issue Element und die archive-Liste
    print("📝 Main index.html Update wird in der Pipeline durchgeführt.")
    pass


if __name__ == '__main__':
    # Test
    articles = [
        {
            'category': '📰 Editorial',
            'title': 'Willkommen bei Bit & Byte!',
            'body': 'Herzlich willkommen zur ersten Ausgabe.\n\nDies ist ein Test.',
            'sources': [
                {'url': 'https://www.tagesschau.de/', 'title': 'tagesschau.de', 'accessed': 'August 2026', 'citation': 'Beispielquelle'}
            ]
        }
    ]
    gen = ArticlePageGenerator(
        issue_id='2026-W34',
        issue_title='Hello World!',
        issue_date='August 2026',
        articles=articles,
        pdf_filename='Bit_Byte_Woche_Hello_World.pdf'
    )
    html = gen.generate()
    print(html[:500])  # Zeigt die ersten 500 Zeichen
    print(f'\n... (HTML-Länge: {len(html)} Zeichen)')
    print(f'\nAusgabe-Verzeichnis: {ISSUES_DIR}/2026-W34/')