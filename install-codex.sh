#!/usr/bin/env bash
# Safe, non-invasive sandbox installer for Codex / ChatGPT Desktop
# Writes ONLY to ~/.gemini/config/skills/skills-companion/ (zero dotfile edits, zero telemetry)
set -e

REPO_RAW="https://raw.githubusercontent.com/gdgworkshop/skills/main"
SKILL_DIR="$HOME/.gemini/config/skills/skills-companion"

mkdir -p "$SKILL_DIR/scripts" "$SKILL_DIR/references"
curl -fsSL "$REPO_RAW/SKILL.md" -o "$SKILL_DIR/SKILL.md"
curl -fsSL "$REPO_RAW/VERSION" -o "$SKILL_DIR/VERSION"
curl -fsSL "$REPO_RAW/scripts/companion.py" -o "$SKILL_DIR/scripts/companion.py"
chmod +x "$SKILL_DIR/scripts/companion.py"

echo "✅ Skills Companion installed (safe sandbox mode) into $SKILL_DIR"
