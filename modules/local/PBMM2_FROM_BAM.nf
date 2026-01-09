process PBMM2_FROM_BAM {
    tag "$meta.id"
    maxForks 8  // Limits the number of concurrent executions of this process to 8
    label 'process_high'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'jiangyanyu/faniva:v1' :
        'jiangyanyu/faniva:v1' }"

    input:
        tuple val(meta), path (unmapped_bams)
        path (fasta)
        path (fasta_index)
        path (fasta_mmi)

    output:
        // tuple val(meta), path ("*.cram"), emit: cram
        // tuple val(meta), path ("*.cram.crai"), emit: crai
        tuple val(meta), path ("${meta.id}.cram"), path ("${meta.id}.cram.crai"), emit: cram_crai
        path "versions.yml", emit: versions

    script:
        """
        samtools cat \\
            -@ ${task.cpus} \\
            ${unmapped_bams} | \\
        samtools fastq \\
            -@ ${task.cpus} \\
            -c 9 \\
            -0 ${meta.id}.fastq.gz
        
        pbmm2 align \\
                ${fasta_mmi} \\
                ${meta.id}.fastq.gz \\
                --num-threads ${task.cpus} \\
                --preset CCS | \\
        samtools addreplacerg -@ ${task.cpus} -r "ID:${meta.id}\\tSM:${meta.id}" - | \\
        samtools sort -@ ${task.cpus} --reference ${fasta} -O cram -o ${meta.id}.cram

        samtools index -@ ${task.cpus} ${meta.id}.cram

        rm ${meta.id}.fastq.gz

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            samtools: \$(samtools --version | head -n 1 | sed 's/^samtools //'),
            pbmm2: \$(pbmm2 --version | head -n 1 | sed 's/^pbmm2 //g')
        END_VERSIONS
        """
}
