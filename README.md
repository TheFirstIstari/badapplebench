# badapplebench

Cross-language performance benchmarks for [BadAppleStein](https://github.com/TheFirstIstari/BadApplestein) implementations.

Compares arrangement, rendering, and encoding performance across C and Odin (more languages coming).

## Quick Start

```bash
# Install dependencies (mise + hyperfine)
brew install mise hyperfine

# Run full benchmark suite (builds all impls, benchmarks all stages, updates README)
mise run bench
```

## What Gets Benchmarked

Each implementation is benchmarked on three stages using [hyperfine](https://github.com/sharkdp/hyperfine):

| Stage | Description |
|-------|-------------|
| **Arrange** | Decode video frames, match tiles against source library, write manifests |
| **Render** | Assemble frames from manifests, encode output video |
| **Encode** | Full pipeline (arrange + render) end-to-end |

All benchmarks use a standardized test library (2000 pages, 200 frames from badapple.mp4) for fair comparison.

## Adding a New Implementation

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
   ```
2. Run `mise run bench`

That's it. The benchmark infrastructure handles cloning, building, testing, and README generation automatically.

## Tasks

| Task | Description |
|------|-------------|
| `mise run bench` | Full benchmark suite (build → bench → README) |
| `mise run setup` | Clone repos + generate test library |
| `mise run build-all` | Build all implementations |
| `mise run bench-arrange` | Benchmark arrange stage only |
| `mise run bench-render` | Benchmark render stage only |
| `mise run bench-encode` | Benchmark encode stage only |
| `mise run gen-readme` | Regenerate README from stored results |
| `mise run clean` | Remove test_lib/ and repos/ |

## Results

Results are stored as hyperfine JSON in `results/` (git-tracked) for historical comparison. The README is auto-generated from these results.

<!-- BENCHMARKS_START -->
_No benchmark results yet. Run `mise run bench` to generate._
<!-- BENCHMARKS_END -->

## Project Structure

```
badapplebench/
├── config.toml          # Implementation registry (add new langs here)
├── mise.toml            # Task definitions
├── gen_test_lib.py      # Test library generator (from BadApplestein)
├── scripts/
│   ├── setup_impls.sh   # Clone repos, generate test lib
│   ├── build_impl.sh    # Build a specific implementation
│   ├── bench.sh         # Run hyperfine for one impl+stage
│   ├── run_all.sh       # Full orchestration
│   └── gen_readme.py    # README generator from results
├── results/             # Historical hyperfine outputs (git-tracked)
├── repos/               # Cloned source repos (gitignored)
└── test_lib/            # Generated test library (gitignored)
```

## Requirements

- [mise](https://mise.jdx.dev/) — tool version manager
- [hyperfine](https://github.com/sharkdp/hyperfine) — benchmarking tool
- Python 3.12+ (managed by mise)
- C compiler (clang/gcc) with ffmpeg/libav
- Odin compiler (for Odin implementations)

## License

MIT
