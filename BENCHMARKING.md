# BadAppleBench — Benchmarking Guide & Knowledge Base

This document captures everything learned about the benchmarking system, performance characteristics, and how to extend it.

---

## Architecture Overview

BadAppleBench is a cross-language performance benchmark suite for [BadAppleStein](https://github.com/TheFirstIstari/BadApplestein) — an implementation that recreates the "Bad Apple" shadow art video using tile-based rendering. It measures how fast different language implementations can perform the same task.

### Pipeline Stages

| Stage | What it does | Typical time range |
|-------|-------------|-------------------|
| **arrange** | Matches video frames to library pages, builds a manifest | 1–6 seconds |
| **render** | Renders matched pages into images (tile-based compositing) | 15–20 seconds |
| **encode** | Full pipeline: arrange → render → encode to video | 1.5–280 seconds |

The full pipeline (`encode`) includes arrange and render internally. The `arrange` and `render` stages can be run independently for profiling.

### Data Flow

```
badapple.mp4 → [arrange] → manifest.bin → [render] → frame images → [encode] → output.mov
                      ↑
              test_lib/ (2000 synthetic pages with feature vectors)
```

---

## Benchmark Parameters

Defined in `config.toml` under `[bench]`:

| Parameter | Current Value | Purpose |
|-----------|--------------|---------|
| `warmup` | 1 | Hyperfine warmup run (discarded from timing) |
| `runs` | 10 | Number of timed runs per benchmark |
| `test_pages` | 2000 | Pages in the synthetic test library |
| `test_frames` | 200 | Video frames to process |
| `render.width` | 7680 | Output width (8K) |
| `render.height` | 4320 | Output height (8K) |

**Critical**: These parameters must remain consistent across all benchmark runs for results to be comparable. Any change to `test_pages`, `test_frames`, or resolution invalidates historical comparisons.

---

## Results Structure

Results are stored in `results/` as git-tracked hyperfine JSON:

```
results/
├── YYYY-MM-DD_<lang>_<label>/     # e.g., 2026-07-25_odin_dev/
│   ├── meta.json                  # lang, label, date, hostname, git commit
│   ├── arrange.json               # hyperfine output for arrange stage
│   ├── render.json                # hyperfine output for render stage
│   └── encode.json                # hyperfine output for encode stage
```

**Naming convention**: `<date>_<language>_<version>` — the directory name encodes the combo. Variants like `-8k` are appended to the label.

### Key Metrics in Hyperfine JSON

- `mean`: Average execution time in seconds
- `stddev`: Standard deviation across runs
- `times`: Array of individual run times (used for box plots)
- `min` / `max`: Fastest and slowest runs

---

## Performance Observations

### C vs Odin — Baseline (200 frames, standard resolution)

| Metric | C v1.0.0 | Odin dev | Ratio |
|--------|----------|----------|-------|
| arrange | 1.56s | 5.70s | 3.6x slower |
| render | — | 15.81s | — |
| encode (full) | 1.61s | 21.50s | 13.4x slower |

**Key insight**: The C implementation's `encode` time (1.61s) is essentially the `arrange` time (1.56s) — the render+encode stages are negligible or optimized away. The Odin implementation runs all stages sequentially.

### 8K Resolution Impact

| Impl | Standard | 8K | Ratio |
|------|----------|-----|-------|
| C v1.0.0 | 1.61s | 33.28s | 20.7x |
| Odin dev | 21.50s | 275.75s | 12.8x |

**Key insight**: 8K is ~20x slower for C (4320×7680 = 33M pixels vs 1080p's 2M pixels = 16.5x pixel increase). Odin's 8K slowdown is lower because its baseline is already slower per-pixel.

### Hardware Encoding

- C v1.0.0 8K run used `--no-hw` flag (software encoding)
- Hardware encoding (VideoToolbox/NVENC) can reduce encode time significantly
- The `--no-hw` flag is used for fair CPU-only comparison across platforms

### Threading Model Differences

- **C v1.0.0**: Uses OpenMP + pthreads for parallelism
- **Odin dev**: Currently single-threaded with software ProRes encoding
- This is the primary architectural difference driving performance gaps

---

## How to Add a New Implementation

1. Add an `[[impl]]` entry to `config.toml`:

```toml
[[impl]]
lang = "rust"
label = "v0.1.0"
git_url = "https://github.com/user/BadAppleRust.git"
git_ref = "main"
repo_dir = "BadAppleRust"
build_cmd = "cargo build --release"
binary_path = "target/release/badapplerust"

[[impl.bench_cmds]]
stage = "arrange"
cmd = "{binary} arrange --video {video} --lib {lib} --frames {frames}"

[[impl.bench_cmds]]
stage = "encode"
cmd = "{binary} encode --video {video} --lib {lib} --frames {frames} --output {output}"
```

2. Run `mise run bench` — the scripts auto-discover from config.

### Template Variables

| Variable | Resolves To |
|----------|------------|
| `{binary}` | Absolute path to the built binary |
| `{video}` | Absolute path to `badapple.mp4` |
| `{lib}` | Absolute path to `test_lib/` directory |
| `{frames}` | Number of test frames (from `test_frames`) |
| `{width}` / `{height}` | Render dimensions (from `render.width`/`render.height`) |
| `{output}` | Absolute path to output `.mov` file |

---

## Running Benchmarks

### Full Suite
```bash
mise run bench          # setup → build → bench → readme
```

### Individual Stages
```bash
mise run bench-arrange  # Arrange only
mise run bench-render   # Render only
mise run bench-encode   # Encode only (full pipeline)
```

### Manual Commands
```bash
# Build a specific implementation
mise run build-c-v1_0_0
mise run build-odin-dev

# Regenerate README from stored results
mise run gen-readme

# Clean generated artifacts
mise run clean
```

---

## Best Practices

### Ensuring Comparable Results

1. **Never change `config.toml` bench parameters between runs** — `test_frames`, `test_pages`, and resolution must stay constant
2. **Run on the same machine** — different CPUs/GPUs produce incomparable results
3. **Close other applications** — background CPU usage affects timing
4. **Run multiple times** — the default 10 runs with hyperfine gives statistical significance
5. **Commit results immediately** — don't lose benchmark data to uncommitted changes

### When Results Seem Wrong

1. **Check the binary** — is it actually built? `file <binary>` should show the right architecture
2. **Check the test library** — does `test_lib/features.bin` exist? Re-run `mise run setup` if not
3. **Check hyperfine** — is it installed? `which hyperfine`
4. **Check for regressions** — compare against previous `results/` entries
5. **Check threading** — some impls need specific CPU features (AVX2, NEON, etc.)

### Common Pitfalls

- **Different CLI flags across implementations**: Some use `--keep-manifests`, others `--features`, others `--registry`. The `config.toml` abstracts this.
- **Hardware encoding variance**: GPU encoding times vary with system load. Use `--no-hw` for CPU-only comparisons.
- **First-run cold start**: The warmup run (default: 1) helps, but disk cache effects can still skew the first timed run.
- **Resolution mismatch**: Always verify the `render.width`/`height` in `config.toml` matches what you intend to benchmark.

---

## Chart System

The README includes auto-generated SVG charts:

### Box Plot Charts
- **By Stage**: Distribution of run times for each stage across all implementations
- **By Implementation**: Distribution of run times for each stage within a single implementation

### Timeline Chart
- Shows performance across benchmark iterations
- X-axis: iteration number (not date) — enables measuring performance across versions
- Y-axis: mean execution time in seconds
- Each line represents one implementation/stage combination

Charts are saved as separate SVG files in `charts/` and referenced via markdown image syntax. GitHub renders these natively.

---

## Extending the System

### Adding a New Stage

1. Add a `[[impl.bench_cmds]]` entry with the new stage name
2. Update `STAGES` list in `scripts/gen_readme.py`
3. Run `mise run gen-readme` to update the README

### Modifying Chart Appearance

- Colors: Edit `COLORS` list in `scripts/gen_readme.py`
- Dimensions: Adjust `width`/`height` in chart functions
- Layout: Modify margins in `svg_box_chart()` or `build_timeline_chart()`

### Custom Test Libraries

The test library generator (`gen_test_lib.py`) creates synthetic pages with 64 visual pattern types. To customize:
- Edit the pattern generators in `gen_test_lib.py`
- Adjust `test_pages` in `config.toml` for library size
- Use `seed` parameter for reproducible libraries

---

## History

| Date | Change | Impact |
|------|--------|--------|
| 2026-07-25 | Initial 8K benchmarks | C 20.7x slower at 8K, Odin 12.8x slower |
| 2026-07-25 | Added timeline chart | Enables tracking performance across versions |
| 2026-07-25 | Fixed GitHub SVG rendering | Charts now display on GitHub pages |
