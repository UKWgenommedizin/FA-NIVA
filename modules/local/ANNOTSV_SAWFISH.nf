process ANNOTSV_SAWFISH {
    tag "$meta.id"
    label 'process_high'
    
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'quay.io/biocontainers/annotsv:3.4.4--py312hdfd78af_0' :
        'quay.io/biocontainers/annotsv:3.4.4--py312hdfd78af_0' }"
        
    containerOptions {
        "-v ${params.annotsvAnnotationsDir}:${params.annotsvAnnotationsDir}"
    }

    input:
    tuple val(meta), path(vcf_file)

    output:
    tuple val(meta), path("${prefix}*_AnnotSV.tsv"),  emit: tsv
    path "versions.yml"                    ,  emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args    = task.ext.args ?: ''
    prefix      = task.ext.prefix ?: "${meta.id}"
    
    // Apply annotation mode flag to command
    def mode = params.annotsvMode

    // Change output file name based on annotation mode
    def outputFile = null
        if (mode == 'full') {
               outputFile = "${prefix}_full_AnnotSV.tsv"
            } else if (mode == 'split') {
               outputFile = "${prefix}_split_AnnotSV.tsv"
            } else if (mode == 'both') {
               outputFile = "${prefix}_both_AnnotSV.tsv"
            } else {
               throw new RuntimeException("Invalid option for --annotSV: ${mode}")}

    //Pass any additional flags to the AnnotSV 
    //def extraArgs = params.extraAnnotsvFlags ?: ''
    """
    AnnotSV \\
        -SVinputFile ${meta.id}.sawfish.vcf.gz \\
        -annotationsDir ${params.annotsvAnnotationsDir} \\
        -bedtools bedtools \\
        -bcftools bcftools \\
        -annotationMode ${params.annotsvMode} \\
        -genomeBuild ${params.annotsvGenomeBuild} \\
        -includeCI 1 \\
        -overwrite 1 \\
        -outputFile ${outputFile} \\
        -outputDir ./

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        annotsv: \$(AnnotSV --version |sed 's/^.*Version: //')
    END_VERSIONS
    """
}
