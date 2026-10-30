#!/usr/bin/env python3
"""Create color-scaled MultiQC General Statistics from staged flagstat files."""

import json
import re
import sys
from pathlib import Path


TOTAL_PATTERN = re.compile(
    r"^(\d+) \+ (\d+) in total \(QC-passed reads \+ QC-failed reads\)$",
    re.MULTILINE,
)
MAPPED_PATTERN = re.compile(r"^(\d+) \+ (\d+) mapped \((.+):(.+)\)$", re.MULTILINE)
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


def parse_flagstat(path):
    text = path.read_text()
    total = TOTAL_PATTERN.search(text)
    mapped = MAPPED_PATTERN.search(text)
    if total is None or mapped is None:
        raise ValueError(f"Could not parse total and mapped counts from {path}")

    sample = path.name[: -len(".flagstat")]
    return sample, {
        "flagstat_total_overlay": (
            int(total.group(1)) + int(total.group(2))
        )
        / READS_PER_MILLION,
        "mapped_passed_overlay": int(mapped.group(1)) / READS_PER_MILLION,
        "mapped_passed_pct_overlay": float(mapped.group(3).strip("% ")),
    }


def main(input_dir):
    for path in sorted(input_dir.rglob("*.flagstat")):
        sample, values = parse_flagstat(path)
        output_path = path.with_name(f"{sample}_samtools_generalstats_mqc.json")
        payload = {
            "id": "samtools_flagstat_generalstats",
            "plot_type": "generalstats",
            "headers": HEADERS,
            "data": {sample: values},
        }
        output_path.write_text(json.dumps(payload))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {Path(sys.argv[0]).name} MULTIQC_INPUT_DIR")
    main(Path(sys.argv[1]))
