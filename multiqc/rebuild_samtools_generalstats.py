#!/usr/bin/env python3
"""Create color-scaled MultiQC tables from staged Samtools flagstat files."""

import csv
import json
import re
import sys
from pathlib import Path


FLAGSTAT_PATTERNS = {
    "total": r"(\d+) \+ (\d+) in total \(QC-passed reads \+ QC-failed reads\)",
    "secondary": r"(\d+) \+ (\d+) secondary",
    "supplementary": r"(\d+) \+ (\d+) supplementary",
    "duplicates": r"(\d+) \+ (\d+) duplicates",
    "mapped": r"(\d+) \+ (\d+) mapped \((.+):(.+)\)",
    "paired in sequencing": r"(\d+) \+ (\d+) paired in sequencing",
    "properly paired": r"(\d+) \+ (\d+) properly paired \((.+):(.+)\)",
    "with itself and mate mapped": r"(\d+) \+ (\d+) with itself and mate mapped",
    "singletons": r"(\d+) \+ (\d+) singletons \((.+):(.+)\)",
    "with mate mapped to a different chr": r"(\d+) \+ (\d+) with mate mapped to a different chr",
    "with mate mapped to a different chr (mapQ >= 5)": (
        r"(\d+) \+ (\d+) with mate mapped to a different chr \(mapQ>=5\)"
    ),
}
READS_PER_MILLION = 1_000_000

HEADERS = [
    {
        "flagstat_total_overlay": {
            "title": "M Reads",
            "description": "Total reads in the BAM",
            "min": 0,
            "scale": "GnBu",
            "format": "{:,.2f}",
            "namespace": "FA-NIVA Samtools flagstat",
        }
    },
    {
        "mapped_passed_overlay": {
            "title": "M Reads Mapped",
            "description": "QC-passed reads mapped by samtools flagstat",
            "min": 0,
            "scale": "YlGn",
            "format": "{:,.2f}",
            "namespace": "FA-NIVA Samtools flagstat",
        }
    },
    {
        "mapped_passed_pct_overlay": {
            "title": "% Reads Mapped",
            "description": "Percentage of QC-passed reads mapped by samtools flagstat",
            "min": 0,
            "max": 100,
            "scale": "RdYlGn",
            "format": "{:,.1f}%",
            "namespace": "FA-NIVA Samtools flagstat",
        }
    },
]

TABLE_METRICS = [
    ("flagstat_total", "Total Reads", "GnBu"),
    ("total_passed", "Total Passed QC", "YlGn"),
    ("mapped_passed", "Mapped", "YlGn"),
    ("secondary_passed", "Secondary Alignments", "PuBu"),
    ("supplementary_passed", "Supplementary Alignments", "PuBu"),
    ("duplicates_passed", "Duplicates", "RdYlGn-rev"),
    ("paired in sequencing_passed", "Paired in Sequencing", "GnBu"),
    ("properly paired_passed", "Properly Paired", "YlGn"),
    ("with itself and mate mapped_passed", "Self and mate mapped", "YlGn"),
    ("singletons_passed", "Singletons", "RdYlGn-rev"),
    (
        "with mate mapped to a different chr_passed",
        "Mate mapped to different chr",
        "RdYlGn-rev",
    ),
    (
        "with mate mapped to a different chr (mapQ >= 5)_passed",
        "Mate mapped to different chr (mapQ >= 5)",
        "RdYlGn-rev",
    ),
]


def parse_flagstat(path):
    text = path.read_text()
    values = {}
    for metric, pattern in FLAGSTAT_PATTERNS.items():
        match = re.search(pattern, text, re.MULTILINE)
        if match is None:
            continue
        values[f"{metric}_passed"] = int(match.group(1))
        values[f"{metric}_failed"] = int(match.group(2))
        try:
            values[f"{metric}_passed_pct"] = float(match.group(3).strip("% "))
        except (IndexError, ValueError):
            pass

    if "total_passed" not in values or "mapped_passed" not in values:
        raise ValueError(f"Could not parse total and mapped counts from {path}")

    values["flagstat_total"] = values["total_passed"] + values["total_failed"]
    sample = path.name[: -len(".flagstat")]
    return sample, values


def write_flagstat_table(path, sample, values):
    metrics = [
        item
        for item in TABLE_METRICS
        if item[0] not in {"secondary_passed", "supplementary_passed"}
        or values.get(item[0], 0) > 0
    ]
    table_id = "samtools_flagstat_color_table"
    with path.open("w", newline="") as handle:
        handle.write('# id: "samtools_flagstat_color_table"\n')
        handle.write('# section_name: "Samtools Flagstat (color-scaled)"\n')
        handle.write('# description: "Color-scaled read counts from samtools flagstat."\n')
        handle.write('# format: "tsv"\n')
        handle.write('# plot_type: "table"\n')
        handle.write(f'# pconfig:\n#   id: "{table_id}"\n')
        handle.write("# headers:\n")
        for _, title, scale in metrics:
            handle.write(f'#   "{title}":\n')
            handle.write(f'#     title: "{title}"\n')
            handle.write("#     min: 0\n")
            handle.write(f'#     scale: "{scale}"\n')
            handle.write('#     format: "{:,.2f}"\n')

        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["Sample"] + [title for _, title, _ in metrics])
        writer.writerow(
            [sample]
            + [
                values.get(key, 0) / READS_PER_MILLION
                for key, _, _ in metrics
            ]
        )


def main(input_dir):
    for path in sorted(input_dir.rglob("*.flagstat")):
        sample, values = parse_flagstat(path)
        general_stats = {
            "flagstat_total_overlay": values["flagstat_total"] / READS_PER_MILLION,
            "mapped_passed_overlay": values["mapped_passed"] / READS_PER_MILLION,
            "mapped_passed_pct_overlay": values["mapped_passed_pct"],
        }
        general_stats_path = path.with_name(
            f"{sample}_samtools_generalstats_mqc.json"
        )
        general_stats_path.write_text(
            json.dumps(
                {
                    "id": "samtools_flagstat_generalstats",
                    "plot_type": "generalstats",
                    "pconfig": HEADERS,
                    "data": {sample: general_stats},
                }
            )
        )
        table_path = path.with_name(f"{sample}_samtools_flagstat_mqc.tsv")
        write_flagstat_table(table_path, sample, values)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {Path(sys.argv[0]).name} MULTIQC_INPUT_DIR")
    main(Path(sys.argv[1]))
