process FAIDX_REFERENCE {
    label 'process_medium'

    conda "bioconda::samtools=1.16"
    container "quay.io/biocontainers/samtools:1.16.1--h6899075_1"

    input:
        path fasta
        
    output:
        path fasta, emit: fasta
        path "${fasta}.fai", emit: fasta_index
        path "versions.yml", emit: versions

    script:
        """
        # Create FAI index
        samtools faidx ${fasta}

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            samtools: \$(samtools --version | head -n1 | sed 's/^samtools //')
        END_VERSIONS
        """
}
