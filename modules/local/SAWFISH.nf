process SAWFISH {
    tag "$meta.id"
    maxForks 8  // Limits the number of concurrent executions of this process to 8
    label 'process_high'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'jiangyanyu/faniva:v1' :
        'jiangyanyu/faniva:v1' }"

    input:
        tuple val(meta), path(cram), path(crai)
        path (fasta)
        path (fasta_index)

    output:
        tuple val(meta), path ("${meta.id}.sawfish.vcf.gz"), path ("${meta.id}.sawfish.vcf.gz.tbi"), val("sawfish"), emit: vcf_tbi
        path "versions.yml", emit: versions

    script:
        """   
        source /opt/conda/etc/profile.d/conda.sh  
        conda activate sawfish

        sawfish discover \\
                --threads ${task.cpus} \\
                --ref ${fasta} \\
                --bam ${cram} \\
                --output-dir ${meta.id}.discover

        sawfish joint-call \\
                --threads ${task.cpus} \\
                --sample ${meta.id}.discover \\
                --output-dir ${meta.id}.joint-call

        cp -l ${meta.id}.joint-call/genotyped.sv.vcf.gz ${meta.id}.sawfish.vcf.gz
        cp -l ${meta.id}.joint-call/genotyped.sv.vcf.gz.tbi ${meta.id}.sawfish.vcf.gz.tbi

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            sawfish: \$(sawfish --version 2>&1)
        END_VERSIONS
        """
}
        // tuple val(meta), path ("joint-call/*alignment*"), emit: bam