#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

REPOS_DIR="$ROOT_DIR/repos"
TEST_LIB_DIR="$ROOT_DIR/test_lib"
mkdir -p "$REPOS_DIR" "$TEST_LIB_DIR"

echo "=== Parsing config.toml ==="

IMPLS=$(python3 -c "
import tomllib, sys
with open('config.toml', 'rb') as f:
    cfg = tomllib.load(f)
for impl in cfg.get('impl', []):
    print(f\"{impl['git_url']}|{impl['git_ref']}|{impl['repo_dir']}\")
")

TEST_PAGES=$(python3 -c "
import tomllib
with open('config.toml', 'rb') as f:
    cfg = tomllib.load(f)
print(cfg['bench']['test_pages'])
")

echo "=== Cloning/updating implementation repos ==="

while IFS='|' read -r GIT_URL GIT_REF REPO_DIR; do
    [ -z "$GIT_URL" ] && continue
    TARGET_DIR="$REPOS_DIR/$REPO_DIR"

    if [ -d "$TARGET_DIR" ]; then
        echo "--- Updating $REPO_DIR ---"
        cd "$TARGET_DIR"
        git fetch --all --tags 2>&1
        git checkout "$GIT_REF" 2>&1
        git pull --ff-only 2>&1 || true
        cd "$ROOT_DIR"
    else
        echo "--- Cloning $REPO_DIR from $GIT_URL ---"
        git clone "$GIT_URL" "$TARGET_DIR" 2>&1
        cd "$TARGET_DIR"
        git checkout "$GIT_REF" 2>&1
        cd "$ROOT_DIR"
    fi
    echo "  -> $REPO_DIR now at $GIT_REF"
done <<< "$IMPLS"

echo "=== Generating test library ==="

if [ ! -f "$TEST_LIB_DIR/features.bin" ]; then
    echo "  test_lib/features.bin not found, generating (pages=$TEST_PAGES)..."
    python3 "$ROOT_DIR/gen_test_lib.py" \
        --pages "$TEST_PAGES" \
        --seed 42 \
        --output "$TEST_LIB_DIR"
    echo "  -> Generated test_lib/features.bin"
else
    echo "  test_lib/features.bin already exists, skipping generation"
fi

echo "=== Linking badapple.mp4 ==="

if [ ! -f "$ROOT_DIR/badapple.mp4" ]; then
    FOUND=0
    while IFS='|' read -r GIT_URL GIT_REF REPO_DIR; do
        [ -z "$GIT_URL" ] && continue
        if [ -f "$REPOS_DIR/$REPO_DIR/badapple.mp4" ]; then
            ln -s "$REPOS_DIR/$REPO_DIR/badapple.mp4" "$ROOT_DIR/badapple.mp4"
            echo "  -> Linked from repos/$REPO_DIR/badapple.mp4"
            FOUND=1
            break
        fi
    done <<< "$IMPLS"

    if [ "$FOUND" -eq 0 ]; then
        echo "  WARNING: badapple.mp4 not found in any cloned repo"
    fi
else
    echo "  badapple.mp4 already exists in working directory"
fi

echo "=== Setup complete ==="
