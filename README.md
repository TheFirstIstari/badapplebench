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
### Latest Benchmarks (2026-07-25)

| Language | Version | Arrange (s) | Render (s) | Encode (s) | Git Commit |
|----------|---------|-------------|------------|------------|------------|
| c | v0.2.0 | 3.46 ± 0.02 | — | — | af01720 |
| c | v1.0.0 | **1.56 ± 0.01** | — | **1.61 ± 0.04** | 157ae38 |
| c | v1.0.0-8k | — | — | 33.28 ± 0.76 | 157ae38 |
| odin | dev | 5.70 ± 0.06 | **15.81 ± 0.25** | 21.50 ± 0.18 | 2c68846 |
| odin | dev-8k | — | — | 275.75 ± 1.47 | 8da1a95 |

### Performance Distribution by Stage

<svg xmlns="http://www.w3.org/2000/svg" width="520" height="260" viewBox="0 0 520 260" style="max-width:100%;height:auto;font-family:system-ui,sans-serif">
<rect width="520" height="260" fill="white" rx="4"/>
<text x="260.0" y="18" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">Distribution: Arrange</text>
<line x1="60" y1="200.0" x2="500" y2="200.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="204.0" text-anchor="end" font-size="10" fill="#64748b">0.0s</text>
<line x1="60" y1="166.0" x2="500" y2="166.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="170.0" text-anchor="end" font-size="10" fill="#64748b">1.3s</text>
<line x1="60" y1="132.0" x2="500" y2="132.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="136.0" text-anchor="end" font-size="10" fill="#64748b">2.5s</text>
<line x1="60" y1="98.0" x2="500" y2="98.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="102.0" text-anchor="end" font-size="10" fill="#64748b">3.8s</text>
<line x1="60" y1="63.99999999999997" x2="500" y2="63.99999999999997" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="67.99999999999997" text-anchor="end" font-size="10" fill="#64748b">5.1s</text>
<line x1="60" y1="30.0" x2="500" y2="30.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="34.0" text-anchor="end" font-size="10" fill="#64748b">6.3s</text>
<text x="133.33333333333331" y="216" text-anchor="middle" font-size="10" fill="#475569">c/v0.2.0</text>
<line x1="133.33333333333331" y1="107.82498080178902" x2="133.33333333333331" y2="107.61395397319332" stroke="#2563eb" stroke-width="1.5"/>
<line x1="133.33333333333331" y1="106.96400925690948" x2="133.33333333333331" y2="106.32869487583345" stroke="#2563eb" stroke-width="1.5"/>
<line x1="121.33333333333331" y1="107.82498080178902" x2="145.33333333333331" y2="107.82498080178902" stroke="#2563eb" stroke-width="1.5"/>
<line x1="121.33333333333331" y1="106.32869487583345" x2="145.33333333333331" y2="106.32869487583345" stroke="#2563eb" stroke-width="1.5"/>
<rect x="113.33333333333331" y="106.96400925690948" width="40" height="0.6499447162838408" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="113.33333333333331" y1="107.31446905362583" x2="153.33333333333331" y2="107.31446905362583" stroke="#2563eb" stroke-width="2"/>
<text x="280.0" y="216" text-anchor="middle" font-size="10" fill="#475569">c/v1.0.0</text>
<line x1="280.0" y1="158.8712728999584" x2="280.0" y2="158.46267174882547" stroke="#2563eb" stroke-width="1.5"/>
<line x1="280.0" y1="158.16833179918268" x2="280.0" y2="157.7268218747185" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="158.8712728999584" x2="292.0" y2="158.8712728999584" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="157.7268218747185" x2="292.0" y2="157.7268218747185" stroke="#2563eb" stroke-width="1.5"/>
<rect x="260.0" y="158.16833179918268" width="40" height="0.2943399496427901" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="260.0" y1="158.289499162572" x2="300.0" y2="158.289499162572" stroke="#2563eb" stroke-width="2"/>
<circle cx="280.0" cy="157.53787742504036" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
<text x="426.66666666666663" y="216" text-anchor="middle" font-size="10" fill="#475569">odin/dev</text>
<line x1="426.66666666666663" y1="50.12317455578514" x2="426.66666666666663" y2="47.634156943159525" stroke="#2563eb" stroke-width="1.5"/>
<line x1="426.66666666666663" y1="45.97481186807579" x2="426.66666666666663" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<line x1="414.66666666666663" y1="50.12317455578514" x2="438.66666666666663" y2="50.12317455578514" stroke="#2563eb" stroke-width="1.5"/>
<line x1="414.66666666666663" y1="45.45454545454547" x2="438.66666666666663" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<rect x="406.66666666666663" y="45.97481186807579" width="40" height="1.6593450750837349" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="406.66666666666663" y1="46.59471030115037" x2="446.66666666666663" y2="46.59471030115037" stroke="#2563eb" stroke-width="2"/>
<circle cx="426.66666666666663" cy="50.25450340441253" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
</svg>

<svg xmlns="http://www.w3.org/2000/svg" width="520" height="260" viewBox="0 0 520 260" style="max-width:100%;height:auto;font-family:system-ui,sans-serif">
<rect width="520" height="260" fill="white" rx="4"/>
<text x="260.0" y="18" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">Distribution: Render</text>
<line x1="60" y1="200.0" x2="500" y2="200.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="204.0" text-anchor="end" font-size="10" fill="#64748b">0.0s</text>
<line x1="60" y1="166.0" x2="500" y2="166.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="170.0" text-anchor="end" font-size="10" fill="#64748b">3.6s</text>
<line x1="60" y1="132.0" x2="500" y2="132.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="136.0" text-anchor="end" font-size="10" fill="#64748b">7.2s</text>
<line x1="60" y1="98.0" x2="500" y2="98.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="102.0" text-anchor="end" font-size="10" fill="#64748b">10.7s</text>
<line x1="60" y1="64.0" x2="500" y2="64.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="68.0" text-anchor="end" font-size="10" fill="#64748b">14.3s</text>
<line x1="60" y1="30.0" x2="500" y2="30.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="34.0" text-anchor="end" font-size="10" fill="#64748b">17.9s</text>
<text x="280.0" y="216" text-anchor="middle" font-size="10" fill="#475569">odin/dev</text>
<line x1="280.0" y1="52.84651451115599" x2="280.0" y2="51.19981752824842" stroke="#2563eb" stroke-width="1.5"/>
<line x1="280.0" y1="47.60799978864" x2="280.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="52.84651451115599" x2="292.0" y2="52.84651451115599" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="45.45454545454547" x2="292.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<rect x="260.0" y="47.60799978864" width="40" height="3.591817739608416" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="260.0" y1="50.64758724083265" x2="300.0" y2="50.64758724083265" stroke="#2563eb" stroke-width="2"/>
</svg>

<svg xmlns="http://www.w3.org/2000/svg" width="520" height="260" viewBox="0 0 520 260" style="max-width:100%;height:auto;font-family:system-ui,sans-serif">
<rect width="520" height="260" fill="white" rx="4"/>
<text x="260.0" y="18" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">Distribution: Encode</text>
<line x1="60" y1="200.0" x2="500" y2="200.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="204.0" text-anchor="end" font-size="10" fill="#64748b">0.0s</text>
<line x1="60" y1="166.0" x2="500" y2="166.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="170.0" text-anchor="end" font-size="10" fill="#64748b">60.9s</text>
<line x1="60" y1="132.0" x2="500" y2="132.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="136.0" text-anchor="end" font-size="10" fill="#64748b">121.8s</text>
<line x1="60" y1="98.00000000000001" x2="500" y2="98.00000000000001" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="102.00000000000001" text-anchor="end" font-size="10" fill="#64748b">182.7s</text>
<line x1="60" y1="64.0" x2="500" y2="64.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="68.0" text-anchor="end" font-size="10" fill="#64748b">243.6s</text>
<line x1="60" y1="30.00000000000003" x2="500" y2="30.00000000000003" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="34.00000000000003" text-anchor="end" font-size="10" fill="#64748b">304.5s</text>
<text x="115.0" y="216" text-anchor="middle" font-size="10" fill="#475569">c/v1.0.0</text>
<line x1="115.0" y1="199.11991069946922" x2="115.0" y2="199.11708670039545" stroke="#2563eb" stroke-width="1.5"/>
<line x1="115.0" y1="199.09942989952307" x2="115.0" y2="199.07294469821454" stroke="#2563eb" stroke-width="1.5"/>
<line x1="103.0" y1="199.11991069946922" x2="127.0" y2="199.11991069946922" stroke="#2563eb" stroke-width="1.5"/>
<line x1="103.0" y1="199.07294469821454" x2="127.0" y2="199.07294469821454" stroke="#2563eb" stroke-width="1.5"/>
<rect x="95.0" y="199.09942989952307" width="40" height="0.017656800872373424" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="95.0" y1="199.10978478893313" x2="135.0" y2="199.10978478893313" stroke="#2563eb" stroke-width="2"/>
<circle cx="115.0" cy="199.04572163644576" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
<text x="225.0" y="216" text-anchor="middle" font-size="10" fill="#475569">c/v1.0.0-8k</text>
<line x1="225.0" y1="181.6188652595064" x2="225.0" y2="181.6096747800314" stroke="#2563eb" stroke-width="1.5"/>
<line x1="225.0" y1="181.50778045644654" x2="225.0" y2="181.35493897106926" stroke="#2563eb" stroke-width="1.5"/>
<line x1="213.0" y1="181.6188652595064" x2="237.0" y2="181.6188652595064" stroke="#2563eb" stroke-width="1.5"/>
<line x1="213.0" y1="181.35493897106926" x2="237.0" y2="181.35493897106926" stroke="#2563eb" stroke-width="1.5"/>
<rect x="205.0" y="181.50778045644654" width="40" height="0.10189432358487238" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="205.0" y1="181.5648903281858" x2="245.0" y2="181.5648903281858" stroke="#2563eb" stroke-width="2"/>
<circle cx="225.0" cy="181.32121403467409" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
<circle cx="225.0" cy="180.23808128848248" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
<text x="335.0" y="216" text-anchor="middle" font-size="10" fill="#475569">odin/dev</text>
<line x1="335.0" y1="188.13541302539528" x2="335.0" y2="188.06836141062414" stroke="#2563eb" stroke-width="1.5"/>
<line x1="335.0" y1="187.9495891649942" x2="335.0" y2="187.81741789378435" stroke="#2563eb" stroke-width="1.5"/>
<line x1="323.0" y1="188.13541302539528" x2="347.0" y2="188.13541302539528" stroke="#2563eb" stroke-width="1.5"/>
<line x1="323.0" y1="187.81741789378435" x2="347.0" y2="187.81741789378435" stroke="#2563eb" stroke-width="1.5"/>
<rect x="315.0" y="187.9495891649942" width="40" height="0.11877224562994115" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="315.0" y1="188.01797316505332" x2="355.0" y2="188.01797316505332" stroke="#2563eb" stroke-width="2"/>
<text x="445.0" y="216" text-anchor="middle" font-size="10" fill="#475569">odin/dev-8k</text>
<line x1="445.0" y1="46.61036990323788" x2="445.0" y2="46.61036990323788" stroke="#2563eb" stroke-width="1.5"/>
<line x1="445.0" y1="45.45454545454547" x2="445.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<line x1="433.0" y1="46.61036990323788" x2="457.0" y2="46.61036990323788" stroke="#2563eb" stroke-width="1.5"/>
<line x1="433.0" y1="45.45454545454547" x2="457.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<rect x="425.0" y="45.45454545454547" width="40" height="1.1558244486924139" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="425.0" y1="45.45454545454547" x2="465.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="2"/>
</svg>

### Performance Distribution by Implementation

<svg xmlns="http://www.w3.org/2000/svg" width="520" height="260" viewBox="0 0 520 260" style="max-width:100%;height:auto;font-family:system-ui,sans-serif">
<rect width="520" height="260" fill="white" rx="4"/>
<text x="260.0" y="18" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">c/v0.2.0 — All Stages</text>
<line x1="60" y1="200.0" x2="500" y2="200.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="204.0" text-anchor="end" font-size="10" fill="#64748b">0.0s</text>
<line x1="60" y1="166.0" x2="500" y2="166.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="170.0" text-anchor="end" font-size="10" fill="#64748b">0.8s</text>
<line x1="60" y1="132.0" x2="500" y2="132.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="136.0" text-anchor="end" font-size="10" fill="#64748b">1.5s</text>
<line x1="60" y1="98.0" x2="500" y2="98.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="102.0" text-anchor="end" font-size="10" fill="#64748b">2.3s</text>
<line x1="60" y1="64.0" x2="500" y2="64.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="68.0" text-anchor="end" font-size="10" fill="#64748b">3.1s</text>
<line x1="60" y1="29.99999999999997" x2="500" y2="29.99999999999997" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="33.99999999999997" text-anchor="end" font-size="10" fill="#64748b">3.8s</text>
<text x="280.0" y="216" text-anchor="middle" font-size="10" fill="#475569">arrange</text>
<line x1="280.0" y1="47.92322236953288" x2="280.0" y2="47.57505558458868" stroke="#2563eb" stroke-width="1.5"/>
<line x1="280.0" y1="46.50273144568234" x2="280.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="47.92322236953288" x2="292.0" y2="47.92322236953288" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="45.45454545454547" x2="292.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<rect x="260.0" y="46.50273144568234" width="40" height="1.072324138906339" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="260.0" y1="47.08094446952825" x2="300.0" y2="47.08094446952825" stroke="#2563eb" stroke-width="2"/>
</svg>

<svg xmlns="http://www.w3.org/2000/svg" width="520" height="260" viewBox="0 0 520 260" style="max-width:100%;height:auto;font-family:system-ui,sans-serif">
<rect width="520" height="260" fill="white" rx="4"/>
<text x="260.0" y="18" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">c/v1.0.0 — All Stages</text>
<line x1="60" y1="200.0" x2="500" y2="200.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="204.0" text-anchor="end" font-size="10" fill="#64748b">0.0s</text>
<line x1="60" y1="166.0" x2="500" y2="166.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="170.0" text-anchor="end" font-size="10" fill="#64748b">0.4s</text>
<line x1="60" y1="132.0" x2="500" y2="132.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="136.0" text-anchor="end" font-size="10" fill="#64748b">0.8s</text>
<line x1="60" y1="98.0" x2="500" y2="98.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="102.0" text-anchor="end" font-size="10" fill="#64748b">1.1s</text>
<line x1="60" y1="63.99999999999997" x2="500" y2="63.99999999999997" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="67.99999999999997" text-anchor="end" font-size="10" fill="#64748b">1.5s</text>
<line x1="60" y1="30.0" x2="500" y2="30.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="34.0" text-anchor="end" font-size="10" fill="#64748b">1.9s</text>
<text x="170.0" y="216" text-anchor="middle" font-size="10" fill="#475569">arrange</text>
<line x1="170.0" y1="61.32810921607668" x2="170.0" y2="59.95044697852998" stroke="#2563eb" stroke-width="1.5"/>
<line x1="170.0" y1="58.958034126779694" x2="170.0" y2="57.469414849154305" stroke="#2563eb" stroke-width="1.5"/>
<line x1="158.0" y1="61.32810921607668" x2="182.0" y2="61.32810921607668" stroke="#2563eb" stroke-width="1.5"/>
<line x1="158.0" y1="57.469414849154305" x2="182.0" y2="57.469414849154305" stroke="#2563eb" stroke-width="1.5"/>
<rect x="150.0" y="58.958034126779694" width="40" height="0.9924128517502879" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="150.0" y1="59.366568709958784" x2="190.0" y2="59.366568709958784" stroke="#2563eb" stroke-width="2"/>
<circle cx="170.0" cy="56.832359293647755" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
<text x="390.0" y="216" text-anchor="middle" font-size="10" fill="#475569">encode</text>
<line x1="390.0" y1="57.46946993062778" x2="390.0" y2="57.01212306292217" stroke="#2563eb" stroke-width="1.5"/>
<line x1="390.0" y1="54.15260280043236" x2="390.0" y2="49.86332240669762" stroke="#2563eb" stroke-width="1.5"/>
<line x1="378.0" y1="57.46946993062778" x2="402.0" y2="57.46946993062778" stroke="#2563eb" stroke-width="1.5"/>
<line x1="378.0" y1="49.86332240669762" x2="402.0" y2="49.86332240669762" stroke="#2563eb" stroke-width="1.5"/>
<rect x="370.0" y="54.15260280043236" width="40" height="2.8595202624898093" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="370.0" y1="55.82957793867311" x2="410.0" y2="55.82957793867311" stroke="#2563eb" stroke-width="2"/>
<circle cx="390.0" cy="45.45454545454547" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
</svg>

<svg xmlns="http://www.w3.org/2000/svg" width="520" height="260" viewBox="0 0 520 260" style="max-width:100%;height:auto;font-family:system-ui,sans-serif">
<rect width="520" height="260" fill="white" rx="4"/>
<text x="260.0" y="18" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">c/v1.0.0-8k — All Stages</text>
<line x1="60" y1="200.0" x2="500" y2="200.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="204.0" text-anchor="end" font-size="10" fill="#64748b">0.0s</text>
<line x1="60" y1="166.0" x2="500" y2="166.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="170.0" text-anchor="end" font-size="10" fill="#64748b">7.8s</text>
<line x1="60" y1="132.0" x2="500" y2="132.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="136.0" text-anchor="end" font-size="10" fill="#64748b">15.6s</text>
<line x1="60" y1="98.0" x2="500" y2="98.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="102.0" text-anchor="end" font-size="10" fill="#64748b">23.4s</text>
<line x1="60" y1="64.0" x2="500" y2="64.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="68.0" text-anchor="end" font-size="10" fill="#64748b">31.1s</text>
<line x1="60" y1="30.0" x2="500" y2="30.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="34.0" text-anchor="end" font-size="10" fill="#64748b">38.9s</text>
<text x="280.0" y="216" text-anchor="middle" font-size="10" fill="#475569">encode</text>
<line x1="280.0" y1="56.252782687785384" x2="280.0" y2="56.18090976650234" stroke="#2563eb" stroke-width="1.5"/>
<line x1="280.0" y1="55.38405877324092" x2="280.0" y2="54.188782283348814" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="56.252782687785384" x2="292.0" y2="56.252782687785384" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="54.188782283348814" x2="292.0" y2="54.188782283348814" stroke="#2563eb" stroke-width="1.5"/>
<rect x="260.0" y="55.38405877324092" width="40" height="0.7968509932614154" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="260.0" y1="55.8306789226213" x2="300.0" y2="55.8306789226213" stroke="#2563eb" stroke-width="2"/>
<circle cx="280.0" cy="53.925040907787434" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
<circle cx="280.0" cy="45.45454545454547" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
</svg>

<svg xmlns="http://www.w3.org/2000/svg" width="520" height="260" viewBox="0 0 520 260" style="max-width:100%;height:auto;font-family:system-ui,sans-serif">
<rect width="520" height="260" fill="white" rx="4"/>
<text x="260.0" y="18" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">odin/dev — All Stages</text>
<line x1="60" y1="200.0" x2="500" y2="200.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="204.0" text-anchor="end" font-size="10" fill="#64748b">0.0s</text>
<line x1="60" y1="166.0" x2="500" y2="166.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="170.0" text-anchor="end" font-size="10" fill="#64748b">4.8s</text>
<line x1="60" y1="132.0" x2="500" y2="132.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="136.0" text-anchor="end" font-size="10" fill="#64748b">9.6s</text>
<line x1="60" y1="98.0" x2="500" y2="98.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="102.0" text-anchor="end" font-size="10" fill="#64748b">14.4s</text>
<line x1="60" y1="64.0" x2="500" y2="64.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="68.0" text-anchor="end" font-size="10" fill="#64748b">19.2s</text>
<line x1="60" y1="30.0" x2="500" y2="30.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="34.0" text-anchor="end" font-size="10" fill="#64748b">24.0s</text>
<text x="133.33333333333331" y="216" text-anchor="middle" font-size="10" fill="#475569">arrange</text>
<line x1="133.33333333333331" y1="160.41657363533145" x2="133.33333333333331" y2="159.75920819475903" stroke="#2563eb" stroke-width="1.5"/>
<line x1="133.33333333333331" y1="159.32096456771077" x2="133.33333333333331" y2="159.18355888668603" stroke="#2563eb" stroke-width="1.5"/>
<line x1="121.33333333333331" y1="160.41657363533145" x2="145.33333333333331" y2="160.41657363533145" stroke="#2563eb" stroke-width="1.5"/>
<line x1="121.33333333333331" y1="159.18355888668603" x2="145.33333333333331" y2="159.18355888668603" stroke="#2563eb" stroke-width="1.5"/>
<rect x="113.33333333333331" y="159.32096456771077" width="40" height="0.4382436270482515" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="113.33333333333331" y1="159.48468370111553" x2="153.33333333333331" y2="159.48468370111553" stroke="#2563eb" stroke-width="2"/>
<circle cx="133.33333333333331" cy="160.45125842261456" r="2.5" fill="#2563eb" fill-opacity="0.6"/>
<text x="280.0" y="216" text-anchor="middle" font-size="10" fill="#475569">render</text>
<line x1="280.0" y1="90.2218375136252" x2="280.0" y2="88.9933829625493" stroke="#2563eb" stroke-width="1.5"/>
<line x1="280.0" y1="86.31384635401912" x2="280.0" y2="84.70734509439967" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="90.2218375136252" x2="292.0" y2="90.2218375136252" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="84.70734509439967" x2="292.0" y2="84.70734509439967" stroke="#2563eb" stroke-width="1.5"/>
<rect x="260.0" y="86.31384635401912" width="40" height="2.679536608530185" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="260.0" y1="88.58141292989642" x2="300.0" y2="88.58141292989642" stroke="#2563eb" stroke-width="2"/>
<text x="426.66666666666663" y="216" text-anchor="middle" font-size="10" fill="#475569">encode</text>
<line x1="426.66666666666663" y1="49.488559075761174" x2="426.66666666666663" y2="48.63795760289858" stroke="#2563eb" stroke-width="1.5"/>
<line x1="426.66666666666663" y1="47.13124001805272" x2="426.66666666666663" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<line x1="414.66666666666663" y1="49.488559075761174" x2="438.66666666666663" y2="49.488559075761174" stroke="#2563eb" stroke-width="1.5"/>
<line x1="414.66666666666663" y1="45.45454545454547" x2="438.66666666666663" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<rect x="406.66666666666663" y="47.13124001805272" width="40" height="1.506717584845859" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="406.66666666666663" y1="47.998743826410504" x2="446.66666666666663" y2="47.998743826410504" stroke="#2563eb" stroke-width="2"/>
</svg>

<svg xmlns="http://www.w3.org/2000/svg" width="520" height="260" viewBox="0 0 520 260" style="max-width:100%;height:auto;font-family:system-ui,sans-serif">
<rect width="520" height="260" fill="white" rx="4"/>
<text x="260.0" y="18" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">odin/dev-8k — All Stages</text>
<line x1="60" y1="200.0" x2="500" y2="200.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="204.0" text-anchor="end" font-size="10" fill="#64748b">0.0s</text>
<line x1="60" y1="166.0" x2="500" y2="166.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="170.0" text-anchor="end" font-size="10" fill="#64748b">60.9s</text>
<line x1="60" y1="132.0" x2="500" y2="132.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="136.0" text-anchor="end" font-size="10" fill="#64748b">121.8s</text>
<line x1="60" y1="98.00000000000001" x2="500" y2="98.00000000000001" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="102.00000000000001" text-anchor="end" font-size="10" fill="#64748b">182.7s</text>
<line x1="60" y1="64.0" x2="500" y2="64.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="68.0" text-anchor="end" font-size="10" fill="#64748b">243.6s</text>
<line x1="60" y1="30.00000000000003" x2="500" y2="30.00000000000003" stroke="#e2e8f0" stroke-width="1"/>
<text x="54" y="34.00000000000003" text-anchor="end" font-size="10" fill="#64748b">304.5s</text>
<text x="280.0" y="216" text-anchor="middle" font-size="10" fill="#475569">encode</text>
<line x1="280.0" y1="46.61036990323788" x2="280.0" y2="46.61036990323788" stroke="#2563eb" stroke-width="1.5"/>
<line x1="280.0" y1="45.45454545454547" x2="280.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="46.61036990323788" x2="292.0" y2="46.61036990323788" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.0" y1="45.45454545454547" x2="292.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="1.5"/>
<rect x="260.0" y="45.45454545454547" width="40" height="1.1558244486924139" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<line x1="260.0" y1="45.45454545454547" x2="300.0" y2="45.45454545454547" stroke="#2563eb" stroke-width="2"/>
</svg>

### History

| Date       | Language | Version | Arrange (s) | Render (s) | Encode (s) |
|------------|----------|---------|-------------|------------|------------|
| 2026-07-25 | c | v0.2.0 | 3.46 | — | — |
| 2026-07-25 | c | v1.0.0 | 1.56 | — | 1.61 |
| 2026-07-25 | c | v1.0.0-8k | — | — | 33.28 |
| 2026-07-25 | odin | dev | 5.70 | 15.81 | 21.50 |
| 2026-07-25 | odin | dev-8k | — | — | 275.75 |
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
