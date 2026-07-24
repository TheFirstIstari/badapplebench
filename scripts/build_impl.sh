#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 2 ]; then
    echo "Usage: $0 <lang> <label>" >&2
    exit 1
fi

LANG="$1"
LABEL="$2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Building implementation: $LANG $LABEL ==="

LOOKUP=$(python3 -c "
import tomllib, sys
with open('config.toml', 'rb') as f:
    cfg = tomllib.load(f)
lang, label = sys.argv[1], sys.argv[2]
for impl in cfg.get('impl', []):
    if impl['lang'] == lang and impl['label'] == label:
        print(impl['repo_dir'])
        print(impl['build_cmd'])
        print(impl['binary_path'])
        sys.exit(0)
print('NOT FOUND', file=sys.stderr)
sys.exit(1)
" "$LANG" "$LABEL")

REPO_DIR=$(echo "$LOOKUP" | sed -n '1p')
BUILD_CMD=$(echo "$LOOKUP" | sed -n '2p')
BINARY_PATH=$(echo "$LOOKUP" | sed -n '3p')

TARGET_DIR="$ROOT_DIR/repos/$REPO_DIR"

if [ ! -d "$TARGET_DIR" ]; then
    echo "ERROR: Repo directory not found: $TARGET_DIR" >&2
    echo "       Run setup_impls.sh first." >&2
    exit 1
fi

cd "$TARGET_DIR"

echo "  repo_dir: $REPO_DIR"
echo "  build_cmd: $BUILD_CMD"
echo "  binary_path: $BINARY_PATH"

if eval "$BUILD_CMD"; then
    if [ -f "$BINARY_PATH" ]; then
        echo "=== Build succeeded: $REPO_DIR/$BINARY_PATH ==="
    else
        echo "WARNING: Build command succeeded but binary not found at $BINARY_PATH" >&2
    fi
else
    echo "ERROR: Build failed for $LANG $LABEL ($REPO_DIR)" >&2
    exit 1
fi
