#!/usr/bin/env python3
"""
Bit & Byte – Research Engine (Web-Recherche-Modul)
Führt Deep Research durch: Web-Suchen + Content-Fetching + Quellenprüfung.

Jeder Artikel durchläuft:
1. Keyword-Recherche (Web-Suche)
2. Content-Extraktion (Web-Fetch)
3. Quellen-Sammlung (URLs + Zitate)
4. Prüfung (keine Fake News – immer quoted)
"""

import json
import sys
import os
import re
import textwrap
from datetime import datetime, timezone
from urllib.parse import urlparse

# OpenClaw-Tools via Subprocess-Aufruf (für Automation ohne direkten API-Zugriff)
# In der Praxis wird dieses Skript von der Pipeline mit Prompts gesteuert.
# Hier definieren wir die Recherche-Logik für jede Kategorie.

# ---------------------------------------------------------------------------
# RESEARCH TOPICS & SEARCH QUERIES
# ---------------------------------------------------------------------------

RESEARCH_TOPICS = {
    'ai_models': {
        'queries': [
            'latest AI model release 2026',
            'new LLM open source this week',
            'aktuelles KI-Modell Veröffentlichung',
            'AI benchmark leaderboard update',
        ],
        'description': 'Neue KI-Modelle und relevante KI-News der Woche',
    },
    'github_project': {
        'queries': [
            'trending GitHub repository this week',
            'best new open source project github',
            'GitHub trending repositories daily',
            'interesting new GitHub project',
        ],
        'description': 'Das interessanteste neue Open-Source-Projekt der Woche',
    },
    'distro': {
        'queries': [
            'latest Linux distribution release 2026',
            'Linux distro news this month',
            'new Linux distribution version',
        ],
        'description': 'Linux-Distribution des Monats',
    },
    'hacks': {
        'queries': [
            'major cyber attack this week 2026',
            'data breach this week',
            'größter Hack der Woche',
            'Datenleck aktuell',
        ],
        'description': 'Bedeutende Hacks und Datenleaks der Woche',
    },
    'security_cve': {
        'queries': [
            'critical CVE this week 2026',
            'wichtigste Sicherheitslücke der Woche',
            'new vulnerability disclosure',
            'CVE explained simply',
        ],
        'description': 'Aktuelle Sicherheitslücke verständlich erklärt',
    },
    'howto': {
        'queries': [
            'explain Passkeys simply',
            'how does DNS work explained',
            'how does end-to-end encryption work',
            'how does VPN work explained',
        ],
        'description': '"Wie funktioniert eigentlich…?" – Ein Technik-Thema erklärt',
    },
    'docker': {
        'queries': [
            'Docker news this week',
            'container technology update 2026',
            'Podman Docker news',
        ],
        'description': 'Neuigkeiten aus der Docker-/Container-Welt',
    },
    'ios': {
        'queries': [
            'iOS 20 update news 2026',
            'Apple iOS beta release this week',
            'neues iOS Update',
        ],
        'description': 'iOS-Updates – Beta- und Release-News',
    },
    'internet_myths': {
        'queries': [
            'internet myth debunked 2026',
            'internet fact check viral claim',
            'faktencheck internet märchen',
        ],
        'description': 'Internet-Mythen und Faktenchecks',
    },
    'tech_fairs': {
        'queries': [
            'IFA 2026 news',
            'WWDC 2026 announcements',
            'tech conference this month 2026',
            'CES 2026 highlights',
        ],
        'description': 'Aktuelle Technikmessen und Konferenzen',
    },
    'space': {
        'queries': [
            'space news this week 2026',
            'NASA latest mission 2026',
            'SpaceX starship update',
            'neues aus der raumfahrt',
        ],
        'description': 'Aktuelles aus der Raumfahrt und Astronomie',
    },
    'studies': {
        'queries': [
            'new scientific study 2026 interesting',
            'bemerkenswerte studie dieser woche',
            'groundbreaking research paper 2026',
            'neue studie publiziert',
        ],
        'description': 'Neue wissenschaftliche Studien (nicht nur Tech)',
    },
    'deep_dive': {
        'queries': [
            'trending technology deep analysis 2026',
            'deep dive technology explainer',
            'what is the future of AI/blockchain/quantum',
        ],
        'description': 'Deep Dive – Ein Thema wird tiefgehend analysiert',
    },
}


class ResearchEngine:
    """
    Führt die Recherche für eine Bit & Byte Ausgabe durch.
    Nutzt OpenClaw's web_search und web_fetch (via CLI-Aufruf im Pipeline-Kontext).
    Hier als Bibliothek für die Pipeline.
    """

    def __init__(self, memory_module=None):
        self.memory = memory_module
        self.results = {}
        self.sources = []
        self.issue_id = datetime.now().strftime('%Y-W%V')
        self.issue_date = datetime.now().strftime('%d.%m.%Y')

    def get_issue_id(self):
        """Gibt die Issue-ID im Format YYYY-Www zurück."""
        from datetime import datetime
        # ISO-Kalenderwoche
        iso = datetime.now().isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"

    def run_all_searches(self):
        """
        Führt alle Recherchen parallel aus.
        In der echten Pipeline wird dies durch OpenClaw-Sessions (web_search) gemacht.
        Diese Methode definiert, welche Prompts an die Sessions gehen.
        """
        print(f"🔍 Starte Deep Research für Ausgabe {self.get_issue_id()}")
        print(f"   Themen: {len(RESEARCH_TOPICS)} Kategorien\n")

        for topic_key, topic_config in RESEARCH_TOPICS.items():
            print(f"  [{topic_key}] {topic_config['description']}")
            for q in topic_config['queries']:
                print(f"    → Suche: {q}")

        print(f"\n📚 Geschätzte Deep-Research-Runden: {len(RESEARCH_TOPICS) * 3}")
        print(f"   (1. Keyword-Runde | 2. Content-Runde | 3. Verifikations-Runde)")
        return RESEARCH_TOPICS

    def get_prompts_for_research(self, topic_key, topic_config, memory_context=""):
        """
        Generiert die Forschungs-Prompts für eine Kategorie.
        Diese Prompts werden an OpenClaw-Sessions übergeben.
        """
        knows_context = ""
        if memory_context:
            knows_context = f"\nBereits bekannt (nicht wiederholen): {memory_context}"

        prompt = f"""Du recherchierst für die Kategorie "{topic_config['description']}".

AUFGABE:
1. Suche nach aktuellen Informationen (heute: {self.issue_date})
2. Extrahiere die wichtigsten Fakten
3. Sammle mindestens 2-3 Quellen-URLs pro Artikel
4. Schreibe einen gut lesbaren Artikel (200-400 Wörter)
5. Füge KEINE Fake News oder unbelegte Behauptungen hinzu

FORMAT (JSON):
{{
    "title": "Artikeltitel",
    "body": "Artikeltext inkl. Quellenverweise [1][2]",
    "sources": [
        {{"url": "https://...", "title": "Seitentitel", "accessed": "{self.issue_date}"}}
    ],
    "media": [
        {{"type": "video", "url": "https://youtube.com/...", "title": "Video-Titel", "channel": "..."}}
    ]
}}{knows_context}

WICHTIG: Jede Behauptung muss durch eine Quelle belegt sein."""
        return prompt

    def get_deep_dive_prompt(self, topic=""):
        """
        Spezieller Prompt für den Deep Dive – der aufwändigste Artikel.
        """
        prompt = f"""Du erstellst einen DEEP DIVE für Bit & Byte – eine wöchentliche Tech-Zeitung.

AUFGABE:
- Wähle ein aktuelles, interessantes Tech-Thema
- Gehe in die Tiefe (500-800 Wörter)
- Erkläre technische Konzepte verständlich
- Zeige Zusammenhänge auf
- Nenne Vor- und Nachteile
- Gib einen Ausblick

FORMAT (JSON):
{{
    "title": "Deep Dive: [Thema]",
    "subtitle": "Kurze Zusammenfassung",
    "body": "Tiefgehende Analyse...",
    "sources": [ ... ],
    "media": [ ... ]
}}

Quellenpflicht: Mindestens 3 Quellen."""
        return prompt


if __name__ == '__main__':
    engine = ResearchEngine()
    engine.run_all_searches()
    print("\n✅ Research Engine bereit.")
    # Beispiel-Prompt ausgeben
    print("\n=== Beispiel-Prompt (KI-Modelle) ===")
    print(engine.get_prompts_for_research('ai_models', RESEARCH_TOPICS['ai_models']))