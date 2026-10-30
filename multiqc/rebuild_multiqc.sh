#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${MULTIQC_CONFIG:-${SCRIPT_DIR}/rebuild_config.yml}"
OUTPUT_DIR="${MULTIQC_OUTPUT_DIR:-${SCRIPT_DIR}/adjusted}"
MULTIQC_IMAGE="${MULTIQC_IMAGE:-quay.io/biocontainers/multiqc:1.13--pyhdfd78af_0}"

usage() {
    cat <<'USAGE'
Rebuild a MultiQC report using the editable rebuild_config.yml.

Usage:
  rebuild_multiqc.sh [MULTIQC_INPUT_DIR] [OUTPUT_DIR]

Pass the Nextflow MultiQC process work directory as MULTIQC_INPUT_DIR. It is
the directory containing numbered staging folders such as 1/, 2/, and 3/.
Alternatively, set MULTIQC_INPUT_DIR in the environment. If omitted, the
script tries the copied task folder beside itself, then the source path in
multiqc_data/multiqc_sources.txt.

Example on the server:
  ./rebuild_multiqc.sh /path/to/work/ab/cdef0123456789 /path/to/results/multiqc-adjusted

Settings can be changed in rebuild_config.yml or by setting MULTIQC_CONFIG.
The script copies recognized staged QC inputs with symlinks resolved before
running MultiQC, so container runtimes can read the files.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

if [[ "$#" -gt 2 ]]; then
    usage >&2
    exit 2
fi

INPUT_DIR="${1:-${MULTIQC_INPUT_DIR:-}}"
if [[ -z "$INPUT_DIR" ]]; then
    # Prefer the copied Nextflow task folder located beside this script.
    for candidate in "$SCRIPT_DIR"/*; do
        if [[ -d "$candidate" && -f "$candidate/.command.sh" && -d "$candidate/multiqc_data" ]]; then
            INPUT_DIR="$candidate"
            break
        fi
    done
fi

if [[ -z "$INPUT_DIR" ]]; then
    SOURCES_FILE="${SCRIPT_DIR}/multiqc_data/multiqc_sources.txt"
    if [[ -f "$SOURCES_FILE" ]]; then
        SOURCE_PATH="$(awk -F '\t' 'NR > 1 && $4 ~ /^\// { print $4; exit }' "$SOURCES_FILE")"
        if [[ -n "$SOURCE_PATH" ]]; then
            SOURCE_PARENT="$(dirname -- "$SOURCE_PATH")"
            if [[ "$(basename -- "$SOURCE_PARENT")" =~ ^[0-9]+$ ]]; then
                # Nextflow stages MultiQC inputs in numbered subdirectories via stageAs '?/*'.
                INPUT_DIR="$(dirname -- "$SOURCE_PARENT")"
            else
                INPUT_DIR="$SOURCE_PARENT"
            fi
        fi
    fi
fi

if [[ -z "$INPUT_DIR" || ! -d "$INPUT_DIR" ]]; then
    echo "ERROR: Provide the original MultiQC input directory. The copied report folder does not contain the source logs." >&2
    usage >&2
    exit 2
fi

INPUT_DIR="$(cd -- "$INPUT_DIR" && pwd)"
BROKEN_RAW_LINK="$(find "$INPUT_DIR" -type l \
    \( -name '*_mqc.tsv' -o -name '*_mqc.json' -o -name '*.flagstat' -o \
       -name '*.stats' -o -name '*.global.dist.txt' -o -name '*.summary.txt' -o \
       -name '*.region.dist.txt' -o -name '*.json' \) \
    ! -exec test -e {} \; -print -quit)"
if [[ -n "$BROKEN_RAW_LINK" ]]; then
    echo "ERROR: Staged QC input is a broken symlink: $BROKEN_RAW_LINK" >&2
    echo "Copy the task folder with symlink targets dereferenced, or run this script where the original Nextflow work files are available." >&2
    exit 2
fi

RAW_INPUT_FILE="$(find -L "$INPUT_DIR" -mindepth 2 -maxdepth 2 -type f \
    \( -name '*_mqc.tsv' -o -name '*_mqc.json' -o -name '*.flagstat' -o \
       -name '*.stats' -o -name '*.global.dist.txt' -o -name '*.summary.txt' -o \
       -name '*.region.dist.txt' -o \( -name '*.json' ! -name 'multiqc_data.json' \) \) \
    -print -quit)"
if [[ -z "$RAW_INPUT_FILE" ]]; then
    echo "ERROR: No raw workflow QC files found in: $INPUT_DIR" >&2
    if [[ -f "$INPUT_DIR/multiqc_data.json" || -f "$INPUT_DIR/multiqc_data/multiqc_data.json" ]]; then
        echo "This folder contains MultiQC's parsed exports (for example multiqc_samtools_flagstat.txt and multiqc_pacbio_bam_summary_table.txt), not the original files MultiQC reads." >&2
        echo "Use the task folder's staged inputs (for example hifi_test.flagstat in a numbered subfolder) with their symlink targets available." >&2
    else
        echo "Use the original MultiQC task input directory, not a generated MultiQC report folder." >&2
    fi
    exit 2
fi

if [[ -n "${2:-}" ]]; then
    OUTPUT_DIR="$2"
fi
mkdir -p -- "$OUTPUT_DIR"
OUTPUT_DIR="$(cd -- "$OUTPUT_DIR" && pwd)"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERROR: MultiQC config not found: $CONFIG_FILE" >&2
    exit 2
fi
CONFIG_FILE="$(cd -- "$(dirname -- "$CONFIG_FILE")" && pwd)/$(basename -- "$CONFIG_FILE")"

# Copy staged inputs while resolving Nextflow symlinks. Containers only mount
# the task directory, so the original symlink targets may otherwise be hidden.
STAGED_INPUT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/faniva-multiqc-input.XXXXXX")"
trap 'rm -rf "$STAGED_INPUT_DIR"' EXIT
while IFS= read -r -d '' source_file; do
    relative_path="${source_file#"${INPUT_DIR}/"}"
    destination_dir="${STAGED_INPUT_DIR}/$(dirname -- "$relative_path")"
    mkdir -p -- "$destination_dir"
    cp -L "$source_file" "${STAGED_INPUT_DIR}/${relative_path}"
done < <(find -L "$INPUT_DIR" -mindepth 2 -maxdepth 2 -type f \
    \( -name '*_mqc.tsv' -o -name '*_mqc.json' -o -name '*.flagstat' -o \
       -name '*.stats' -o -name '*.global.dist.txt' -o -name '*.summary.txt' -o \
       -name '*.region.dist.txt' -o \( -name '*.json' ! -name 'multiqc_data.json' \) \) \
    -print0)

if [[ -z "$(find "$STAGED_INPUT_DIR" -type f -print -quit)" ]]; then
    echo "ERROR: No readable QC inputs could be staged from: $INPUT_DIR" >&2
    exit 2
fi

if command -v multiqc >/dev/null 2>&1; then
    echo "Using local $(multiqc --version 2>&1 | tail -n 1)"
    multiqc \
        --force \
        --config "$CONFIG_FILE" \
        --outdir "$OUTPUT_DIR" \
        --filename multiqc_report.html \
        "$STAGED_INPUT_DIR"
elif command -v apptainer >/dev/null 2>&1; then
    echo "Using Apptainer image $MULTIQC_IMAGE"
    apptainer exec \
        --bind "$STAGED_INPUT_DIR:/input:ro" \
        --bind "$OUTPUT_DIR:/output" \
        --bind "$CONFIG_FILE:/rebuild_config.yml:ro" \
        "docker://${MULTIQC_IMAGE}" \
        multiqc \
        --force \
        --config /rebuild_config.yml \
        --outdir /output \
        --filename multiqc_report.html \
        /input
elif command -v singularity >/dev/null 2>&1; then
    echo "Using Singularity image $MULTIQC_IMAGE"
    singularity exec \
        --bind "$STAGED_INPUT_DIR:/input:ro" \
        --bind "$OUTPUT_DIR:/output" \
        --bind "$CONFIG_FILE:/rebuild_config.yml:ro" \
        "docker://${MULTIQC_IMAGE}" \
        multiqc \
        --force \
        --config /rebuild_config.yml \
        --outdir /output \
        --filename multiqc_report.html \
        /input
elif command -v docker >/dev/null 2>&1; then
    echo "Using container $MULTIQC_IMAGE"
    docker run --rm \
        --entrypoint multiqc \
        --volume "$STAGED_INPUT_DIR:/input:ro" \
        --volume "$OUTPUT_DIR:/output" \
        --volume "$CONFIG_FILE:/rebuild_config.yml:ro" \
        "$MULTIQC_IMAGE" \
        --force \
        --config /rebuild_config.yml \
        --outdir /output \
        --filename multiqc_report.html \
        /input
else
    echo "ERROR: Install MultiQC or Docker to rebuild the report." >&2
    exit 127
fi

echo "Report written to: ${OUTPUT_DIR}/multiqc_report.html"
