# FA-NIVA: Fanconi Anemia Nanopore Analysis

A comprehensive Nextflow pipeline for analyzing long-read Nanopore sequencing data for Fanconi Anemia diagnosis. This pipeline automates basecalling, alignment, variant calling, and structural variant annotation.

---

## 📑 Table of Contents

| [Overview](#overview) | [Quick Start](#quick-start) | [Input](#input-data) | [Supported_Input](#supported-input-types) | [Configuration](#configuration) | [Output](#output-structure) | [Features](#pipeline-features) | [Examples](#execution-examples) | [Requirements](#system-requirements) | [Troubleshooting](#troubleshooting) | [Citation](#citation) |

---

## Overview

FA-NIVA processes Nanopore sequencing data to:
- Perform high-accuracy basecalling using Dorado with optional GPU acceleration
- Align reads to reference genome using Minimap2
- Call small variants (SNVs/indels) using DeepVariant with GPU support
- Annotate structural variants using AnnotSV
- Generate comprehensive quality control reports with MultiQC

---

## Quick Start

### Prerequisites

- **Nextflow** >= 22.10.1
- One of the following container engines:
  - Docker
  - Singularity
  - Conda/Mamba
  - Podman
  - Shifter
  - Charliecloud

### Basic Usage

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile docker \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir ./results
```

### Using GPU Acceleration (Recommended)

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile docker \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir ./results \
  --use_gpu true
```

### Cluster Execution (RIS/LSF)

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile ris \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir ./results
```

---

## Input Data

### Samplesheet Format

Create a CSV file (`samplesheet.csv`) with the following columns:

```csv
sample,fastq_pass
sample_001,/path/to/sample_001/fastq_pass/
sample_002,/path/to/sample_002/fastq_pass/
```

See [`assets/samplesheet.csv`](assets/samplesheet.csv) for a complete example.

---

## Supported Input Types

FA-NIVA supports three starting points:

| Input type | Starting step | Required files |
|------------|---------------|----------------|
| POD5 | Basecalling | *.pod5 files |
| FAST5 | Basecalling | *.fast5 files |
| FASTQ | Alignment | *.fastq.gz files |
| BAM | Variant calling | aligned BAM files + BAI index |

### Using POD5 files

samplesheet.csv

sample,pod5
Patient01,/data/pod5/Patient01/

Example command:

nextflow run UKWgenommedizin/FA-NIVA \
  -profile docker \
  --input samplesheet_pod5.csv \
  --genome GRCh38

The pipeline will:
1. Run Dorado basecalling
2. Align reads using Minimap2
3. Perform variant calling using DeepVariant
4. Generate QC reports

### Using FAST5 files

...

### Using BAM files

...


---

## Configuration

### Execution Profiles

| Profile | Use Case |
|---------|----------|
| **docker** | Run with Docker containers |
| **singularity** | Run with Singularity containers |
| **conda** | Use Conda environments |
| **mamba** | Use Mamba (faster Conda) |
| **podman** | Run with Podman |
| **shifter** | Run with Shifter container engine |
| **charliecloud** | Run with Charliecloud containers |
| **arm** | Run on ARM-based systems (e.g., Mac M1/M2) |
| **ris** | Execute on RIS cluster with LSF scheduler |
| **test** | Quick validation run with minimal data |
| **fa_niva** | Custom FA-NIVA configuration |
| **gitpod** | Cloud development environment |

### Key Parameters

#### Input/Output
- `--input` : Path to samplesheet CSV *(required)*
- `--outdir` : Output directory *(required)*
- `--genome` : Reference genome build (e.g., `GRCh38`, `GRCh37`)

#### Basecalling
- `--use_gpu` : Enable GPU acceleration for Dorado (default: `true`)
- `--nanopore_reads_type` : Dorado model type (default: `ont_r10_q20`)
  - Options: `ont_r9_4_1d`, `ont_r10_q20`, `ont_r10_q20_5mCG_5hmCG`

#### Structural Variants
- `--run_annotsv` : Enable AnnotSV for structural variant annotation (default: `false`)
- `--annotsvGenomeBuild` : Genome build for AnnotSV (default: `GRCh38`)
- `--annotsvMode` : AnnotSV mode - `full`, `split`, or `both` (default: `both`)

#### Resource Management
- `--max_cpus` : Maximum CPUs per task (default: `64`)
- `--max_memory` : Maximum memory per task (default: `256.GB`)
- `--max_time` : Maximum execution time per task (default: `256.h`)

#### Publishing
- `--publish_dir_mode` : How to publish results - `copy`, `link`, or `rellink` (default: `copy`)
- `--publish_sorted_bam` : Publish sorted BAM files (default: `false`)

#### MultiQC
- `--multiqc_config` : Custom MultiQC configuration file
- `--multiqc_title` : Title for MultiQC report
- `--multiqc_logo` : Path to logo for MultiQC report

For all available parameters, see [`nextflow_schema.json`](nextflow_schema.json).

---

## Output Structure

Results are organized in the specified `--outdir`:

```
results/
├── basecalling/           # Dorado basecalling results
│   ├── *.fastq.gz        # Basecalled reads
│   └── *.bam             # Alignment BAM files
├── alignment/             # Minimap2 aligned BAM files
│   ├── *.sorted.bam      # Sorted BAM files
│   └── *.sorted.bam.bai  # BAM index files
├── variants/              # DeepVariant VCF files
│   ├── *.vcf.gz          # Variant calls
│   └── *.vcf.gz.tbi      # VCF index files
├── annotation/            # AnnotSV structural variant annotations
│   ├── *.annotated.tsv   # Annotated SVs
│   └── *.unannotated.tsv # Unannotated SVs
├── multiqc/               # Quality control report
│   └── multiqc_report.html
└── pipeline_info/         # Execution metadata
    ├── execution_timeline_*.html
    ├── execution_report_*.html
    ├── execution_trace_*.txt
    └── pipeline_dag_*.html
```

---

## Pipeline Features

✅ **GPU Support**: Optional GPU acceleration for Dorado basecalling and DeepVariant variant calling  
✅ **Multi-Platform**: Support for Docker, Singularity, Conda, Podman, Shifter, and Charliecloud  
✅ **Cluster Integration**: LSF scheduler support for RIS clusters  
✅ **Quality Control**: Built-in MultiQC reporting  
✅ **Structural Variants**: Optional AnnotSV annotation for structural variants  
✅ **Comprehensive Logging**: Execution timeline, reports, DAG visualization, and trace files  
✅ **Resource Management**: Configurable resource limits per task  
✅ **Validation**: Built-in parameter schema validation  

---

## Execution Examples

### Local Docker Execution

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile docker \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir ./results \
  --use_gpu true
```

### Singularity on HPC

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile singularity \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir ./results
```

### With Structural Variant Annotation

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile docker \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir ./results \
  --run_annotsv true \
  --annotsvGenomeBuild GRCh38
```

### Conda Environment

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile conda \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir ./results
```

### Test Run

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile test,docker \
  --outdir ./test_results
```

### Mac M1/M2 (ARM)

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile arm,docker \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir ./results
```

### RIS Cluster with GPU

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile ris \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir ./results \
  --use_gpu true
```

---

## System Requirements

### Minimum
- 8 CPU cores
- 32 GB RAM
- 50 GB disk space per sample

### Recommended (with GPU)
- 16+ CPU cores
- 64 GB RAM
- NVIDIA GPU (RTX 3090 or better recommended)
- 500 GB+ disk space per sample

### Environment Variables

The pipeline sets the following environment variables to prevent package conflicts:

```bash
PYTHONNOUSERSITE=1          # Prevent system Python packages
R_PROFILE_USER=/.Rprofile   # R user profile
R_ENVIRON_USER=/.Renviron   # R environment variables
JULIA_DEPOT_PATH=/usr/local/share/julia  # Julia packages directory
```

---

## Troubleshooting

### Common Issues

**Docker socket permission denied**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
```

**GPU not recognized**
```bash
# Verify NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

**Out of memory errors**
```bash
# Increase available memory or adjust max_memory parameter
nextflow run ... --max_memory 128.GB
```

**Singularity container caching**
```bash
# Clear Singularity cache if experiencing issues
rm -rf $HOME/.singularity/cache
```

**Permission issues with output files**
```bash
# Adjust publish_dir_mode to avoid permission problems
nextflow run ... --publish_dir_mode symlink
```

---

## Pipeline Architecture

```
FA-NIVA/
├── bin/                    # Helper scripts (Python, Bash)
├── conf/                   # Configuration files
│   ├── base.config        # Base process configuration
│   ├── modules.config     # Process-specific modules
│   ├── test.config        # Test profile configuration
│   └── profile.config     # FA-NIVA specific settings
├── docker_files/          # Docker container definitions
├── lib/                   # Groovy utility libraries
├── modules/               # Nextflow DSL2 process modules
│   ├── nf-core/          # nf-core modules
│   └── local/            # Custom modules
├── subworkflows/          # Workflow subcomponents
│   ├── nf-core/          # nf-core subworkflows
│   └── local/            # Custom subworkflows
├── workflows/             # Main workflow definitions
├── assets/                # Templates and reference data
├── main.nf                # Pipeline entry point
├── nextflow.config        # Main configuration
└── nextflow_schema.json   # Parameter schema and validation
```

---

## Citation

If you use FA-NIVA in your research, please cite:

```bibtex
@software{fa_niva_2024,
  title={FA-NIVA: Nextflow pipeline for analysis of Nanopore sequencing for Fanconi diagnosis},
  author={Yu, Jiangyan},
  year={2024},
  url={https://github.com/UKWgenommedizin/FA-NIVA}
}
```

See [`CITATIONS.md`](CITATIONS.md) for citations of tools and methods used.

---

## Authors

- **Jiangyan Yu** - jiangyan.yu@ukw.de

## License

This project is licensed under the [MIT License](LICENSE).

## Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/UKWgenommedizin/FA-NIVA/issues)
- **Discussions**: [GitHub Discussions](https://github.com/UKWgenommedizin/FA-NIVA/discussions)
- **Contributing**: Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

## Additional Resources

- [Nextflow Documentation](https://www.nextflow.io/)
- [nf-core Community](https://nf-co.re/)
- [Dorado Basecaller](https://github.com/nanoporetech/dorado)
- [DeepVariant](https://github.com/google/deepvariant)
- [AnnotSV](https://lbgi.fr/AnnotSV/)
