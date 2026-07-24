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

    replacement = latest_table + "\n" + history_table if history_table else latest_table

    new_content = content.split(MARKER_START)[0]
    new_content += MARKER_START + "\n"
    new_content += replacement
    new_content += MARKER_END + content.split(MARKER_END)[1]

    README.write_text(new_content)
    print(f"README.md updated with benchmark results ({len(entries)} entries).")


if __name__ == "__main__":
    main()
