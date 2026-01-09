FA-NIVA is an nf-core based workflow to analyze nanopore long-read sequencing data for fanconi genetic analysis.
![Description](https://github.com/UKWgenommedizin/FA-NIVA/blob/main/docs/workflow_complete_graph.png)
**Basic steps to use the workflow**:
1. Install nextflow according to its manual (https://www.nextflow.io/docs/latest/install.html)
2. Download and unzip (or git clone) FA-NIVA package from github (https://github.com/UKWgenommedizin/FA-NIVA)
```
git clone -b main https://github.com/UKWgenommedizin/FA-NIVA
```
3. Download the test bam files from zenodo: https://zenodo.org/records/17284961. 
   The reference human genome can be also downloaded from here: https://github.com/PacificBiosciences/reference_genomes?tab=readme-ov-file

4. Adjusting file path accordingly:
   1) Sequencing data path in **/FA-NIVA/assets/samplesheet.csv**. The file directory is the absolute path in your file system. 
   2) Reference genome path and dorado details in **/FA-NIVA/profile.config**. Besides the reference path, annotsvAnnotations database directory as well as the dorado model details can be specified in this file. It is also possible to provide the genome path in the command line using --fasta, --fasta_index accordingly.
   3) Resource specification in **/FA-NIVA/conf/base.config**. GPU is needed for dorado basecaller.
   4) Select packages to be used in **/FA-NIVA/nextflow.config**. 
   -In the default setting, annotation part is marked as false. If needed, installation of annotation database is needed (see below).
5. Run the analysis by following command:
```
   nextflow run ./FA-NIVA/ \ # The path to the FA-NIVA package
      -profile fa_niva,docker \ # Corresponding to the setting in /FA-NIVA/profile.config. Beaware that there is no space between fa_niva,docker 
      --outdir ./output # Specify the directory for output results.
```
6. Output file structure (one example output folder can be found in zenodo:https://zenodo.org/records/17284961 ):
````
<sample_id> (folder)

-multiqc (folder)
--multiqc_data (folder)
--multiqc_plots (folder)
--multiqc_report.html
--versions.yml

-pipeline_info (folder)
--execution_report_<time>.html
--execution_timeline_<time>.html
--execution_trace_<time>.txt
--execution_dag_<time>.html
--samplesheet.valid.csv
--software_versions.yml

-<sample_id> (folder)
--basecaller (optional bam output)
--deepvariant 
--pbmm2 (optional cram output)
--sawfish 
--whatshap 

-<sample_id>.html (PycoQC report)

-<sample_id>.json

````


**Notes**
1) the current annotsv docker image does not contain annotationsDir, thus need to be installed first (https://github.com/lgmgeo/AnnotSV/blob/master/bin/INSTALL_annotations.sh). Then manually change the directory in the profile.config file.
2) Deepvariant model_type is set as WGS

**Cite us (to-be-updated):**
FA-NIVA: A Nextflow framework for automated analysis of Nanopore based long-read sequencing data for genetic analysis in Fanconi anemia 

   
<sub>Basic structure is from following repos (2024-12-10):</sub> \
<sub>1. https://github.com/nf-core/nanoseq</sub> \
<sub>2. https://github.com/dhslab/nf-core-wgsnano</sub> \
<sub>2.1 since the firewall is restricted to docker, I have simply copied the dorado image from dhslab (https://github.com/dhslab/dhslab-docker-images/pkgs/container/docker-dorado) to my docker hub, version 241016.</sub> \
<sub>2.2 same for https://github.com/dhslab/dhslab-docker-images/pkgs/container/docker-whatshap, version 240302.</sub>


