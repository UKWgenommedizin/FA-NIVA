process MERGE_VCF {
    label 'process_medium'

    conda "bioconda::bcftools=1.16"
    container "quay.io/biocontainers/bcftools:1.16--hfe4b78e_1"

    input:
        tuple val(meta), path(vcfs)

    output:
        tuple val(meta), path("${meta.id}.phased.merged.vcf.gz"), emit: vcf
        path("versions.yml"), emit: versions

    script:
        def vcf_list = vcfs instanceof List ? vcfs.join(' ') : vcfs
        """
        bcftools concat -O z -o ${meta.id}.phased.merged.vcf.gz ${vcf_list}
        bcftools index ${meta.id}.phased.merged.vcf.gz

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            bcftools: $(bcftools --version | head -n1 | sed 's/^bcftools //')
        END_VERSIONS
        """
}
