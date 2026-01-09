process SPLIT_VCF_BY_CHROM {
    tag "$meta.id:$caller:$chrom"
    maxForks 24  // Limits the number of concurrent executions of this process to 24
    label 'process_medium'

    conda "bioconda::bcftools=1.16"
    container "quay.io/biocontainers/bcftools:1.16--hfe4b78e_1"

    input:
        tuple val(meta), path(vcf), path(tbi), val(caller), val(chrom)

    output:
        tuple val(meta), path("${meta.id}.${caller}.${chrom}.vcf.gz"), path("${meta.id}.${caller}.${chrom}.vcf.gz.tbi"), val(caller), val(chrom), emit: vcf_tbi
        path("versions.yml"), emit: versions

    script:
        """
        bcftools view \\
            --threads ${task.cpus} \\
            -r ${chrom} \\
            -O z \\
            -o ${meta.id}.${caller}.${chrom}.vcf.gz \\
            ${vcf}

        tabix ${meta.id}.${caller}.${chrom}.vcf.gz

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            bcftools: \$(bcftools --version | head -n1 | sed 's/^bcftools //')
        END_VERSIONS
        """
}
