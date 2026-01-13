process EDIT_SNV_GENOTYPE {
    tag "$meta.id:$chrom"
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'jiangyanyu/faniva:v1.1' :
        'jiangyanyu/faniva:v1.1' }"

    // conda "bioconda::bcftools=1.16"
    // container "quay.io/biocontainers/bcftools:1.16--hfe4b78e_1"


    input:
        tuple val(meta), path(snv_vcf), path(snv_tbi), path(sv_vcf), path(sv_tbi), val(chrom)
        path regions_csv
        
    output:
        tuple val(meta), path("${meta.id}.deepvariant.${chrom}.edited_gt.vcf"), val(chrom), emit: vcf
        path "versions.yml"                                                                                   , emit: versions

    // when:
    // task.ext.when == null || task.ext.when

    script: // This script is bundled with the pipeline, in FA-NIVA/bin/
    
    """
    SNV_modify_GT.py \\
        --snv_vcf ${snv_vcf} \\
        --sv_vcf ${sv_vcf} \\
        --regions_csv ${regions_csv} \\
        --output_vcf ${meta.id}.deepvariant.${chrom}.edited_gt.vcf


    # bgzip ${meta.id}.deepvariant.${chrom}.edited_gt.vcf > ${meta.id}.deepvariant.${chrom}.edited_gt.vcf.gz
    # tabix -p vcf ${meta.id}.deepvariant.${chrom}.edited_gt.vcf.gz


    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
