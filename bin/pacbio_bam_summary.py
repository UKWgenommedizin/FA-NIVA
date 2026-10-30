#!/usr/bin/env python3
"""Summarize PacBio HiFi metrics that can be recovered from a BAM file."""

import math
import csv
import json
import statistics
import sys


def median(values):
    return statistics.median(values) if values else "NA"


def mean(values):
    return statistics.mean(values) if values else "NA"


def fmt(value):
    return f"{value:.2f}" if isinstance(value, (int, float)) else value


def read_tags(fields):
    tags = {}
    for field in fields[11:]:
        parts = field.split(":", 2)
        if len(parts) == 3:
            tags[parts[0]] = parts[2]
    return tags


def read_qv(tags, qualities):
    # PacBio's rq tag is the predicted read accuracy. Convert it to Phred QV.
    try:
        accuracy = float(tags["rq"])
        if 0 < accuracy < 1:
            return -10 * math.log10(1 - accuracy)
        if accuracy >= 1:
            return 60.0
    except (KeyError, ValueError):
        pass
    return statistics.mean(qualities) if qualities else None


rows = []
for line in sys.stdin:
    fields = line.rstrip("\n").split("\t")
    if len(fields) < 11:
        continue
    try:
        flag = int(fields[1])
    except ValueError:
        continue
    if flag & (0x100 | 0x800):  # Exclude secondary and supplementary records.
        continue
    seq = fields[9]
    if seq == "*":
        continue
    qualities = [ord(char) - 33 for char in fields[10]] if fields[10] != "*" else []
    tags = read_tags(fields)
    qv = read_qv(tags, qualities)
    try:
        passes = float(tags["np"])
    except (KeyError, ValueError):
        passes = None
    # PacBio QNAMEs have movie/zmw/start_end form. Count each represented ZMW once.
    name_parts = fields[0].split("/")
    zmw = "/".join(name_parts[:2]) if len(name_parts) >= 3 else fields[0]
    rows.append((len(seq), qv, passes, zmw, qualities))


def metrics(selected):
    lengths = [row[0] for row in selected]
    qvs = [row[1] for row in selected if row[1] is not None]
    bases = sum(lengths)
    sorted_lengths = sorted(lengths, reverse=True)
    n50 = "NA"
    cumulative = 0
    for length in sorted_lengths:
        cumulative += length
        if cumulative >= bases / 2:
            n50 = length
            break
    return {
        "reads": len(selected),
        "yield": bases,
        "mean_length": fmt(mean(lengths)),
        "median_length": fmt(median(lengths)),
        "n50": n50,
        "median_qv": fmt(median(qvs)),
        "mean_qv": fmt(mean(qvs)),
    }


all_metrics = metrics(rows)
lt_q20 = [row for row in rows if row[1] is not None and row[1] < 20]
ge_q30 = [row for row in rows if row[1] is not None and row[1] >= 30]
passes = [row[2] for row in rows if row[2] is not None]
q30_bases = sum(sum(1 for q in row[4] if q >= 30) for row in rows)

passing_zmws = len(set(row[3] for row in rows))
report_rows = [
    ("HiFi Reads", all_metrics["reads"], "Primary BAM records"),
    ("HiFi Yield (bp)", all_metrics["yield"], ""),
    ("HiFi Read Length (mean, bp)", all_metrics["mean_length"], ""),
    ("HiFi Read Length (median, bp)", all_metrics["median_length"], ""),
    ("HiFi Read Length N50 (bp)", all_metrics["n50"], ""),
    ("HiFi Read Quality (median)", all_metrics["median_qv"], "Derived from rq tag; base-quality mean used when rq is absent"),
    ("HiFi Read Quality (mean)", all_metrics["mean_qv"], "Derived from rq tag; base-quality mean used when rq is absent"),
    ("HiFi Number of Passes (mean)", fmt(mean(passes)), "From np tag; NA if absent"),
    ("ZMWs pass filters", passing_zmws, "Unique ZMWs represented in the HiFi BAM"),
]
for title, subset in (("<Q20", lt_q20), (">=Q30", ge_q30)):
    data = metrics(subset)
    report_rows.extend([
        (f"{title} Reads", data["reads"], "Based on per-read rq-derived QV"),
        (f"{title} Yield (bp)", data["yield"], ""),
        (f"{title} Read Length (mean, bp)", data["mean_length"], ""),
        (f"{title} Read Length (median, bp)", data["median_length"], ""),
        (f"{title} Read Quality (median)", data["median_qv"], ""),
        (f"{title} Read Quality (mean)", data["mean_qv"], ""),
    ])
report_rows.extend([
    ("Base quality >=Q30 (bp)", q30_bases, "Counted from BAM QUAL values"),
    ("ZMWs represented in BAM", passing_zmws, "Passing/read records only; not total input ZMWs"),
    ("CCS filtering and failure counts", "NA", "Require CCS run report or original subreads"),
    ("ZMWs missing adapters", "NA", "Not reliably recoverable from a HiFi BAM"),
])

writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
writer.writerow(("Metric", "Value", "Notes"))
writer.writerows(report_rows)

# MultiQC's custom-content parser accepts a self-describing TSV table. Files
# sharing the section id are combined into one table, one row per sample.
mqc_path, sample = sys.argv[1:3]
with open(mqc_path, "w", newline="") as handle:
    handle.write('# id: "pacbio_bam_summary"\n')
    handle.write('# section_name: "PacBio BAM summary"\n')
    handle.write('# description: "Metrics calculated from PacBio HiFi BAM records. ZMW failure categories require the CCS report or original subreads."\n')
    handle.write('# format: "tsv"\n')
    handle.write('# plot_type: "table"\n')
    handle.write('# pconfig:\n#   id: "pacbio_bam_summary_table"\n')
    table_writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    table_writer.writerow(["Sample"] + [name for name, _, _ in report_rows])
    table_writer.writerow([sample] + [value for _, value, _ in report_rows])

# Add the main numeric PacBio QC metrics to MultiQC's General Statistics table,
# where MultiQC renders the values with color-scaled bars.
def number_or_none(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


general_stats = {
    "pacbio_hifi_reads": all_metrics["reads"],
    "pacbio_hifi_yield_bp": all_metrics["yield"],
    "pacbio_hifi_mean_length_bp": number_or_none(all_metrics["mean_length"]),
    "pacbio_hifi_median_length_bp": number_or_none(all_metrics["median_length"]),
    "pacbio_hifi_n50_bp": number_or_none(all_metrics["n50"]),
    "pacbio_hifi_median_qv": number_or_none(all_metrics["median_qv"]),
    "pacbio_hifi_mean_qv": number_or_none(all_metrics["mean_qv"]),
    "pacbio_hifi_mean_passes": number_or_none(fmt(mean(passes))),
    "pacbio_zmws_pass": passing_zmws,
    "pacbio_lt_q20_reads": len(lt_q20),
    "pacbio_gte_q30_reads": len(ge_q30),
    "pacbio_gte_q30_bases_bp": q30_bases,
}

general_stats_headers = []
for key, title, description, scale, maximum in [
    ("pacbio_hifi_reads", "PacBio HiFi reads", "Number of HiFi BAM records", "YlGn", None),
    ("pacbio_hifi_yield_bp", "PacBio HiFi yield", "HiFi yield in bases", "YlGn", None),
    ("pacbio_hifi_mean_length_bp", "PacBio mean read length", "Mean HiFi read length (bp)", "YlGn", None),
    ("pacbio_hifi_median_length_bp", "PacBio median read length", "Median HiFi read length (bp)", "YlGn", None),
    ("pacbio_hifi_n50_bp", "PacBio read N50", "HiFi read N50 (bp)", "YlGn", None),
    ("pacbio_hifi_median_qv", "PacBio median read QV", "Median read quality value", "YlGn", 60),
    ("pacbio_hifi_mean_qv", "PacBio mean read QV", "Mean read quality value", "YlGn", 60),
    ("pacbio_hifi_mean_passes", "PacBio mean passes", "Mean number of passes from the np tag", "YlGn", None),
    ("pacbio_zmws_pass", "PacBio passing ZMWs", "Unique ZMWs represented in the HiFi BAM", "YlGn", None),
    ("pacbio_lt_q20_reads", "PacBio reads <Q20", "HiFi records with read QV below 20", "RdYlGn_r", None),
    ("pacbio_gte_q30_reads", "PacBio reads ≥Q30", "HiFi records with read QV at least 30", "YlGn", None),
    ("pacbio_gte_q30_bases_bp", "PacBio bases ≥Q30", "Bases with base quality at least Q30", "YlGn", None),
]:
    config = {"title": title, "description": description, "min": 0, "scale": scale}
    if maximum is not None:
        config["max"] = maximum
    general_stats_headers.append({key: config})

general_stats_path = mqc_path.replace("_mqc.tsv", "_generalstats_mqc.json")
with open(general_stats_path, "w") as handle:
    json.dump(
        {
            "id": "pacbio_bam_generalstats",
            "plot_type": "generalstats",
            "headers": general_stats_headers,
            "data": {sample: general_stats},
        },
        handle,
    )
