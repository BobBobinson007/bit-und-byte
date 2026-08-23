#!/usr/bin/env python3
"""
Bit & Byte – GitHub Pages Article Generator (Dark Kachel-Design)
Erzeugt die HTML-Artikel-Seiten mit allen Quellen für die GitHub-Pages-Seite.
"""

import os
import json
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
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1c1c1e;
            color: #f0f0f5;
            line-height: 1.6;
        }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        .back {{
            margin-bottom: 1rem;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            color: #0f9d58;
            text-decoration: none;
            font-size: 0.9rem;
            padding: 0.4rem 0.8rem;
            background: #26262a;
            border-radius: 8px;
            transition: background 0.2s;
        }}
        .back:hover {{ background: #30303a; }}
        .article {{
            background: #26262a;
            border-radius: 14px;
            padding: 2rem 2.5rem;
            box-shadow: 0 4px 24px rgba(0,0,0,0.3);
            border-left: 4px solid #0f9d58;
        }}
        .article h1 {{ font-size: 2rem; margin-bottom: 0.3rem; color: #fff; }}
        .article .meta {{
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #333;
        }}
        .article h2 {{ margin: 1.5rem 0 0.8rem; font-size: 1.3rem; color: #0f9d58; }}
        .article h3 {{ margin: 1.2rem 0 0.5rem; font-size: 1.1rem; color: #c0c0cc; }}
        .article p {{ margin-bottom: 1rem; color: #d0d0dd; }}
        .article ul {{ margin: 0.8rem 0 0.8rem 1.5rem; color: #d0d0dd; }}
        .article li {{ margin-bottom: 0.3rem; }}
        .article blockquote {{
            border-left: 3px solid #0f9d58;
            padding-left: 1rem;
            margin: 1rem 0;
            color: #a0a0aa;
            font-style: italic;
        }}
        .cat-badge {{
            display: inline-block;
            padding: 0.15rem 0.7rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #fff;
        }}
        .article .sources {{
            margin-top: 2rem;
            padding: 1.2rem;
            background: #30303a;
            border-radius: 10px;
        }}
        .article .sources h4 {{ font-size: 0.9rem; color: #0f9d58; margin-bottom: 0.8rem; }}
        .article .source-item {{
            font-size: 0.85rem;
            padding: 0.4rem 0;
            border-bottom: 1px solid #333;
            color: #aaa;
        }}
        .article .source-item:last-child {{ border-bottom: none; }}
        .article .source-item a {{ color: #0f9d58; text-decoration: none; }}
        .article .source-item a:hover {{ text-decoration: underline; }}
        .article .source-item .access {{ color: #666; font-size: 0.8rem; }}
        .article .media-links {{ margin: 1rem 0; display: flex; gap: 0.5rem; flex-wrap: wrap; }}
        .media-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.35rem 0.8rem;
            border-radius: 8px;
            color: #64b5f6;
            text-decoration: none;
            font-size: 0.85rem;
            background: #1a2a3a;
            transition: background 0.2s;
        }}
        .media-link:hover {{ background: #2a3a4a; }}
        .pdf-download {{
            text-align: center;
            padding: 1.5rem;
            background: #26262a;
            border-radius: 14px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.3);
            margin-top: 2rem;
            border-left: 4px solid #0f9d58;
        }}
        .pdf-download a {{
            display: inline-block;
            padding: 0.8rem 2rem;
            background: #0f9d58;
            color: #fff;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .pdf-download a:hover {{ background: #0d7a44; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(15,157,88,0.4); }}
        img {{
            max-width: 100%;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.3);
        }}
        footer {{
            text-align: center;
            padding: 2rem 0;
            color: #666;
            font-size: 0.85rem;
            margin-top: 2rem;
            border-top: 1px solid #333;
        }}
        @media (max-width: 640px) {{
            .container {{ padding: 1rem; }}
            .article {{ padding: 1.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back">← Zurück zur Übersicht</a>
'''

HTML_FOOT = '''
        <div class="pdf-download">
            <a href="{pdf_url}" target="_blank">📄 PDF dieser Ausgabe herunterladen</a>
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
        self.issue_id = issue_id
        self.issue_title = issue_title
        self.issue_date = issue_date
        self.articles = articles
        self.pdf_filename = pdf_filename

    def _escape_html(self, text):
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        return text

    def _format_body(self, body):
        lines = body.split('\n')
        html_parts = []
        in_list = False
        in_blockquote = False

        for line in lines:
            if line.startswith('## '):
                if in_list: html_parts.append('</ul>'); in_list = False
                if in_blockquote: html_parts.append('</blockquote>'); in_blockquote = False
                html_parts.append(f'<h3>{self._escape_html(line[3:])}</h3>')
            elif line.startswith('### '):
                if in_list: html_parts.append('</ul>'); in_list = False
                if in_blockquote: html_parts.append('</blockquote>'); in_blockquote = False
                html_parts.append(f'<h4>{self._escape_html(line[4:])}</h4>')
            elif line.startswith('> '):
                if not in_blockquote:
                    html_parts.append('<blockquote>')
                    in_blockquote = True
                html_parts.append(self._escape_html(line[2:]) + '<br>')
            elif line.startswith('- ') or line.startswith('* '):
                if not in_list:
                    html_parts.append('<ul>')
                    in_list = True
                html_parts.append(f'<li>{self._escape_html(line[2:])}</li>')
            elif line.strip() == '':
                if in_list: html_parts.append('</ul>'); in_list = False
                if in_blockquote: html_parts.append('</blockquote>'); in_blockquote = False
                continue
            else:
                if in_list: html_parts.append('</ul>'); in_list = False
                if in_blockquote: html_parts.append('</blockquote>'); in_blockquote = False
                text = self._escape_html(line)
                html_parts.append(f'<p>{text}</p>')

        if in_list: html_parts.append('</ul>')
        if in_blockquote: html_parts.append('</blockquote>')
        return '\n'.join(html_parts)

    def _cat_color(self, category):
        """Kategorie-Farbe als CSS-Hex."""
        colors = {
            'ki': '0078c8', 'github': 'c87800', 'distro': 'c85000',
            'hack': 'c81e1e', 'sicherheit': '009696', 'wie funktioniert': '7850c8',
            'docker': '0096c8', 'ios': '646464', 'mythen': 'c86400',
            'messen': '960096', 'weltall': '0050b4', 'studie': 'b43c78',
            'deep': '0f9d58', 'editorial': '0f9d58',
        }
        for key, color in colors.items():
            if key in category.lower():
                return color
        return '0f9d58'

    def generate(self):
        pdf_url = f"../../pdf/{self.pdf_filename}" if self.issue_id != 'Hello-World' else f"pdf/{self.pdf_filename}"
        parts = [HTML_HEAD.format(issue_title=self._escape_html(self.issue_title))]

        parts.append(f'''
        <div class="article">
            <h1>{self._escape_html(self.issue_title)}</h1>
            <div class="meta">Ausgabe {self._escape_html(self.issue_id)} · {self.issue_date}</div>
        ''')

        for i, article in enumerate(self.articles):
            cat_color = self._cat_color(article.get('category', ''))
            parts.append(f'<div style="margin:1.5rem 0;padding:1.5rem;background:#30303a;border-radius:10px;border-left:3px solid #{cat_color};">')

            if article.get('category'):
                parts.append(f'<span class="cat-badge" style="background:#{cat_color};">{self._escape_html(article["category"])}</span>')
            parts.append(f'<h2 style="margin:0.3rem 0 0.8rem;color:#fff;">{self._escape_html(article["title"])}</h2>')

            # Bild
            if article.get('image_url'):
                img_url = article['image_url']
                img_caption = self._escape_html(article.get('image_caption', ''))
                parts.append(f'<img src="{img_url}" alt="{img_caption}">')
                if article.get('image_source'):
                    parts.append(f'<p style="font-size:0.8rem;color:#666;margin-top:-0.5rem;">Quelle: {self._escape_html(article["image_source"])}</p>')

            # Medien-Links
            if article.get('media'):
                parts.append('<div class="media-links">')
                for m in article['media']:
                    icon = '🎬' if m['type'] == 'video' else '🎙️'
                    channel = f' · {self._escape_html(m.get("channel", ""))}' if m.get('channel') else ''
                    parts.append(f'<a href="{m["url"]}" class="media-link" target="_blank">{icon} {self._escape_html(m["title"])}{channel}</a>')
                parts.append('</div>')

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

        parts.append('</div>')  # close article div

        depth_prefix = '' if self.pdf_filename.startswith('Bit_Byte') else '../../'
        pdf_url = f"{depth_prefix}pdf/{self.pdf_filename}"
        parts.append(HTML_FOOT.format(
            pdf_url=pdf_url,
            issue_id=self._escape_html(self.issue_id),
            issue_date=self.issue_date
        ))

        return '\n'.join(parts)

    def save(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.join(ISSUES_DIR, self.issue_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'index.html')
        html = self.generate()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'✅ Artikel-Seite erstellt: {output_path}')
        return output_path


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
    print(gen.generate()[:500])
    print(f'\n... (HTML-Länge: {len(gen.generate())} Zeichen)')