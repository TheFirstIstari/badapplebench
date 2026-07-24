#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

FILTER_STAGE="${1:-}"

echo "============================================"
echo "  BadAppleStein Benchmark Runner"
echo "============================================"

if [ -n "$FILTER_STAGE" ]; then
    echo "  Running stage: $FILTER_STAGE"
else
    echo "  Running all stages"
fi
echo ""

# Get list of all implementations
IMPLS=$(python3 -c "
import tomllib, sys
with open('config.toml', 'rb') as f:
    cfg = tomllib.load(f)
for impl in cfg.get('impl', []):
    stages = [c.get('stage', '') for c in impl.get('bench_cmds', [])]
    print(f\"{impl['lang']}|{impl['label']}|{' '.join(stages)}\")
")

# Get all available stages
ALL_STAGES=$(python3 -c "
import tomllib
with open('config.toml', 'rb') as f:
    cfg = tomllib.load(f)
stages = set()
for impl in cfg.get('impl', []):
    for cmd in impl.get('bench_cmds', []):
        stages.add(cmd.get('stage', ''))
for s in sorted(stages):
    print(s)
")

STAGES_TO_RUN=()
if [ -n "$FILTER_STAGE" ]; then
    STAGES_TO_RUN=("$FILTER_STAGE")
else
    while IFS= read -r s; do
        [ -z "$s" ] && continue
        STAGES_TO_RUN+=("$s")
    done <<< "$ALL_STAGES"
fi

TOTAL_IMPLS=0
TOTAL_BENCHS=0
FAILED_BENCHS=0

echo "=== Phase 0: Setup ==="
bash "$SCRIPT_DIR/setup_impls.sh"
echo ""

echo "=== Phase 1: Building implementations ==="
echo ""

BUILD_IMPLS=$(python3 -c "
import tomllib, sys
with open('config.toml', 'rb') as f:
    cfg = tomllib.load(f)
for impl in cfg.get('impl', []):
    print(f\"{impl['lang']}|{impl['label']}\")
")

while IFS='|' read -r LANG LABEL; do
    [ -z "$LANG" ] && continue
    TOTAL_IMPLS=$((TOTAL_IMPLS + 1))
    echo ""
    echo ">>> Building $LANG $LABEL..."
    if ! bash scripts/build_impl.sh "$LANG" "$LABEL"; then
        echo "ERROR: Failed to build $LANG $LABEL" >&2
    fi
done <<< "$BUILD_IMPLS"

echo ""
echo "=== Phase 2: Running benchmarks ==="
echo ""

while IFS='|' read -r LANG LABEL IMPL_STAGES; do
    [ -z "$LANG" ] && continue

    for STAGE in "${STAGES_TO_RUN[@]}"; do
        # Check if this impl has a bench_cmd for this stage
        if echo "$IMPL_STAGES" | grep -qw "$STAGE"; then
            TOTAL_BENCHS=$((TOTAL_BENCHS + 1))
            echo ""
            echo ">>> Benchmarking $LANG $LABEL ($STAGE)..."
            if ! bash scripts/bench.sh "$LANG" "$LABEL" "$STAGE"; then
                echo "ERROR: Benchmark failed for $LANG $LABEL $STAGE" >&2
                FAILED_BENCHS=$((FAILED_BENCHS + 1))
            fi
        fi
    done
done <<< "$IMPLS"

echo ""
echo "=== Phase 3: Generating README ==="

if [ -f scripts/gen_readme.py ]; then
    python3 scripts/gen_readme.py
    echo "  README generated"
else
    echo "  WARNING: scripts/gen_readme.py not found, skipping"
fi

echo ""
echo "============================================"
echo "  Benchmark Summary"
echo "============================================"
echo "  Implementations: $TOTAL_IMPLS"
echo "  Benchmarks run:  $TOTAL_BENCHS"
echo "  Failed:          $FAILED_BENCHS"
echo "============================================"
