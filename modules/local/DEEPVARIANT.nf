// Function to determine the label
def determineLabel() {
    return params.use_gpu ? 'process_gpu_long' : 'process_high'
}
def processLabel = determineLabel()

process DEEPVARIANT {
    tag "$meta.id"
    maxForks 4  // Limits the number of concurrent executions of this process to 4
    label processLabel

    container "google/deepvariant:1.9.0-gpu"

    // Exit if running this module with -profile conda / -profile mamba
    if (workflow.profile.tokenize(',').intersect(['conda', 'mamba']).size() >= 1) {
        exit 1, "DEEPVARIANT module does not support Conda. Please use Docker / Singularity / Podman instead."
    }

    input:
        tuple val(meta), path(cram), path(crai)
        path(fasta)
        path(fai)

    output:
        tuple val(meta), path("${meta.id}.deepvariant.vcf.gz"), path("${meta.id}.deepvariant.vcf.gz.tbi"), val("deepvariant"), emit: vcf_tbi
        path "versions.yml", emit: versions

    when:
        task.ext.when == null || task.ext.when

    script:
        
        """
        /opt/deepvariant/bin/run_deepvariant \\
            --num_shards=${task.cpus} \\
            --model_type=PACBIO \\
            --disable_small_model \\
            --postprocess_variants_extra_args='only_keep_pass=true' \\
            --ref=${fasta} \\
            --reads=${cram} \\
            --output_vcf=${meta.id}.deepvariant.vcf.gz

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            deepvariant: \$(echo \$(/opt/deepvariant/bin/run_deepvariant --version) | sed 's/^.*version //; s/ .*\$//' )
        END_VERSIONS
        """
}
