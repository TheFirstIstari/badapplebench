#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 3 ]; then
    echo "Usage: $0 <lang> <label> <stage>" >&2
    exit 1
fi

LANG="$1"
LABEL="$2"
STAGE="$3"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p results

echo "=== Benchmarking: $LANG $LABEL (stage: $STAGE) ==="

# Parse impl config
LOOKUP=$(python3 -c "
import tomllib, sys
with open('config.toml', 'rb') as f:
    cfg = tomllib.load(f)
lang, label = sys.argv[1], sys.argv[2]
for impl in cfg.get('impl', []):
    if impl['lang'] == lang and impl['label'] == label:
        print(impl.get('repo_dir', ''))
        print(impl.get('binary_path', ''))
        import json
        bench_cmds = impl.get('bench_cmds', [])
        print(json.dumps(bench_cmds))
        sys.exit(0)
print('NOT FOUND', file=sys.stderr)
sys.exit(1)
" "$LANG" "$LABEL")

REPO_DIR=$(echo "$LOOKUP" | sed -n '1p')
BINARY_PATH=$(echo "$LOOKUP" | sed -n '2p')
BENCH_CMDS=$(echo "$LOOKUP" | sed -n '3p')

# Parse bench config
BENCH_CONFIG=$(python3 -c "
import tomllib, json
with open('config.toml', 'rb') as f:
    cfg = tomllib.load(f)
bench = cfg.get('bench', {})
render = bench.get('render', {})
out = {
    'warmup': bench.get('warmup', 1),
    'runs': bench.get('runs', 10),
    'test_frames': bench.get('test_frames', 200),
    'width': render.get('width', 1920),
    'height': render.get('height', 1080),
}
print(json.dumps(out))
")

WARMUP=$(echo "$BENCH_CONFIG" | python3 -c "import sys,json; print(json.load(sys.stdin)['warmup'])")
RUNS=$(echo "$BENCH_CONFIG" | python3 -c "import sys,json; print(json.load(sys.stdin)['runs'])")
TEST_FRAMES=$(echo "$BENCH_CONFIG" | python3 -c "import sys,json; print(json.load(sys.stdin)['test_frames'])")
WIDTH=$(echo "$BENCH_CONFIG" | python3 -c "import sys,json; print(json.load(sys.stdin)['width'])")
HEIGHT=$(echo "$BENCH_CONFIG" | python3 -c "import sys,json; print(json.load(sys.stdin)['height'])")

# Resolve template variables
ABS_BINARY="$ROOT_DIR/repos/$REPO_DIR/$BINARY_PATH"

ABS_VIDEO=""
if [ -f "$ROOT_DIR/badapple.mp4" ]; then
    ABS_VIDEO="$ROOT_DIR/badapple.mp4"
elif [ -f "$ROOT_DIR/test_lib/badapple.mp4" ]; then
    ABS_VIDEO="$ROOT_DIR/test_lib/badapple.mp4"
else
    echo "ERROR: badapple.mp4 not found" >&2
    exit 1
fi

ABS_LIB="$ROOT_DIR/test_lib"
ABS_OUTPUT="/tmp/badapplebench_output"

# Find the bench_cmd for this stage
CMD_CONFIG=$(echo "$BENCH_CMDS" | python3 -c "
import sys, json
cmds = json.load(sys.stdin)
for c in cmds:
    if c.get('stage') == '$STAGE':
        print(c.get('cmd', ''))
        prepare = c.get('prepare', '')
        print(prepare)
        sys.exit(0)
print('NOT FOUND', file=sys.stderr)
sys.exit(1)
")

BENCH_CMD=$(echo "$CMD_CONFIG" | sed -n '1p')
PREPARE_CMD=$(echo "$CMD_CONFIG" | sed -n '2p')

if [ -z "$BENCH_CMD" ]; then
    echo "ERROR: No bench_cmd found for stage '$STAGE' in $LANG $LABEL" >&2
    exit 1
fi

# Resolve template variables in the command
RESOLVED_CMD="$BENCH_CMD"
RESOLVED_CMD="${RESOLVED_CMD//\{binary\}/$ABS_BINARY}"
RESOLVED_CMD="${RESOLVED_CMD//\{video\}/$ABS_VIDEO}"
RESOLVED_CMD="${RESOLVED_CMD//\{lib\}/$ABS_LIB}"
RESOLVED_CMD="${RESOLVED_CMD//\{frames\}/$TEST_FRAMES}"
RESOLVED_CMD="${RESOLVED_CMD//\{width\}/$WIDTH}"
RESOLVED_CMD="${RESOLVED_CMD//\{height\}/$HEIGHT}"
RESOLVED_CMD="${RESOLVED_CMD//\{output\}/$ABS_OUTPUT}"

echo "  binary: $ABS_BINARY"
echo "  video: $ABS_VIDEO"
echo "  lib: $ABS_LIB"
echo "  frames: $TEST_FRAMES"
echo "  resolution: ${WIDTH}x${HEIGHT}"
echo "  cmd: $RESOLVED_CMD"

# Run prepare command if present and stage is render
if [ -n "$PREPARE_CMD" ] && [ "$STAGE" = "render" ]; then
    RESOLVED_PREPARE="$PREPARE_CMD"
    RESOLVED_PREPARE="${RESOLVED_PREPARE//\{binary\}/$ABS_BINARY}"
    RESOLVED_PREPARE="${RESOLVED_PREPARE//\{video\}/$ABS_VIDEO}"
    RESOLVED_PREPARE="${RESOLVED_PREPARE//\{lib\}/$ABS_LIB}"
    RESOLVED_PREPARE="${RESOLVED_PREPARE//\{frames\}/$TEST_FRAMES}"
    RESOLVED_PREPARE="${RESOLVED_PREPARE//\{width\}/$WIDTH}"
    RESOLVED_PREPARE="${RESOLVED_PREPARE//\{height\}/$HEIGHT}"
    RESOLVED_PREPARE="${RESOLVED_PREPARE//\{output\}/$ABS_OUTPUT}"

    echo "  Running prepare command (untimed)..."
    echo "  prepare: $RESOLVED_PREPARE"
    if ! eval "$RESOLVED_PREPARE"; then
        echo "ERROR: Prepare command failed" >&2
        exit 1
    fi
fi

# Create results directory
DATE_PREFIX=$(date +%Y-%m-%d)
RESULTS_DIR="$ROOT_DIR/results/${DATE_PREFIX}_${LANG}_${LABEL}"
mkdir -p "$RESULTS_DIR"

HYPERFINE_OUTPUT="$RESULTS_DIR/${STAGE}.json"
META_PATH="$RESULTS_DIR/meta.json"

echo "  Running hyperfine ($RUNS runs, warmup=$WARMUP)..."

if ! hyperfine \
    --warmup "$WARMUP" \
    -n "$RUNS" \
    "$RESOLVED_CMD" \
    --export-json "$HYPERFINE_OUTPUT"; then
    echo "ERROR: hyperfine failed for $LANG $LABEL $STAGE" >&2
    exit 1
fi

echo "  Results saved to $HYPERFINE_OUTPUT"

# Write meta.json
GIT_COMMIT=$(git -C "$ROOT_DIR/repos/$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")

python3 -c "
import json, socket, datetime
meta = {
    'lang': '$LANG',
    'label': '$LABEL',
    'stage': '$STAGE',
    'date': datetime.date.today().isoformat(),
    'hostname': socket.gethostname(),
    'git_commit': '$GIT_COMMIT'
}
with open('$META_PATH', 'w') as f:
    json.dump(meta, f, indent=2)
"

echo "  Meta saved to $META_PATH"
echo "=== Benchmark complete: $LANG $LABEL $STAGE ==="
