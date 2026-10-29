#!/bin/sh
# Install skill files only. Python/OCR preparation is performed by the AI on first use.
set -eu
REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET=${1:-}
USER_ROOT=${2:-"$HOME"}
if [ -z "$TARGET" ]; then
  printf 'Install for: 1 Codex / 2 Claude Code / 3 Both / 4 WorkBuddy\n'
  read -r TARGET
fi
case "$TARGET" in
  1|codex) TARGET=codex ;;
  2|claude) TARGET=claude ;;
  3|all) TARGET=all ;;
  4|workbuddy) printf 'WorkBuddy: download scan-pdf-to-word.zip from Releases, then import it in Skills > Add > Upload.\nhttps://github.com/laughing-glitch/scan-pdf-to-word-skill/releases/latest\n'; exit 0 ;;
  *) printf 'Usage: sh install.sh codex|claude|all|workbuddy [user-home-for-install]\n' >&2; exit 2 ;;
esac
SOURCE="$REPO_DIR/skills/scan-pdf-to-word"
[ -f "$SOURCE/SKILL.md" ] || { printf 'Missing skill source. Download and extract the complete starter package.\n' >&2; exit 1; }
for HOST in codex claude; do
  if [ "$TARGET" = "$HOST" ] || [ "$TARGET" = all ]; then
    if [ "$HOST" = codex ]; then BASE="$USER_ROOT/.agents/skills"; else BASE="$USER_ROOT/.claude/skills"; fi
    [ ! -e "$BASE/scan-pdf-to-word" ] || { printf 'Already exists; no files overwritten: %s\n' "$BASE/scan-pdf-to-word" >&2; exit 1; }
  fi
done
for HOST in codex claude; do
  if [ "$TARGET" = "$HOST" ] || [ "$TARGET" = all ]; then
    if [ "$HOST" = codex ]; then BASE="$USER_ROOT/.agents/skills"; else BASE="$USER_ROOT/.claude/skills"; fi
    mkdir -p "$BASE"
    cp -R "$SOURCE" "$BASE/scan-pdf-to-word"
    printf 'Installed: %s\n' "$BASE/scan-pdf-to-word"
  fi
done
printf 'Open a new conversation and ask the AI to initialize scan-pdf-to-word and convert your PDF.\n'
