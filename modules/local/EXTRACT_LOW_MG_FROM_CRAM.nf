process EXTRACT_LOW_MG_FROM_CRAM {
    tag "$meta.id"
    maxForks 24  // Limits the number of concurrent executions of this process to 24
    label 'process_medium'

    conda "bioconda::samtools=1.16.1"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/samtools:1.16.1--h6899075_1' :
        'quay.io/biocontainers/samtools:1.16.1--h6899075_1' }"

    input:
        tuple val(meta), path(cram), path(crai)
        path(fasta)

    output:
        tuple val(meta), path("${meta.id}.low_MG.cram"), path("${meta.id}.low_MG.cram.crai"), emit: cram_crai
        path("versions.yml"), emit: versions

    script:
     """
        samtools view \
            -@ ${task.cpus} \\
            --reference ${fasta} \\
            -e '[mg]<95' \\
            -O cram \\
            -o ${meta.id}.low_MG.cram \\
            ${cram}

        samtools index -@ ${task.cpus} ${meta.id}.low_MG.cram

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            samtools: \$(samtools --version | head -n1 | sed 's/^samtools //')
        END_VERSIONS
        """
}
