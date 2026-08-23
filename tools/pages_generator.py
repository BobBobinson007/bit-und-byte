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
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #fff; color: #1a1a1a; line-height: 1.5; font-size: 15px; }}
        .container {{ max-width: 780px; margin: 0 auto; padding: 1.5rem; }}
        .back {{ margin-bottom: 0.8rem; display: inline-block; color: #228b22; text-decoration: none; font-size: 0.85rem; padding: 0.3rem 0.8rem; background: #f5f5f5; border-radius: 5px; }}
        .back:hover {{ background: #e8e8e8; }}
        .article {{ background: #f8f8fa; border-radius: 8px; padding: 1.5rem 2rem; border: 1px solid #ddd; border-left: 4px solid #228b22; }}
        .article h1 {{ font-size: 1.6rem; color: #000; margin-bottom: 0.2rem; }}
        .article .meta {{ color: #999; font-size: 0.85rem; margin-bottom: 1rem; padding-bottom: 0.8rem; border-bottom: 1px solid #eee; }}
        .article h2 {{ font-size: 1.15rem; color: #228b22; margin: 1.2rem 0 0.5rem; }}
        .article h3 {{ font-size: 1.05rem; color: #333; margin: 1rem 0 0.4rem; }}
        .article p {{ margin-bottom: 0.7rem; color: #333; }}
        .article ul {{ margin: 0.5rem 0 0.5rem 1.3rem; color: #333; }}
        .article li {{ margin-bottom: 0.2rem; }}
        .article blockquote {{ border-left: 3px solid #228b22; padding-left: 0.8rem; margin: 0.8rem 0; color: #666; font-style: italic; }}
        .cat-badge {{ display: inline-block; padding: 0.15rem 0.6rem; border-radius: 3px; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.3rem; color: #fff; }}
        .sources {{ margin-top: 1.5rem; padding: 1rem; background: #f0f0f0; border-radius: 6px; font-size: 0.85rem; }}
        .sources h4 {{ font-size: 0.85rem; color: #228b22; margin-bottom: 0.5rem; }}
        .source-item {{ padding: 0.3rem 0; border-bottom: 1px solid #e0e0e0; color: #888; }}
        .source-item:last-child {{ border-bottom: none; }}
        .source-item a {{ color: #228b22; text-decoration: none; }}
        .source-item a:hover {{ text-decoration: underline; }}
        .source-item .access {{ color: #aaa; font-size: 0.8rem; }}
        .media-links {{ margin: 0.8rem 0; display: flex; gap: 0.4rem; flex-wrap: wrap; }}
        .media-link {{ display: inline-flex; align-items: center; gap: 0.2rem; padding: 0.25rem 0.7rem; border-radius: 4px; color: #1a6dc8; text-decoration: none; font-size: 0.82rem; background: #eef3fa; }}
        .media-link:hover {{ background: #dce6f5; }}
        img {{ max-width: 100%; border-radius: 6px; margin: 0.8rem 0; border: 1px solid #eee; }}
        .pdf-download {{ text-align: center; padding: 1.2rem; background: #f8f8fa; border-radius: 8px; border: 1px solid #ddd; margin-top: 1.5rem; }}
        .pdf-download a {{ display: inline-block; padding: 0.5rem 1.5rem; background: #228b22; color: #fff; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
        .pdf-download a:hover {{ background: #1a6e1a; }}
        footer {{ text-align: center; padding: 1.5rem 0; color: #999; font-size: 0.8rem; margin-top: 1.5rem; border-top: 1px solid #eee; }}
        .article-card {{ margin: 1rem 0; padding: 1.2rem 1.5rem; background: #f8f8fa; border-radius: 8px; border: 1px solid #e0e0e0; border-left: 3px solid #ccc; }}
        @media (max-width: 640px) {{ .container {{ padding: 0.8rem; }} .article {{ padding: 1rem; }} }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back">← Übersicht</a>
'''

HTML_FOOT = '''
        <div class="pdf-download">
            <a href="{pdf_url}" target="_blank">📄 PDF herunterladen</a>
        </div>
        <footer>
            Bit & Byte · Ausgabe {issue_id} · Quellen: {issue_date}
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
            parts.append(f'<div class="article-card" style="border-left-color:#{cat_color};">')

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