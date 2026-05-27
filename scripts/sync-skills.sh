#!/usr/bin/env bash
# Sync ./skills/ from submodules/cockroachdb-skills/skills/
#
# Mirrors the submodule's skills directory into the vendored ./skills/ tree
# that Codex actually reads. Run after bumping the submodule pointer.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/submodules/cockroachdb-skills/skills"
DST="$REPO_ROOT/skills"

if [[ ! -d "$SRC" ]]; then
  echo "ERROR: submodule not initialized at $SRC" >&2
  echo "Run: git submodule update --init --recursive" >&2
  exit 1
fi

git -C "$REPO_ROOT/submodules/cockroachdb-skills" submodule update --init --recursive

mkdir -p "$DST"
rsync -a --delete --exclude='.git' --exclude='.github' "$SRC/" "$DST/"

SUBMODULE_SHA=$(git -C "$REPO_ROOT/submodules/cockroachdb-skills" rev-parse --short HEAD)
SKILL_COUNT=$(find "$DST" -name 'SKILL.md' -type f | wc -l | tr -d ' ')

echo "Synced skills from cockroachdb-skills@${SUBMODULE_SHA}"
echo "Skills present: ${SKILL_COUNT}"
echo "Review changes with: git -C \"$REPO_ROOT\" status skills/"
