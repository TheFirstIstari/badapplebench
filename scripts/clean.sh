#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Cleaning generated artifacts ==="

# Remove regenerable test library (re-created by setup_impls.sh on next bench)
rm -rf test_lib/
echo "  removed test_lib/"

# Remove the impl repos dir, then re-link any local dev checkouts.
# repos/* may be symlinks into /Users/frobinson/dev/{BadApplestein,BadOdinStein,BadZiggle}
# — wiping them makes the next bench clone from GitHub and silently lose local
# uncommitted fixes, so re-create the symlinks for any local checkout found.
rm -rf repos/
mkdir -p repos/

REPO_DIRS=$(python3 -c "
import tomllib
with open('config.toml', 'rb') as f:
    cfg = tomllib.load(f)
for impl in cfg.get('impl', []):
    print(impl['repo_dir'])
")

for REPO_DIR in $REPO_DIRS; do
    [ -z "$REPO_DIR" ] && continue
    LOCAL_SRC="$ROOT_DIR/../$REPO_DIR"
    if [ -d "$LOCAL_SRC" ]; then
        ln -s "$LOCAL_SRC" "repos/$REPO_DIR"
        echo "  re-linked repos/$REPO_DIR -> $LOCAL_SRC"
    else
        echo "  note: no local checkout at $LOCAL_SRC; next bench will clone it"
    fi
done

echo "=== Clean complete ==="
