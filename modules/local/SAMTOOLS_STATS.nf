process SAMTOOLS_STATS {
    label 'process_low'

    container 'ghcr.io/dhslab/docker-baseimage:241109'

    input:
    tuple val(meta), path(haplotagged_cram)

    output:
        tuple val(meta), path("${meta.id}.combined.stats.txt"), emit: combined_stats
        tuple val(meta), path("${meta.id}.hap1.stats.txt")    , emit: hap1_stats
        tuple val(meta), path("${meta.id}.hap2.stats.txt")    , emit: hap2_stats
        path  ("versions.yml")                                    , emit: versions

    script:
    """
    samtools stats -@ ${task.cpus} $haplotagged_cram > ${meta.id}.stats.txt
    samtools view -@ ${task.cpus} -h -d HP:1 -u $haplotagged_cram | samtools stats -@ ${task.cpus} - > ${meta.id}.hap1.stats.txt
    samtools view -@ ${task.cpus} -h -d HP:2 -u $haplotagged_cram | samtools stats -@ ${task.cpus} - > ${meta.id}.hap2.stats.txt


    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        samtools: \$(echo \$(samtools --version 2>&1) | sed 's/^.*samtools //; s/Using.*\$//')
    END_VERSIONS
    """

}
