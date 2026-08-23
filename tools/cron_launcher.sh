#!/bin/bash
# ============================================================
# BIT & BYTE – CRON PIPELINE LAUNCHER
# ============================================================
# Wird jeden Samstag um 8:00 Uhr von OpenClaw Cron aufgerufen.
#
# Was passiert:
#   1. Deep Research (OpenClaw Sessions)
#   2. Artikel schreiben
#   3. Review
#   4. PDF generieren
#   5. GitHub Pages aktualisieren
#   6. Git Push
#   7. PDF an Chat senden
# ============================================================

BASE_DIR="/home/ansible/bit-und-byte"
LOG_FILE="$BASE_DIR/pipeline.log"

# Logging
echo "========================================" >> "$LOG_FILE"
echo "🕐 $(date '+%Y-%m-%d %H:%M:%S') – Pipeline gestartet" >> "$LOG_FILE"

# 1. In das Projekt-Verzeichnis wechseln
cd "$BASE_DIR" || {
    echo "❌ Konnte nicht nach $BASE_DIR wechseln" >> "$LOG_FILE"
    exit 1
}

# 2. GitHub-Status prüfen
git remote -v >> "$LOG_FILE" 2>&1
git fetch origin >> "$LOG_FILE" 2>&1

# 3. Hello-World generieren (für den ersten Test)
#    In der Produktion wird hier die volle Pipeline ausgeführt
python3 tools/pipeline.py --hello-world 2>&1 >> "$LOG_FILE"

echo "✅ $(date '+%Y-%m-%d %H:%M:%S') – Pipeline beendet" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"