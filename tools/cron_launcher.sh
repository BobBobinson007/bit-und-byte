#!/bin/bash
# ============================================================
# BIT & BYTE – CRON PIPELINE LAUNCHER
# ============================================================
# Wird jeden Samstag um 8:00 Uhr MEZ von OpenClaw Cron aufgerufen.
#
# HAUPTLOOP (OpenClaw-gesteuert, im Cron-Prompt definiert):
#   Phase 1: Deep Research (web_search × 36 Runden)
#   Phase 2: Artikel schreiben
#   Phase 3: Review / Fake-News-Check
#   Phase 4: PDF generieren (python3 tools/pdf_generator.py)
#   Phase 5: GitHub Pages aktualisieren
#   Phase 6: Git Push
#   Phase 7: PDF an Telegram senden
#
# Dieses Script wird VOR der Pipeline ausgeführt,
# um die Umgebung vorzubereiten.
# ============================================================

BASE_DIR="/home/ansible/bit-und-byte"
LOG_FILE="$BASE_DIR/pipeline.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

# Logging
mkdir -p "$BASE_DIR"

{
  echo "========================================"
  echo "🕐 $TIMESTAMP – CRON LAUNCHER"
  echo "========================================"
  echo "BASE_DIR: $BASE_DIR"
  
  # In Projektverzeichnis wechseln
  cd "$BASE_DIR" || { echo "❌ FEHLER: $BASE_DIR nicht gefunden"; exit 1; }

  # Git-Status prüfen
  echo "📡 Git Status:"
  git remote -v 2>&1
  git fetch origin 2>&1
  echo "Branch: $(git branch --show-current 2>/dev/null)"

  # Prüfe, ob Python-Module verfügbar sind
  echo "🐍 Python-Check:"
  python3 -c "from fpdf import FPDF; print('✅ fpdf2 verfügbar')" 2>&1
  python3 -c "from tools import memory; print('✅ Memory-Modul verfügbar')" 2>&1

  echo ""
  echo "✅ Cron-Launcher bereit. OpenClaw übernimmt jetzt die Pipeline."
  echo "========================================"
  echo ""

} >> "$LOG_FILE" 2>&1