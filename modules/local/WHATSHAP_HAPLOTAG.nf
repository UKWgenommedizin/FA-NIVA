process WHATSHAP_HAPLOTAG {
    tag "$meta.id:$chrom"
    label 'process_medium'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://hub.docker.com/repository/docker/jiangyanyu/docker-whatshap/' :
        'jiangyanyu/docker-whatshap:v251127' }"

    input:
        tuple val(meta), path(split_cram), path(split_crai), path(split_vcf), path(split_tbi), val(caller), val(chrom)
        path(fasta)
        path(fasta_index)

    output:
        tuple val(meta), path("${meta.id}.${chrom}.haplotagged.cram"), path("${meta.id}.${chrom}.haplotagged.cram.crai"), val(chrom), emit: cram_crai
        path  ("versions.yml")                                       , emit: versions

    script:
    
    """

    whatshap haplotag \\
        --tag-supplementary \\
        --ignore-read-groups \\
        --output-threads=${task.cpus} \\
        -o ${meta.id}.${chrom}.haplotagged.cram \\
        --reference ${fasta} \\
        ${split_vcf} \\
        ${split_cram} || true


    samtools index -@ ${task.cpus} ${meta.id}.${chrom}.haplotagged.cram
    

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        whatshap: \$(whatshap --version |sed 's/^.*Version: //')
    END_VERSIONS
    """
}
