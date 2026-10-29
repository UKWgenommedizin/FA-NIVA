process PACBIO_BAM_SUMMARY {
    tag "$meta.id"
    label 'process_low'

    container 'ghcr.io/dhslab/docker-baseimage:241109'

    input:
        tuple val(meta), path(input_bams)

    output:
        tuple val(meta), path("${meta.id}.pacbio_summary.tsv"), emit: summary
        tuple val(meta), path("${meta.id}_pacbio_mqc.tsv"), emit: multiqc

    script:
    """
    samtools cat ${input_bams} | \
        samtools view -F 0x900 - | \
        python3 ${projectDir}/bin/pacbio_bam_summary.py ${meta.id}_pacbio_mqc.tsv ${meta.id} > ${meta.id}.pacbio_summary.tsv
    """
}
