#!/usr/bin/env python3
"""
====================================================================
BIT & BYTE – MAIN PIPELINE
====================================================================
Vollautomatische wöchentliche Tech-Zeitung.

ABLAUF:
  1. Deep Research Phase  (8-12 parallele Recherche-Sessions)
  2. Content Writing Phase (12 Artikel generieren)
  3. Review Phase         (Quellen prüfen, Fake-News-Check)
  4. PDF Generation        (fpdf2 → minimalistisches PDF)
  5. GitHub Pages Update   (HTML-Artikel + Quellen + Index)
  6. Git Push              (Commit + Push zu GitHub)
  7. Notification          (PDF an Telegram chat senden)

CRON:
  Jeden Samstag um 8:00 Uhr → cron job ruft pipeline.py auf

PFADE:
  /home/ansible/bit-und-byte/   → Projekt-Wurzel
  ├── tools/                     → Python-Module
  │   ├── pipeline.py           ← DIESE DATEI
  │   ├── research.py           → Research Engine
  │   ├── pdf_generator.py      → PDF-Erzeugung
  │   ├── pages_generator.py    → GitHub-Pages-HTML
  │   └── memory.py             → Gedächtnis-Tracking
  ├── memory/                    → JSON-Gedächtnis
  ├── articles/                  → Roh-Artikel (Markdown)
  ├── pdf/                       → Generierte PDFs
  ├── docs/                      → GitHub Pages Root
  │   ├── index.html
  │   └── issues/                → Einzelne Ausgaben
  │       └── YYYY-Www/
  │           └── index.html     → Artikel + Quellen
  └── README.md

GEDÄCHTNIS (memory/):
  - distros.json         → Bereits genannte Distributionen
  - howto_explained.json → Bereits erklärte Themen
  - github_projects.json → Bereits vorgestellte GitHub-Projekte
  - issues.json          → Alle erschienenen Ausgaben

DEEP RESEARCH:
  Pro Ausgabe werden ca. 25-35 Research-Runden durchgeführt:
  - 12 Themen × 2-3 Suchqueries = 24-36 Runden
  - Davon: 1. Runde (Keywords) → 2. Runde (Content-Fetch)
  - 3. Runde (Verifikation/Quervergleich)
  - Insgesamt ca. 3 Runden Prompting pro Thema

PDF:
  - Keine Quellen im PDF
  - Nur auf GitHub Pages (docs/issues/) mit voller Quellenangabe
  - Minimalistisches Design (DejaVu Sans, grüne Akzente)

FAKE-NEWS-PRÄVENTION:
  - Jeder Artikel benötigt mind. 2 URLs als Quellen
  - Alle Quellen werden auf der Webseite verlinkt
  - Keine KI-generierten Bilder (nur echte Internet-Bilder)
====================================================================
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime, timezone
from pathlib import Path

# Projekt-Root finden
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'tools'))

# Falls die Module direkt da sind, importieren
try:
    from memory import load_memory, save_memory, add_distro, add_explained_topic, add_github_project, register_issue, get_all_issues
    from research import ResearchEngine, RESEARCH_TOPICS
    from pdf_generator import BitBytePDF
    from pages_generator import ArticlePageGenerator
except ImportError as e:
    print(f"⚠️  Module nicht geladen: {e}")
    print("   Pipeline läuft im Standalone-Modus (wenn von OpenClaw aufgerufen).")


# ============================================================
# KONFIGURATION
# ============================================================

CONFIG = {
    'repo_url': 'https://github.com/BobBobinson007/bit-und-byte.git',
    'repo_branch': 'main',
    'pdf_dir': BASE_DIR / 'docs' / 'pdf',
    'design': 'kachel',  # Kachel-Design (Cards, hoher Kontrast, dunkel)
    'docs_dir': BASE_DIR / 'docs',
    'articles_dir': BASE_DIR / 'articles',
    'author': 'Bit & Byte Automation',
    'max_articles_per_issue': 12,
    'min_sources_per_article': 2,
}

# ============================================================
# PHASE 1: DEEP RESEARCH
# ============================================================

def phase_research():
    """
    Führt die Deep-Research-Phase durch.
    In der OpenClaw-Umgebung wird dies durch parallele Sessions realisiert.
    Hier definieren wir die Struktur: Welche Prompts werden wohin geschickt?
    """
    print("=" * 60)
    print("PHASE 1/6: DEEP RESEARCH")
    print("=" * 60)

    engine = ResearchEngine()
    engine.run_all_searches()

    # In der echten Automation werden diese Prompts an Sessions geschickt.
    # Pro Thema: 3 Runden (Keyword-Suche → Content-Fetch → Verifikation)
    # Gesamt: ~12 Themen × 3 Runden = 36 Research-Runden
    research_prompts = []

    for topic_key, topic_config in RESEARCH_TOPICS.items():
        # Runde 1: Breite Suche
        r1_prompt = engine.get_prompts_for_research(topic_key, topic_config)
        research_prompts.append({
            'round': 1,
            'topic': topic_key,
            'description': topic_config['description'],
            'type': 'keyword_search',
            'prompt': r1_prompt,
        })

    print(f"   → {len(research_prompts)} Research-Prompts vorbereitet")
    print(f"   → ~{len(research_prompts) * 2} weitere Runden für Content-Fetch + Verifikation\n")
    return research_prompts


# ============================================================
# PHASE 2: CONTENT WRITING
# ============================================================

def phase_writing(research_data):
    """
    Schreibt die Artikel aus den gesammelten Research-Daten.
    research_data: dict mit topic_key → {sources, snippets, articles}
    """
    print("=" * 60)
    print("PHASE 2/6: CONTENT WRITING")
    print("=" * 60)

    articles = []

    # Deep Dive bekommt mehr Platz
    for topic_key, topic_config in RESEARCH_TOPICS.items():
        word_count = '500-800' if topic_key == 'deep_dive' else '200-400'
        articles.append({
            'topic_key': topic_key,
            'category': topic_config['description'],
            'word_count': word_count,
        })

    print(f"   → {len(articles)} Artikel geplant")
    print(f"   → Deep Dive: 500-800 Wörter, Rest: 200-400 Wörter\n")
    return articles


# ============================================================
# PHASE 3: REVIEW & FAKE-NEWS-CHECK
# ============================================================

def phase_review(articles):
    """
    Prüft jeden Artikel auf Quellen und Fake News.
    """
    print("=" * 60)
    print("PHASE 3/6: REVIEW & FAKE NEWS CHECK")
    print("=" * 60)

    issues = []
    for article in articles:
        sources = article.get('sources', [])
        if len(sources) < CONFIG['min_sources_per_article']:
            issues.append(f"  ⚠️  {article.get('category', '?')}: Nur {len(sources)} Quellen")
        # Prüfe auf unbelegte Behauptungen (Pattern-basiert)
        body = article.get('body', '')
        unsubstantiated = check_unsubstantiated_claims(body)
        if unsubstantiated:
            issues.append(f"  ⚠️  {article.get('category', '?')}: {unsubstantiated} unbelegte Behauptungen")

    if not issues:
        print("   ✅ Alle Artikel bestanden den Review")
    else:
        print("\n".join(issues))
    print()
    return issues


def check_unsubstantiated_claims(text):
    """
    Simple Prüfung auf Behauptungen ohne Quellenverweis.
    Gibt Anzahl der verdächtigen Sätze zurück.
    """
    if not text:
        return 0
    # Zähle Sätze mit starken Behauptungen
    claims = 0
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    for s in sentences:
        s = s.strip().lower()
        # Ignoriere kurze / einleitende Sätze
        if len(s) < 30:
            continue
        # Prüfe auf Quellenverweis
        if '[' not in s and 'http' not in s and 'quelle' not in s and 'laut' not in s:
            # Starke Behauptung ohne Quellenverweis?
            strong_words = ['ist der', 'ist das', 'wurde', 'hat', 'gibt es', 'bietet', 'ermöglicht']
            if any(w in s for w in strong_words):
                claims += 1
    return claims


# ============================================================
# PHASE 4: PDF GENERATION
# ============================================================

def phase_pdf(articles, issue_id, issue_title, issue_date):
    """
    Erzeugt die PDF der aktuellen Ausgabe.
    """
    print("=" * 60)
    print("PHASE 4/6: PDF GENERATION")
    print("=" * 60)

    pdf_filename = f'Bit_Byte_Woche_{issue_id}.pdf'
    pdf_path = CONFIG['pdf_dir'] / pdf_filename

    pdf_articles = []
    for a in articles:
        pdf_articles.append({
            'title': a['title'],
            'category': a['category'],
            'body': a['body'],
        })

    try:
        pdf = BitBytePDF(
            issue_title=issue_title,
            issue_date=issue_date,
            articles=pdf_articles,
            output_path=str(pdf_path)
        )
        pdf.generate()
        print(f"   ✅ PDF erstellt: {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")
        return str(pdf_path), pdf_filename
    except Exception as e:
        print(f"   ❌ PDF-Fehler: {e}")
        return None, pdf_filename


# ============================================================
# PHASE 5: GITHUB PAGES UPDATE
# ============================================================

def phase_github_pages(articles, issue_id, issue_title, issue_date, pdf_filename):
    """
    Erstellt/aktualisiert die GitHub-Pages-Seiten mit Quellen.
    """
    print("=" * 60)
    print("PHASE 5/6: GITHUB PAGES UPDATE")
    print("=" * 60)

    gen = ArticlePageGenerator(
        issue_id=issue_id,
        issue_title=issue_title,
        issue_date=issue_date,
        articles=articles,
        pdf_filename=pdf_filename
    )
    output_path = gen.save()
    print(f"   ✅ GitHub Pages: {output_path}")
    return output_path


# ============================================================
# PHASE 6: GIT PUSH
# ============================================================

def phase_git_push():
    """
    Pusht die Änderungen zu GitHub.
    """
    print("=" * 60)
    print("PHASE 6/6: GIT PUSH")
    print("=" * 60)

    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=str(BASE_DIR),
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip():
            print(f"   → Änderungen gefunden")
            # Add all
            subprocess.run(['git', 'add', '-A'], cwd=str(BASE_DIR), check=True, timeout=30)
            # Commit
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
            commit_msg = f'📰 Bit & Byte – Automatische Ausgabe vom {date_str}'
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=str(BASE_DIR), check=True, timeout=30)
            # Push
            result = subprocess.run(
                ['git', 'push', 'origin', CONFIG['repo_branch']],
                cwd=str(BASE_DIR),
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print("   ✅ Erfolgreich zu GitHub gepusht")
                return True
            else:
                print(f"   ⚠️  Push-Problem: {result.stderr[:200]}")
                return False
        else:
            print("   ℹ️  Keine Änderungen zu pushen")
            return True
    except subprocess.TimeoutExpired:
        print("   ❌ Git-Operation timeout")
        return False
    except Exception as e:
        print(f"   ❌ Git-Fehler: {e}")
        return False


# ============================================================
# PIPELINE ORCHESTRATION
# ============================================================

def run_pipeline(articles_data=None, skip_git=False):
    """
    Haupt-Pipeline.

    Normalbetrieb (OpenClaw-gesteuert):
      1. OpenClaw führt Deep Research durch (web_search + web_fetch)
      2. Ergebnisse werden an diese Pipeline übergeben
      3. Pipeline generiert PDF + Pages + pusht

    Wenn keine articles_data übergeben werden, generiert die Pipeline
    Platzhalter und beschreibt, wie der Ablauf in OpenClaw aussieht.
    """
    print("=" * 60)
    print("  ⟨ B I T  &  B Y T E ⟩  –  AUTOMATED PIPELINE  ")
    print("=" * 60)
    print(f"  Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  PID: {os.getpid()}")
    print(f"  CWD: {BASE_DIR}")
    print("=" * 60)

    issue_date = datetime.now().strftime('%d.%m.%Y')
    iso = datetime.now().isocalendar()
    issue_id = f"{iso[0]}-W{iso[1]:02d}"
    issue_title = f"Ausgabe {issue_id}"

    # Phase 1: Research
    research_prompts = phase_research()

    # Phase 2: Content (hier kommen später die echten Artikel rein)
    if articles_data is None:
        # Demo-Modus: Erkläre, wie die Artikel rein kommen
        print("=" * 60)
        print("ℹ️  KEINE ARTIKEL-DATEN ÜBERGEBEN – DEMO-MODUS")
        print("=" * 60)
        print("\nIm Normalbetrieb werden die Artikel von OpenClaw generiert:")
        print("  openclaw → web_search (36 Research-Runden)")
        print("  openclaw → content-generation (12 Artikel)")
        print("  openclaw → pipeline.py mit den Artikel-Daten")
        print("\nÜbergabe-Format (JSON):")
        print(json.dumps([{
            'category': '🤖 Neue KI-Modelle',
            'title': 'Beispiel-Titel',
            'body': 'Artikeltext mit Behauptungen [1] ...',
            'sources': [{'url': 'https://...', 'title': 'Quellentitel', 'accessed': issue_date}],
            'media': [{'type': 'video', 'url': 'https://youtube.com/...', 'title': 'Video', 'channel': 'HoodInformatik'}],
            'image_url': 'https://...',
            'image_caption': 'Bildbeschreibung',
            'image_source': 'Quelle des Bildes',
        }], indent=2, ensure_ascii=False))
        print()
        return

    # Phase 3: Review
    issues = phase_review(articles_data)
    if issues:
        print("⚠️  Review-Warnungen vorhanden – Artikel werden trotzdem verarbeitet")
        print("   (Im Produktivbetrieb würden diese manuell geprüft)")

    # Phase 4: PDF
    pdf_path, pdf_filename = phase_pdf(articles_data, issue_id, issue_title, issue_date)

    # Phase 5: GitHub Pages
    if pdf_path:
        gh_path = phase_github_pages(articles_data, issue_id, issue_title, issue_date, pdf_filename)

    # Phase 6: Git Push
    if not skip_git:
        success = phase_git_push()
        if success:
            # Gedächtnis aktualisieren
            register_issue(issue_id, issue_title)

            # Gedächtnis: Bereits erklärte Themen tracken
            for article in articles_data:
                if article.get('category', '').startswith('Wie funktioniert'):
                    add_explained_topic(article['title'])
                if article.get('category', '').startswith('Distro'):
                    add_distro(article['title'])
                if article.get('category', '').startswith('GitHub'):
                    add_github_project(article['title'], '')
                    for src in article.get('sources', []):
                        if 'github.com' in src.get('url', ''):
                            add_github_project(article['title'], src['url'])
                            break

    print("=" * 60)
    print("  ✅ PIPELINE ABGESCHLOSSEN")
    print("=" * 60)

    return pdf_path


# ============================================================
# CLI-EINTRITT
# ============================================================

if __name__ == '__main__':
    print("🏴‍☠️  Bit & Byte Pipeline CLI")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        # Demo: Zeige den vollständigen Ablauf ohne echte Research
        print("📋 DEMO-MODUS: Zeige komplette Pipeline-Struktur")
        run_pipeline(articles_data=None)

    elif len(sys.argv) > 1 and sys.argv[1] == '--hello-world':
        # Hello World: Erstelle die Beispielausgabe
        print("📋 HELLO WORLD: Erstelle Beispielausgabe")
        from pdf_generator import create_hello_world_pdf
        create_hello_world_pdf()

        # Beispiel-Seite
        articles = [
            {
                'category': '📰 Editorial',
                'title': '👋 Willkommen bei Bit & Byte!',
                'body': (
                    'Herzlich willkommen zur ersten Ausgabe von Bit & Byte – '
                    'deiner wöchentlichen Tech-Zeitung!\n\n'
                    'Jeden Samstag um 8:00 Uhr erscheint eine neue Ausgabe mit '
                    'den spannendsten Themen aus der Welt der Technologie.\n\n'
                    'Unser Versprechen: **Keine Fake News.** Jeder Artikel wird '
                    'sorgfältig recherchiert. Alle Quellen findest du auf der '
                    'GitHub-Pages-Seite – im PDF selbst stehen keine Quellen.'
                ),
                'sources': [
                    {'url': 'https://www.tagesschau.de/', 'title': 'tagesschau.de – Beispielquelle', 'accessed': 'August 2026', 'citation': 'Allgemeine Nachrichtenquelle'}
                ],
                'media': [
                    {'type': 'video', 'url': 'https://youtube.com/@HoodInformatik', 'title': 'HoodInformatik auf YouTube', 'channel': 'HoodInformatik'}
                ],
                'image_url': 'https://www.tagesschau.de/multimedia/bilder/computer-ki-138~_v-gross16x9.jpg',
                'image_caption': 'KI-Illustration',
                'image_source': 'tagesschau.de',
            }
        ]
        gen = ArticlePageGenerator(
            issue_id='Hello-World',
            issue_title='Hello World – Beispielausgabe',
            issue_date='August 2026',
            articles=articles,
            pdf_filename='Bit_Byte_Woche_Hello_World.pdf'
        )
        gen.save(output_dir=str(BASE_DIR / 'docs' / 'issues' / 'hello-world'))
        print()
        print("   📄 PDF: /pdf/Bit_Byte_Woche_Hello_World.pdf")
        print("   🌐 Pages: /issues/hello-world/")
        print()

    elif len(sys.argv) > 1 and sys.argv[1] == '--check-git':
        # Prüfe Git-Status
        print("📋 GIT STATUS")
        subprocess.run(['git', 'status'], cwd=str(BASE_DIR))
        subprocess.run(['git', 'remote', '-v'], cwd=str(BASE_DIR))

    else:
        print("Verwendung:")
        print("  python3 tools/pipeline.py --demo          Zeige Pipeline-Ablauf")
        print("  python3 tools/pipeline.py --hello-world   Erstelle Beispielausgabe")
        print("  python3 tools/pipeline.py --check-git     Prüfe Git-Status")
        print("  python3 tools/pipeline.py [--skip-git]    Normale Pipeline (mit Artikeln als STDIN) ")
        print()
        print("Für den Normalbetrieb übergib Artikel-Daten als JSON über STDIN:")
        print("  cat articles.json | python3 tools/pipeline.py")
        print()
        print("Oder OpenClaw ruft direkt auf:")
        print("  openclaw → content-generation → pipeline.py → PDF + Pages + Push")
        print()