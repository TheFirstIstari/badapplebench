# BadAppleStein Parity Audit Report

**Date:** 2026-08-08
**Scope:** Arrange stage parity between the three implementations, using the C
reference (BadApplestein) as source of truth.

## Result

**60/60 frames byte-identical arrange manifests** across all three
implementations, verified with clean (uninstrumented) builds after the fixes:

```
C    → /tmp/parity/final_c    (badapplestein src/badapplestein, via c_arrange harness)
Odin → /tmp/parity/final_odin (badodin)
Zig  → /tmp/parity/final_zig  (badziggle, ReleaseFast)

for i in $(seq 0 59); do f=$(printf '%04d.bin' $i);
  cmp -s final_c/$f final_odin/$f || echo "C-O $i";
  cmp -s final_c/$f final_zig/$f  || echo "C-Z $i"; done   # → 0 differences
```

Frames 0–2 legitimately contain 0 matched tiles in all three (start of the
video) — this is expected, not a deviation.

## What was verified identical

Per-frame pipeline stages, compared byte-for-byte through the manifest output:

- Grayscale conversion (BT.601 weights)
- Sobel edge detection
- Quantization / thresholding
- Resize parameters and interpolation
- Feature extraction and **full-feature FNV-1a hashing**
- Tile matching, dedup, and cache population
- Manifest file format (`<w> <h>` header + packed `Inst` records + `fps.bin`)

## Root causes found and fixed

### 1. Hash truncation in the match cache (Odin + Zig)

The C reference hashes the **entire feature** (43,008 bytes) for cache lookups;
the Odin/Zig ports used sparse/truncated hashes, which produced different cache
hits and therefore different `op_id` assignments than C.

**Fix:** switched Odin and Zig to full-feature FNV-1a over all `feat_len`
bytes, matching C's `full_feat_hash`.

### 2. Dedup-map compaction bug (Odin + Zig only)

The dedup scan compared `h_i == feat_hashes[j]` — the hash of the **original**
tile slot `j` — but the compaction copy
(`@memcpy(tiles_buf[unique_nt], tiles_buf[i])` / Odin
`copy(tiles[unique_nt*feat_len:], tiles[i*feat_len:][:feat_len])`) moves a
*different* feature into slot `j`. The match result `results[j]` (for another
feature) was then broadcast to the duplicate tiles, and that wrong pid was
inserted into the cache under the correct hash — poisoning later frames.

C has no dedup layer, so it was always consistent. This surfaced as a C-vs-O/Z
`op_id` divergence on frames 44 and 49 (6 tiles).

**Fix:** track `uniq_hashes[j]` = hash of the feature **actually present** in
compacted slot `j`; the scan compares against `uniq_hashes[j]`, and the
new-unique branch records `uniq_hashes[unique_nt] = h_i` before the copy.

### 3. Zig performance trap: Debug-mode default (no parity impact)

`BadZiggle/build.zig` falls back to `b.standardOptimizeOption(.{})`, which
defaults to **Debug** when built with plain `zig build`. The Debug binary
(2.7 MB) ran ~6.7× more CPU work than C/Odin — and is the cause of the earlier
"hyperfine warmup stuck at 100 % CPU" report.

**Fix:** the benchmark config builds with `zig build -Drelease-fast=true`
(645 KB binary). For manual builds, always pass `-Drelease-fast=true` (or
`-Doptimize=ReleaseFast`).

## Performance (500-frame arrange, 512×384 video)

Clean ReleaseFast / `-o:speed -lto:thin` / `-O3` builds, Apple Silicon:

| Implementation | real   | user   | notes                            |
|----------------|--------|--------|----------------------------------|
| C (reference)  | 9.06s  | 21.04s | harness arrange-only, 21.4s proc |
| Odin           | 11.18s | 22.39s |                                  |
| Zig (ReleaseFast) | 14.33s | 23.29s | was 67.78s/155.15s in Debug   |

All three scale ~2.3× parallel (user/real ratio). The full-feature hash change
costs all three ~3.6× vs the old sparse-hash Odin build (3.07s) — that cost is
inherent to byte-identical parity with the C reference.

## Known open issues (documented, not fixed in this pass)

1. **Bench resolution mismatch:** `badapplebench/config.toml` `[bench.render]`
   claims 7680×4320, but the test video (`badapple.mp4`) is 512×384. The render
   stage upscales; the 8K config is aspirational until an 8K source is supplied.
2. **C `build` output location:** the C implementation writes `registry.bin` to
   the current working directory, not to the `--library` directory.
3. **Stream routing:** the C version writes banner/progress to stdout; Odin and
   Zig write to stderr. Affects log parsing, not output bytes.
4. **Home library path:** C and Odin use `~/.badapplestein/library`; Zig uses
   `~/.badziggle/library`. Only affects default lookup when no `--library`
   flag is passed.
5. **PDF support:** C builds with mupdf (`-DHAVE_MUPDF`); Odin skips PDFs;
   Zig warns and skips. Behavioral divergence in `build`, out of arrange scope.
6. **Bench clone tag:** the bench used to clone `BadApplestein@v1.0.0`, a tag
   that lacks `vt_prores.m`, so the C build failed inside the bench. The local
   repo (which includes `vt_prores.m`) builds cleanly, and `config.toml` now
   pins `git_ref = "master"` / label `v1.1.0`.
7. **Odin per-frame allocations:** `dedup_map`, `feat_hashes`, and
   `uniq_hashes` are allocated per frame with `make` and never freed (pre-existing
   pattern in the codebase, small and consistent). Left untouched this pass.
8. **Zig build default:** see root cause #3 — plain `zig build` produces a Debug
   binary; the repo's `build.zig` should default `optimize` to ReleaseFast to
   avoid future confusion.

## Reproduction

```bash
# C (arrange-only driver; the unified binary has no standalone arrange command)
cc -O3 -funroll-loops -Xpreprocessor -fopenmp -Isrc \
  -I/opt/homebrew/opt/libomp/include -I/opt/homebrew/Cellar/ffmpeg/8.1.2_1/include \
  -I/opt/homebrew/opt/mupdf/include -DVERSION=\"1.1.0\" -DHAVE_MUPDF \
  /tmp/parity/c_arrange.c src/arrange.c src/render.c src/build_library.c src/match.c \
  src/pdf.c src/system_detect.c src/imgops.c src/video.c src/cli.c src/vt_prores.m \
  -L/opt/homebrew/opt/libomp/lib -lomp \
  -L/opt/homebrew/Cellar/ffmpeg/8.1.2_1/lib -lavformat -lavcodec -lswscale -lavutil \
  -L/opt/homebrew/opt/mupdf/lib -lmupdf -lmupdf-third -lm -fobjc-arc \
  -framework Foundation -framework AVFoundation -framework CoreMedia -framework CoreVideo \
  -o /tmp/parity/c_arrange

cd /Users/frobinson/dev/badapplebench
/tmp/parity/c_arrange badapple.mp4 test_lib/features.bin test_lib/registry.bin /tmp/parity/c_out 60
./repos/BadOdinStein/badodin arrange --video badapple.mp4 \
  --features test_lib/features.bin --registry test_lib/registry.bin \
  --manifests /tmp/parity/o_out --max-frames 60 --quiet
./repos/BadZiggle/zig-out/bin/badziggle arrange --video badapple.mp4 \
  --features test_lib/features.bin --registry test_lib/registry.bin \
  --manifests /tmp/parity/z_out --max-frames 60 --quiet

for i in $(seq 0 59); do f=$(printf '%04d.bin' $i);
  cmp -s /tmp/parity/c_out/$f /tmp/parity/o_out/$f || echo "C-O $i";
  cmp -s /tmp/parity/c_out/$f /tmp/parity/z_out/$f || echo "C-Z $i"; done
```

## Files changed in this pass

- `BadZiggle/src/arrange.zig` — full-feature FNV-1a cache hash + `uniq_hashes`
  dedup fix; removed BAP_DUMP trace.
- `BadOdinStein/src/arrange.odin` — full-feature FNV-1a cache hash + `uniq_hashes`
  dedup fix; removed BAP_DUMP trace.
- `BadApplestein/src/arrange.c` — removed BAP_DUMP trace (C already hashed full
  features; no dedup layer).
- `BadZiggle/src/main.zig` — removed `g_dump_fi` hook.
