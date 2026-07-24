#!/usr/bin/env python3
"""Regenerate README.md benchmark tables from results/ directory."""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
README = ROOT / "README.md"

MARKER_START = "<!-- BENCHMARKS_START -->"
MARKER_END = "<!-- BENCHMARKS_END -->"

DIR_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}_([^_]+)_(.+)$")
STAGES = ["arrange", "render", "encode"]


def parse_results():
    """Scan results/ and return all benchmark entries."""
    if not RESULTS_DIR.is_dir():
        return []

    entries = []
    for d in sorted(RESULTS_DIR.iterdir()):
        if not d.is_dir():
            continue
        m = DIR_PATTERN.match(d.name)
        if not m:
            continue

        meta_path = d / "meta.json"
        if not meta_path.is_file():
            print(f"Warning: skipping {d.name} (no meta.json)", file=sys.stderr)
            continue

        with open(meta_path) as f:
            meta = json.load(f)

        lang = meta.get("lang", m.group(1))
        label = meta.get("label", m.group(2))
        date = meta.get("date", m.group(0).split("_")[0])
        git_commit = meta.get("git_commit", "")[:7]

        stage_data = {}
        for stage in STAGES:
            stage_file = d / f"{stage}.json"
            if stage_file.is_file():
                with open(stage_file) as f:
                    hf = json.load(f)
                results = hf.get("results", [])
                if results:
                    r = results[0]
                    stage_data[stage] = {
                        "mean": r.get("mean", 0),
                        "stddev": r.get("stddev", 0),
                        "times": r.get("times", []),
                    }

        entries.append({
            "lang": lang,
            "label": label,
            "date": date,
            "git_commit": git_commit,
            "stages": stage_data,
        })

    return entries


def latest_per_combo(entries):
    """Return the latest entry per (lang, label) by date."""
    best = {}
    for e in entries:
        key = (e["lang"], e["label"])
        if key not in best or e["date"] > best[key]["date"]:
            best[key] = e
    return sorted(best.values(), key=lambda e: e["lang"])


def fmt_time(stage_data, key):
    """Format mean ± stddev, or return '—'."""
    if key not in stage_data:
        return "—"
    v = stage_data[key]
    return f"{v['mean']:.2f} ± {v['stddev']:.2f}"


def fmt_time_plain(stage_data, key):
    """Format mean only (for history), or return '—'."""
    if key not in stage_data:
        return "—"
    return f"{stage_data[key]['mean']:.2f}"


def bold_if_fastest(val, fastest_map, stage_key):
    """Wrap value in **bold** if it's the fastest for that stage."""
    if val == "—":
        return val
    if stage_key in fastest_map and val == fastest_map[stage_key]:
        return f"**{val}**"
    return val


def find_fastest(entries, stage):
    """Find the fastest mean for a given stage across all latest entries."""
    times = {}
    for e in entries:
        if stage in e["stages"]:
            times[e["stages"][stage]["mean"]] = fmt_time(e["stages"], stage)
    if not times:
        return {}
    min_time = min(times.keys())
    return {stage: times[min_time]}


# ── Box plot SVG generation ──

def box_stats(values):
    """Compute box plot statistics from a list of values."""
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    q1 = s[n // 4]
    median = s[n // 2]
    q3 = s[(3 * n) // 4]
    iqr = q3 - q1
    whisker_lo = max(s[0], q1 - 1.5 * iqr)
    whisker_hi = min(s[-1], q3 + 1.5 * iqr)
    outliers = [v for v in s if v < whisker_lo or v > whisker_hi]
    return {
        "min": s[0],
        "q1": q1,
        "median": median,
        "q3": q3,
        "max": s[-1],
        "whisker_lo": whisker_lo,
        "whisker_hi": whisker_hi,
        "outliers": outliers,
    }


def svg_box_plot(stats, x_center, box_width, y_scale, y_offset, color):
    """Return SVG elements for a single box plot centered at x_center."""
    if stats is None:
        return ""

    def y(val):
        return y_offset - val * y_scale

    half = box_width / 2
    q1_y = y(stats["q1"])
    q3_y = y(stats["q3"])
    med_y = y(stats["median"])
    wl_y = y(stats["whisker_lo"])
    wh_y = y(stats["whisker_hi"])

    lines = []
    # Whisker lines
    lines.append(f'<line x1="{x_center}" y1="{wl_y}" x2="{x_center}" y2="{q1_y}" stroke="{color}" stroke-width="1.5"/>')
    lines.append(f'<line x1="{x_center}" y1="{q3_y}" x2="{x_center}" y2="{wh_y}" stroke="{color}" stroke-width="1.5"/>')
    # Whisker caps
    cap = box_width * 0.3
    lines.append(f'<line x1="{x_center - cap}" y1="{wl_y}" x2="{x_center + cap}" y2="{wl_y}" stroke="{color}" stroke-width="1.5"/>')
    lines.append(f'<line x1="{x_center - cap}" y1="{wh_y}" x2="{x_center + cap}" y2="{wh_y}" stroke="{color}" stroke-width="1.5"/>')
    # Box
    lines.append(f'<rect x="{x_center - half}" y="{q3_y}" width="{box_width}" height="{q1_y - q3_y}" fill="{color}" fill-opacity="0.25" stroke="{color}" stroke-width="1.5"/>')
    # Median line
    lines.append(f'<line x1="{x_center - half}" y1="{med_y}" x2="{x_center + half}" y2="{med_y}" stroke="{color}" stroke-width="2"/>')
    # Outliers
    for o in stats["outliers"]:
        oy = y(o)
        lines.append(f'<circle cx="{x_center}" cy="{oy}" r="2.5" fill="{color}" fill-opacity="0.6"/>')
    return "\n".join(lines)


COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2", "#be185d", "#4f46e5"]


def svg_box_chart(title, labels, data_series, width=520, height=260):
    """Generate an SVG chart with multiple box plots.

    labels: list of category names (x-axis)
    data_series: list of (series_name, list_of_times_per_category)
    """
    if not labels or not any(data_series):
        return ""

    # Compute global y range
    all_vals = []
    for _, cat_data in data_series:
        for times in cat_data:
            if times:
                all_vals.extend(times)
    if not all_vals:
        return ""

    y_min = 0
    y_max = max(all_vals) * 1.1
    if y_max == 0:
        y_max = 1

    margin_left = 60
    margin_right = 20
    margin_top = 30
    margin_bottom = 60
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    y_scale = plot_h / (y_max - y_min)
    y_offset = margin_top + plot_h

    n_cats = len(labels)
    n_series = len(data_series)
    group_w = plot_w / n_cats
    box_w = min(group_w / (n_series + 1), 40)

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="max-width:100%;height:auto;font-family:system-ui,sans-serif">')
    # Background
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="white" rx="4"/>')
    # Title
    svg_parts.append(f'<text x="{width / 2}" y="18" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">{title}</text>')

    # Y-axis ticks
    n_ticks = 5
    for i in range(n_ticks + 1):
        val = y_min + (y_max - y_min) * i / n_ticks
        ty = y_offset - val * y_scale
        svg_parts.append(f'<line x1="{margin_left}" y1="{ty}" x2="{width - margin_right}" y2="{ty}" stroke="#e2e8f0" stroke-width="1"/>')
        svg_parts.append(f'<text x="{margin_left - 6}" y="{ty + 4}" text-anchor="end" font-size="10" fill="#64748b">{val:.1f}s</text>')

    # Box plots per category
    for ci, label in enumerate(labels):
        cx = margin_left + group_w * ci + group_w / 2
        # X-axis label
        svg_parts.append(f'<text x="{cx}" y="{height - margin_bottom + 16}" text-anchor="middle" font-size="10" fill="#475569">{label}</text>')
        # Boxes for each series
        for si, (series_name, cat_data) in enumerate(data_series):
            times = cat_data[ci] if ci < len(cat_data) else []
            stats = box_stats(times)
            offset = (si - (n_series - 1) / 2) * (box_w + 4)
            color = COLORS[si % len(COLORS)]
            svg_parts.append(svg_box_plot(stats, cx + offset, box_w, y_scale, y_offset, color))

    # Legend
    if n_series > 1:
        lx = margin_left + 8
        ly = height - 10
        for si, (series_name, _) in enumerate(data_series):
            color = COLORS[si % len(COLORS)]
            svg_parts.append(f'<rect x="{lx}" y="{ly - 8}" width="10" height="10" fill="{color}" fill-opacity="0.25" stroke="{color}" stroke-width="1"/>')
            svg_parts.append(f'<text x="{lx + 14}" y="{ly}" font-size="9" fill="#475569">{series_name}</text>')
            lx += len(series_name) * 6 + 28

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def build_stage_charts(entries):
    """Build per-stage box plot charts — one chart per stage, all implementations."""
    latest = latest_per_combo(entries)
    if not latest:
        return ""

    charts = []
    for stage in STAGES:
        labels = []
        data = []
        for e in latest:
            if stage in e["stages"] and e["stages"][stage].get("times"):
                labels.append(f"{e['lang']}/{e['label']}")
                data.append(e["stages"][stage]["times"])
        if not labels:
            continue
        series = [("All runs", data)]
        svg = svg_box_chart(f"Distribution: {stage.capitalize()}", labels, series)
        if svg:
            charts.append(svg)

    if not charts:
        return ""
    return "### Performance Distribution by Stage\n\n" + "\n\n".join(charts) + "\n"


def build_impl_charts(entries):
    """Build per-implementation box plot charts — one chart per impl, all stages."""
    latest = latest_per_combo(entries)
    if not latest:
        return ""

    charts = []
    for e in latest:
        cat_labels = []
        cat_data = []
        for stage in STAGES:
            if stage in e["stages"] and e["stages"][stage].get("times"):
                cat_labels.append(stage)
                cat_data.append(e["stages"][stage]["times"])
        if not cat_labels:
            continue
        series = [(f"{e['lang']}/{e['label']}", cat_data)]
        svg = svg_box_chart(f"{e['lang']}/{e['label']} — All Stages", cat_labels, series)
        if svg:
            charts.append(svg)

    if not charts:
        return ""
    return "### Performance Distribution by Implementation\n\n" + "\n\n".join(charts) + "\n"


def build_latest_table(entries):
    """Build the latest benchmarks markdown table."""
    if not entries:
        return "_No benchmark results yet. Run `mise run bench` to generate._\n"

    latest = latest_per_combo(entries)

    # Find fastest per stage
    fastest = {}
    for stage in STAGES:
        fastest.update(find_fastest(latest, stage))

    # Find overall latest date
    max_date = max(e["date"] for e in latest)

    lines = []
    lines.append(f"### Latest Benchmarks ({max_date})\n")
    lines.append("| Language | Version | Arrange (s) | Render (s) | Encode (s) | Git Commit |")
    lines.append("|----------|---------|-------------|------------|------------|------------|")

    for e in latest:
        vals = {}
        for stage in STAGES:
            vals[stage] = bold_if_fastest(fmt_time(e["stages"], stage), fastest, stage)

        line = (
            f"| {e['lang']} "
            f"| {e['label']} "
            f"| {vals['arrange']} "
            f"| {vals['render']} "
            f"| {vals['encode']} "
            f"| {e['git_commit']} |"
        )
        lines.append(line)

    return "\n".join(lines) + "\n"


def build_history_table(entries):
    """Build the full history markdown table."""
    if not entries:
        return ""

    sorted_entries = sorted(entries, key=lambda e: (e["date"], e["lang"]))

    lines = []
    lines.append("### History\n")
    lines.append("| Date       | Language | Version | Arrange (s) | Render (s) | Encode (s) |")
    lines.append("|------------|----------|---------|-------------|------------|------------|")

    for e in sorted_entries:
        line = (
            f"| {e['date']} "
            f"| {e['lang']} "
            f"| {e['label']} "
            f"| {fmt_time_plain(e['stages'], 'arrange')} "
            f"| {fmt_time_plain(e['stages'], 'render')} "
            f"| {fmt_time_plain(e['stages'], 'encode')} |"
        )
        lines.append(line)

    return "\n".join(lines) + "\n"


def main():
    if not README.is_file():
        print(f"Warning: {README} not found", file=sys.stderr)
        sys.exit(1)

    content = README.read_text()

    if MARKER_START not in content or MARKER_END not in content:
        print(f"Warning: markers not found in {README}", file=sys.stderr)
        sys.exit(1)

    entries = parse_results()

    latest_table = build_latest_table(entries)
    history_table = build_history_table(entries)
    stage_charts = build_stage_charts(entries)
    impl_charts = build_impl_charts(entries)

    parts = [latest_table]
    if stage_charts:
        parts.append(stage_charts)
    if impl_charts:
        parts.append(impl_charts)
    if history_table:
        parts.append(history_table)

    replacement = "\n".join(parts)

    new_content = content.split(MARKER_START)[0]
    new_content += MARKER_START + "\n"
    new_content += replacement
    new_content += MARKER_END + content.split(MARKER_END)[1]

    README.write_text(new_content)
    print(f"README.md updated with benchmark results ({len(entries)} entries).")


if __name__ == "__main__":
    main()
