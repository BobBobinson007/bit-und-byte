#!/usr/bin/env python3
"""
Bit & Byte – Memory Manager
Trackt bereits verwendete Themen, Distributionen, GitHub-Projekte und Ausgaben.
Wird vor jeder neuen Ausgabe gelesen und nach der Erstellung aktualisiert.
"""

import json
import os
from datetime import datetime

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memory')

def load_memory(name):
    """Lädt ein JSON-Gedächtnisfile."""
    path = os.path.join(MEMORY_DIR, f'{name}.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_memory(name, data):
    """Speichert ein JSON-Gedächtnisfile."""
    path = os.path.join(MEMORY_DIR, f'{name}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_distro(name):
    """Fügt eine Distribution zur 'bereits erwähnt'-Liste hinzu."""
    data = load_memory('distros')
    if 'mentioned' not in data:
        data['mentioned'] = []
    if name not in data['mentioned']:
        data['mentioned'].append(name)
    data['last_updated'] = datetime.now().isoformat()
    save_memory('distros', data)
    return data['mentioned']

def get_distros():
    """Gibt alle bereits erwähnten Distributionen zurück."""
    data = load_memory('distros')
    return data.get('mentioned', [])

def add_explained_topic(topic):
    """Fügt ein Thema zu 'Wie funktioniert eigentlich...?' hinzu."""
    data = load_memory('howto_explained')
    if 'explained_topics' not in data:
        data['explained_topics'] = []
    if topic not in data['explained_topics']:
        data['explained_topics'].append(topic)
    data['last_updated'] = datetime.now().isoformat()
    save_memory('howto_explained', data)
    return data['explained_topics']

def get_explained_topics():
    """Gibt alle bereits erklärten Themen zurück."""
    data = load_memory('howto_explained')
    return data.get('explained_topics', [])

def add_github_project(name, url):
    """Fügt ein GitHub-Projekt zur 'bereits vorgestellt'-Liste hinzu."""
    data = load_memory('github_projects')
    if 'featured_projects' not in data:
        data['featured_projects'] = []
    project = {'name': name, 'url': url}
    if project not in data['featured_projects']:
        data['featured_projects'].append(project)
    data['last_updated'] = datetime.now().isoformat()
    save_memory('github_projects', data)
    return data['featured_projects']

def get_github_projects():
    """Gibt alle bereits vorgestellten GitHub-Projekte zurück."""
    data = load_memory('github_projects')
    projects = data.get('featured_projects', [])
    return [p['name'] for p in projects]

def register_issue(issue_id, title):
    """Registriert eine neue Ausgabe."""
    data = load_memory('issues')
    if 'published_issues' not in data:
        data['published_issues'] = []
    data['published_issues'].append({
        'id': issue_id,
        'title': title,
        'date': datetime.now().isoformat()
    })
    data['last_issue_date'] = datetime.now().isoformat()
    save_memory('issues', data)

def get_last_issue():
    """Gibt die letzte erschienene Ausgabe zurück."""
    data = load_memory('issues')
    issues = data.get('published_issues', [])
    return issues[-1] if issues else None

def get_all_issues():
    """Gibt alle erschienenen Ausgaben zurück."""
    data = load_memory('issues')
    return data.get('published_issues', [])

if __name__ == '__main__':
    # Test
    print('=== Bit & Byte Memory Manager Test ===')
    print(f'Distros: {get_distros()}')
    print(f'Explained topics: {get_explained_topics()}')
    print(f'GitHub projects: {get_github_projects()}')
    print(f'All issues: {get_all_issues()}')
    print(f'Last issue: {get_last_issue()}')