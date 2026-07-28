# FA-NIVA: Flexible and  Automated – Nextflow-based Integrated Variant Analysis

A Nextflow framework for integrated variant analysis of Nanopore-based long-read sequencing data. This pipeline automates basecalling, alignment, variant calling, and structural variant annotation.

![Description](https://github.com/UKWgenommedizin/FA-NIVA/blob/main/docs/workflow_complete_graph.png)

FA-NIVA processes Nanopore sequencing data to:
- Perform high-accuracy basecalling using Dorado with GPU acceleration
- Align reads to reference genome using pbmm2
- Call small variants (SNVs/indels) using DeepVariant with GPU support
- Joint SNV-SV based phasing
- Annotate structural variants using AnnotSV
- Generate comprehensive quality control reports with MultiQC

---

## Pipeline Architecture

```
FA-NIVA/
├── bin/                   # Python scripts to check samplesheet and modify SNV genotype
├── conf/                  # Configuration files
│   ├── base.config        # CPU, memory, and execution time for each process
│   ├── modules.config     # Process output directories
│   └── profile.config     # Paths to samplesheet, reference genomes, and Dorado models
├── docker_files/          # Docker container definitions
├── lib/                   # Groovy utility libraries
├── modules/               # Nextflow DSL2 process modules
│   ├── nf-core/           # nf-core modules
│   └── local/             # Custom modules
├── subworkflows/          # Workflow subcomponents
│   ├── nf-core/           # nf-core subworkflows
│   └── local/             # Custom subworkflows
├── workflows/             # Main workflow (fa-niva.nf) definitions
├── assets/                # Example samplesheet and regions for SNV genotype modification
├── main.nf                # Pipeline entry point
├── nextflow.config        # Main configuration
└── nextflow_schema.json   # Parameter schema and validation
```

## Files Users Should Update

Before running the pipeline, users should review and modify the following files to match their local environment:

| File | Purpose | What to update |
|------|---------|----------------|
| `conf/profile.config` | Environment-specific paths | Update the paths to the samplesheet, reference genomes, Dorado models, and any other local resources. |
| `conf/base.config` *(optional)* | Resource allocation | Adjust CPU, memory, and execution time for processes according to your computing environment. |
| `assets/samplesheet.csv` | Input samples | Replace the example samplesheet with your own sample information. |
| `assets/SNV_modify_regions.csv` *(if applicable)* | Target regions | Update the BED file if using custom genomic regions for SNV genotype modification. |

> **Note:** The pipeline source code (`modules/`, `subworkflows/`, and `workflows/`) typically does not require modification for routine analyses. Most users only need to update the configuration files and input files listed above.

---

## 📑 Table of Contents

- [1. Quick Start](#1-quick-start-using-example-files)

- [2. Input](#2-input-data)
  - [2.1 Samplesheet Format](#21-samplesheet-format)
  - [2.2 Supported Input Types](#22-supported-input-types)

- [3. Configuration](#3-configuration)
  - [3.1 Key Parameters](#31-key-parameters)
  - [3.2 Configuration Files](#32-configuration-files)
  - [3.3 Computational Resources](#33-computational-resources)

- [4. Output](#4-output-structure)

- [Citation/Authors/License](#citation)
- [Notes and Implementation Details](#notes-and-implementation-details)

---

## 1. Quick Start Using Example Files

### 1.1 Prerequisites

Before running FA-NIVA, ensure that the following software and resources are available:

- **Nextflow** ≥ 22.10.1  
  Install Nextflow according to the official documentation:  
  https://www.nextflow.io/docs/latest/install.html

- **Container engine** (one of the following):
  - Docker — recommended and fully tested
  - Singularity/Apptainer — supported
  - Conda/Mamba — supported
  - Podman — supported
  - Shifter — supported
  - Charliecloud — supported

- **Test input data (BAM format)**  
  Example BAM files for testing the pipeline are available on Zenodo:  
  https://zenodo.org/records/17284961  
  For test purpose, only input_path column in samplesheet.csv shall be adjusted to your local path to the downloaded folder.

- **Reference genome files**  
  FA-NIVA requires a reference genome compatible with the selected build (e.g., GRCh38).

The pipeline supports two deployment modes:

### 1.2 Basic Usage

FA-NIVA can be executed in two modes depending on compute environment connectivity.

---

#### Option A: HPC environment with internet access

If internet access is available, all required reference files (e.g., genome FASTA, indices) will be automatically downloaded during execution.

```bash
nextflow run UKWgenommedizin/FA-NIVA \
  -profile fa_niva,docker \
  --input samplesheet.csv \
  --genome GRCh38 \
  --outdir results \
  --reads_format bam \
  --use_gpu true
```

> **Note:** For test runs using BAM files, the `input_path` in the sample sheet should point to the directory containing the downloaded Zenodo BAM test dataset.

---

#### Option B: HPC environment without internet access

If external downloads are restricted, all reference genome files must be provided manually.

Reference genomes can be obtained from:  
https://github.com/PacificBiosciences/reference_genomes

For the GRCh38, one can download bundle for human_GRCh38_no_alt_analysis_set

Required files:

```text
GRCh38_reference/
├── human_GRCh38_no_alt_analysis_set.fasta
├── human_GRCh38_no_alt_analysis_set.fasta.fai
```

These files must be passed via command-line parameters:

```bash
git clone -b main https://github.com/UKWgenommedizin/FA-NIVA
nextflow run ./FA-NIVA \ # local path to the downloaded folder from git repo
  -profile fa_niva,docker \
  --input samplesheet.csv \
  --genome GRCh38 \
  --fasta /path/to/GRCh38_reference/human_GRCh38_no_alt_analysis_set.fasta \
  --fasta_index /path/to/GRCh38_reference/human_GRCh38_no_alt_analysis_set.fasta.fai \
  --outdir results \
  --reads_format bam \
  --use_gpu true
```

For cluster-specific settings, resource allocation, and custom configurations, see the [Configuration](#3-configuration) section below.

---

## 2 Input Data

### 2.1 Samplesheet Format

Create a CSV file (`samplesheet.csv`) with the following columns. The input_path column should contain the path to the directory holding the input data files (e.g., POD5, FAST5, FASTQ, or BAM files) for each sample.

To ensure compatibility across operating systems, we recommend copying and modifying the template file located at [`assets/samplesheet.csv`](assets/samplesheet.csv). When preparing the sample sheet on Linux-based HPC systems, editing the file with vim or another Unix-compatible text editor can help avoid issues related to Windows line endings and file formatting.

```csv
id,sample,flowcell,input_path,batch,kit
test,chr21,flowcell1,/home/yu_j/smbshare/test_faniva/chr21,20251127,LSK114
test,chr22,flowcell1,/home/yu_j/smbshare/test_faniva/chr22,20251127,LSK114
```
---

### 2.2 Supported Input Types

FA-NIVA supports three starting points:

| Input Type | Pipeline Entry Point | Required Files                                                         | Validation Status |
| ---------- | -------------------- | ---------------------------------------------------------------------- | ----------------- |
| POD5       | Basecalling          | Nanopore POD5 files (`*.pod5`)                                         | Fully tested      |
| FAST5      | Basecalling          | Nanopore FAST5 files (`*.fast5`)                                       | Fully tested      |
| FASTQ      | Alignment            | Basecalled FASTQ files (`*.fastq.gz`)                                  | Fully tested      |
| BAM*       | Variant Calling      | Coordinate-sorted BAM file (`*.bam`) and corresponding index (`*.bai`) | Fully tested      |

*When input is bam file, dorado basecalling step will be skipped.

#### 2.2.1 Using POD5 files

prepare samplesheet_pod5.csv

```csv
id,sample,flowcell,input_path,batch,kit
sample1_pod5,sample1,flowcell1,/home/yu_j/smbshare/sample1,20251127,LSK114
```

Example command:

```bash
nextflow run ./FA-NIVA \
  -profile FA_NIVA,docker \
  --input samplesheet_pod5.csv \
  --fasta ./ref/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta \
  --fasta_index ./ref/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta.fai \
  --outdir results \
  --dorado_model dna_r10.4.1_e8.2_400bps_fast@v5.0.0 \ # important to use the corresponding dorado_model for basecalling
  --reads_format pod5 \
  --use_gpu true
```


#### 2.2.2 Using FAST5 files

prepare samplesheet_fast5.csv

```csv
id,sample,flowcell,input_path,batch,kit
sample1_fast,sample1,flowcell1,/home/yu_j/smbshare/sample1,20251127,LSK114
```

Example command:

```bash
nextflow run ./FA-NIVA \
  -profile FA_NIVA,docker \
  --input samplesheet_fast5.csv \
  --fasta ./ref/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta \
  --fasta_index ./ref/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta.fai \
  --outdir results \
  --dorado_model dna_r10.4.1_e8.2_400bps_fast@v5.0.0 \ # important to use the corresponding dorado_model for basecalling
  --reads_format fast5 \
  --use_gpu true
```

#### 2.2.3 Using BAM files

prepare samplesheet_bam.csv

```csv
id,sample,flowcell,input_path,batch,kit
sample1_bam,sample1,flowcell1,/home/yu_j/smbshare/sample1,20251127,LSK114
```

Example command:

```bash
nextflow run ./FA-NIVA \
  -profile FA_NIVA,docker \
  --input samplesheet_bam.csv \
  --fasta ./ref/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta \
  --fasta_index ./ref/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta.fai \
  --outdir results \
  --reads_format bam \ # dorado basecalling step will be skipped
  --use_gpu true
```

#### Barcoded Datasets 
The default FA-NIVA workflow is configured for single-sample analysis and does not perform barcode demultiplexing. For datasets containing multiple barcoded samples, users should perform barcode demultiplexing during the basecalling step using Dorado's native barcode support. Barcode demultiplexing can be enabled by modifying the Dorado command in: `modules/local/DORADO_BASECALLER.nf` and adding the appropriate Dorado barcode-related parameters (e.g., barcode kit specification and demultiplexing options) according to the Dorado documentation. 

FA-NIVA does not automatically detect or process multiplexed datasets. If barcode demultiplexing is required, users must customize the Dorado basecalling module before running the workflow. Because Dorado provides built-in support for barcode demultiplexing, users can adapt the workflow to their experimental design by editing the basecalling command and supplying the barcode configuration appropriate for their sequencing run.

---

## 3 Configuration

FA-NIVA can be configured through a combination of command-line parameters and configuration files. Most users only need to adjust the input sample sheet, reference genome settings, and computational resources before running the pipeline.

### 3.1 Key Parameters

| Parameter | Description |
|-----------|-------------|
| `--input` | Path to the sample sheet describing the input samples. See [Samplesheet Format](#21-samplesheet-format). Optional if configured in `conf/profile.config`. |
| `--outdir` | Output directory where pipeline results will be written. |
| `--genome` | Reference genome build (`GRCh38` or `GRCh37`). |
| `--fasta` | Path to the reference genome FASTA file. Optional if configured in `conf/profile.config`. |
| `--fasta_index` | Path to the corresponding FASTA index (`.fai`) file. Optional if configured in `conf/profile.config`. |
| `--use_gpu` | Enable GPU acceleration for Dorado basecalling and DeepVariant variant calling. Optional if configured in `conf/profile.config`. |
| `--dorado_model` | Important to use the corresponding dorado_model for basecalling. Will be skipped if input is bam. Optional if configured in `conf/profile.config`. |
| `--reads_format` | Optional if configured in `conf/profile.config`.  |

### 3.2 Configuration Files

The following files may require modification depending on the computing environment and analysis requirements.

| File | Description |
|------|-------------|
| `assets/samplesheet.csv` | Defines the input samples. The `input_path` field should contain the absolute path to the directory containing the input sequencing files (`*.pod5`, `*.fast5`, `*.fastq.gz`, or `*.bam`). |
| `conf/profile.config` | Defines reference genome resources, Dorado model settings, and AnnotSV database locations. Reference paths can also be supplied using `--fasta` and `--fasta_index`. |
| `conf/base.config` | Specifies computational resources such as CPU, memory, and GPU allocation. |
| `nextflow.config` | Controls workflow components and software modules. Structural variant annotation is disabled by default and must be enabled if AnnotSV analysis is required. |
| `assets/SNV_modify_regions.csv` | Defines genomic regions used for SNV–SV joint phasing analysis. Modify this file to analyze additional genomic regions. |

### 3.3 Computational Resources

Resource limits can be adjusted in `conf/base.config`.

| Setting | Default | Description |
|----------|---------|-------------|
| `max_cpus` | `64` | Maximum number of CPUs allocated to a process. |
| `max_memory` | `256.GB` | Maximum memory allocated to a process. |
| `max_time` | `256.h` | Maximum execution time allocated to a process. |

> **Note**
>
> GPU resources are required for Dorado basecalling and recommended for DeepVariant variant calling.
>
> To maximize stability on shared HPC systems, we recommend processing one sample at a time and allocating a single GPU per analysis:
>
> ```bash
> --use_gpu 1
> ```
>
> Using a dedicated GPU minimizes resource contention and can improve overall workflow performance and scheduling efficiency.

For a complete list of available parameters and advanced options, see [`nextflow_schema.json`](nextflow_schema.json).


---

## 4 Output Structure

Results are organized in the specified `--outdir`:


```text
<sample_id>/
├── multiqc/                          # MultiQC quality-control reports
│   ├── multiqc_data/                 # Raw data used by MultiQC
│   ├── multiqc_plots/                # Figures generated by MultiQC
│   ├── multiqc_report.html           # Interactive MultiQC report
│   └── versions.yml                  # Software versions collected by MultiQC
│
├── pipeline_info/                    # Workflow execution metadata
│   ├── execution_report_<time>.html  # Execution summary and resource usage
│   ├── execution_timeline_<time>.html# Workflow timeline
│   ├── execution_trace_<time>.txt    # Process-level execution details
│   ├── execution_dag_<time>.html     # Workflow DAG visualization
│   ├── samplesheet.valid.csv         # Validated sample sheet
│   └── software_versions.yml         # Software versions used in the analysis
│
├── <sample_id>/                      # Sample-specific analysis results
│   ├── basecaller/                   # Dorado basecalling outputs
│   ├── deepvariant/                  # Small-variant calling results
│   ├── pbmm2/                        # Read alignment files (BAM/CRAM)
│   ├── sawfish/                      # Structural-variant calling results
│   └── whatshap/                     # Phasing analysis results
│
├── <sample_id>.html                  # PycoQC sequencing quality report
└── <sample_id>.json                  # Machine-readable QC and run statistics
```

---

## Citation

If you use FA-NIVA in your research, please cite:

```bibtex
@article{neurgaonkar2026faniva, 
  title = {FA-NIVA: A Nextflow framework for automated analysis of Nanopore-based long-read sequencing data for genetic analysis in Fanconi anemia}, 
  author = {Neurgaonkar, Priya Satish and Dierolf, Michelle and O'Gorman, Luke and Remmele, Christian and Schäffer, Judith and Popp, Isabell and Borst, Angela and Rost, Simone and Ankenbrand, Markus J. and Kratz, Christian P. and Bergmann, Anke K. and Kalb, Reinhard and Yu, Jiangyan}, 
  journal = {medRxiv}, 
  year = {2026}, 
  doi = {10.64898/2026.02.27.26346867} }
```

See [`CITATIONS.md`](CITATIONS.md) for citations of tools and methods used.

---

## Authors

- **Priya Satish Neurgaonkar** 
- **Markus J. Ankenbrand** - markus.ankenbrand@uni-wuerzburg.de
- **Christian Remmele** - remmele_c@ukw.de
- **Jiangyan Yu** - jiangyan.yu@ukw.de

## License

This project is licensed under the [MIT License](LICENSE).


## Notes and Implementation Details

### AnnotSV Installation

The current AnnotSV container image does not include the annotation database (`annotationsDir`). Therefore, the annotation database must be installed separately before running structural variant annotation.

Install the AnnotSV annotation resources according to the official instructions:

https://github.com/lgmgeo/AnnotSV/blob/master/bin/INSTALL_annotations.sh

After installation, update the corresponding annotation database path in:

```text
conf/profile.config
```

and enable AnnotSV annotation as described in the Configuration section.

### DeepVariant Configuration

FA-NIVA uses the **ONT_R104** model for small-variant calling:

```text
model_type = ONT_R104
```

## Additional Resources

- [Nextflow Documentation](https://www.nextflow.io/)
- [nf-core Community](https://nf-co.re/)
- [Dorado Basecaller](https://github.com/nanoporetech/dorado)
- [DeepVariant](https://github.com/google/deepvariant)
- [AnnotSV](https://lbgi.fr/AnnotSV/)

### Workflow Origins and Adaptations

The FA-NIVA workflow was initially developed using components and workflow structures from the following projects (accessed 2024-12-10):

1. https://github.com/nf-core/nanoseq
2. https://github.com/dhslab/nf-core-wgsnano

#### Container Adaptations

Due to institutional firewall restrictions that limited access to specific container registries, selected container images were mirrored to Docker Hub for use within FA-NIVA.

| Software | Original Source | Version Used |
|-----------|----------------|--------------|
| Dorado | https://github.com/dhslab/dhslab-docker-images/pkgs/container/docker-dorado | 241016 |
| WhatsHap | https://github.com/dhslab/dhslab-docker-images/pkgs/container/docker-whatshap | 240302 |

These mirrored images are functionally equivalent to the corresponding images provided by the DHSLab container repository and were used to ensure reproducible execution within the local computing environment.

### Reproducibility

Software versions used during each pipeline execution are recorded in:

```text
pipeline_info/software_versions.yml
multiqc/versions.yml
```

These files should be retained together with the analysis results to ensure full reproducibility.
