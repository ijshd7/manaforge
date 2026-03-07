#!/usr/bin/env bash
# Bump ManaForge version in VERSION, backend/pyproject.toml, and frontend/package.json.
# Usage:
#   ./scripts/bump-version.sh           # bump patch (0.1.0 -> 0.1.1)
#   ./scripts/bump-version.sh minor     # bump minor (0.1.0 -> 0.2.0)
#   ./scripts/bump-version.sh major     # bump major (0.1.0 -> 1.0.0)
#   ./scripts/bump-version.sh 0.2.0     # set explicit version

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$ROOT/VERSION"
PYPROJECT="$ROOT/backend/pyproject.toml"
PACKAGE_JSON="$ROOT/frontend/package.json"

read_current() {
  cat "$VERSION_FILE" | tr -d '[:space:]'
}

bump_patch() {
  local v="$1"
  local minor="${v#*.}"
  local patch="${minor#*.}"
  local major="${v%%.*}"
  minor="${minor%%.*}"
  echo "$major.$minor.$((patch + 1))"
}

bump_minor() {
  local v="$1"
  local minor="${v#*.}"
  local patch="${minor#*.}"
  local major="${v%%.*}"
  minor="${minor%%.*}"
  echo "$major.$((minor + 1)).0"
}

bump_major() {
  local v="$1"
  local major="${v%%.*}"
  echo "$((major + 1)).0.0"
}

case "${1:-patch}" in
  patch)
    NEW=$(bump_patch "$(read_current)")
    ;;
  minor)
    NEW=$(bump_minor "$(read_current)")
    ;;
  major)
    NEW=$(bump_major "$(read_current)")
    ;;
  *)
    if [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      NEW="$1"
    else
      echo "Usage: $0 [patch|minor|major|X.Y.Z]"
      exit 1
    fi
    ;;
esac

echo "$NEW" > "$VERSION_FILE"
sed -i.bak "s/^version = \".*\"/version = \"$NEW\"/" "$PYPROJECT" && rm -f "$PYPROJECT.bak"
sed -i.bak "s/\"version\": \".*\"/\"version\": \"$NEW\"/" "$PACKAGE_JSON" && rm -f "$PACKAGE_JSON.bak"

echo "Bumped to $NEW"
echo "  VERSION"
echo "  backend/pyproject.toml"
echo "  frontend/package.json"
