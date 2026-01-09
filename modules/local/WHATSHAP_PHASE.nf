process WHATSHAP_PHASE {
    tag "$meta.id:$chrom"
    label 'process_high'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://hub.docker.com/repository/docker/jiangyanyu/docker-whatshap/' :
        'jiangyanyu/docker-whatshap:v251127' }"

    input:
        tuple val(meta), path(split_cram), path(split_crai), path(split_vcf), path(split_tbi), val(caller), val(chrom)
        path(fasta)
        path(fasta_index)

    output:
        tuple val(meta), path("${meta.id}.${caller}.${chrom}.whatshap_phase.vcf.gz"), path("${meta.id}.${caller}.${chrom}.whatshap_phase.vcf.gz.tbi"), val(caller), val(chrom), emit: vcf_tbi_caller_chrom
        path  ("versions.yml")                                       , emit: versions

    script:

    """
    whatshap phase -o ${meta.id}.${caller}.${chrom}.whatshap_phase.vcf.gz \\
        --reference=${fasta} \\
        ${meta.id}.${caller}.${chrom}.vcf.gz \\
        ${meta.id}.${chrom}.cram


    tabix ${meta.id}.${caller}.${chrom}.whatshap_phase.vcf.gz


    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        whatshap: \$(whatshap --version |sed 's/^.*Version: //')
    END_VERSIONS

    """
}
