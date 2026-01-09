nano-fanconi is an nf-core based workflow to analyze nanopore long-read sequencing data for routine fanconi diagnosis.
![Description](https://github.com/UKWgenommedizin/FA-NIVA/blob/main/docs/workflow_complete_graph.png)
**Basic steps to use the workflow**:
1. Install nextflow according to its manual (https://www.nextflow.io/docs/latest/install.html)
2. Download and unzip (or git clone) nano-fanconi package from github (https://github.com/UKWgenommedizin/FA-NIVA)
```
git clone -b main https://github.com/UKWgenommedizin/FA-NIVA
```
4. Adjusting file path accordingly:
   1) Sequencing data path in **/FA-NIVA/assets/samplesheet.csv**. The file directory is the absolute path in your file system. 
   2) Reference genome path in **/FA-NIVA/profile.config**. Besides the reference path, annotsvAnnotations database directory as well as the dorado model details can be specified in this file.
   3) Select packages to be used in **/FA-NIVA/nextflow.config**. 
   -Select (true or false) the programs one likes to use. The dafault setting is for analyzing human nanopore data. If aimed to analyze other genomes, please unselect variants annotations, use joint-snv-sv for phasing (target only for FANCA gene).
   -In the default setting, annotation part is marked as false. If needed, installation of annotation database is needed (see below).
   4) Resource specification in **/FA-NIVA/conf/base.config**.
5. Run the analysis by following command:
```
   nextflow run ./FA-NIVA/ \ # The path to the nano-fanconi package
      -profile fa_niva,docker \ # Corresponding to the setting in /nf-core_nano-fanconi/profile.config. Beaware that no space between nanofanconi,docker 
      --outdir ./output # Specify the directory for output results.
```
6. Output file structure:
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

-<sample_name> (folder)
--basecaller (optional bam output)
--deepvariant 
--pbmm2 (optional bam output)
--sawfish 
--whatshap 

-<sample_name>.html (PycoQC report)

-<sample_name>.json

````


**Notes**
1) the current annotsv docker image does not contain annotationsDir, thus need to be installed first (https://github.com/lgmgeo/AnnotSV/blob/master/bin/INSTALL_annotations.sh). Then manually change the directory in the profile.config file.
2) Deepvariant model_type is set as WGS

**Cite us (to-be-updated):**
Nano-Fanconi: A Nextflow framework for automated analysis of Nanopore based long-read sequencing data for Fanconi anemia diagnosis. 

   
<sub>Basic structure is from following repos (2024-12-10):</sub> \
<sub>1. https://github.com/nf-core/nanoseq</sub> \
<sub>2. https://github.com/dhslab/nf-core-wgsnano</sub> \
<sub>2.1 since the firewall is restricted to docker, I have simply copied the dorado image from dhslab (https://github.com/dhslab/dhslab-docker-images/pkgs/container/docker-dorado) to my docker hub, version 241016.</sub> \
<sub>2.2 same for https://github.com/dhslab/dhslab-docker-images/pkgs/container/docker-whatshap, version 240302.</sub>


