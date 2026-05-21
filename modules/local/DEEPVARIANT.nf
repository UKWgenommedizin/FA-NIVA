// Function to determine the label
def determineLabel() {
    return params.use_gpu ? 'process_gpu_long' : 'process_high'
}
def processLabel = determineLabel()

process DEEPVARIANT {
    tag "$meta.id"
    maxForks 4  // Limits the number of concurrent executions of this process to the maximum GPUs available
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

    beforeScript """
        WORK_DIR=\$(mktemp -d)
        # or find the actual task workdir
        sleep \$((RANDOM % 15))
        GPU_ID=\$(nvidia-smi --query-gpu=index,memory.free \\
                    --format=csv,noheader,nounits \\
                | sort -t',' -k2 -rn \\
                | head -1 \\
                | cut -d',' -f1 \\
                | tr -d ' ')
        echo \$GPU_ID > /tmp/.gpu_env_${meta.id}
        """



    script:
        
        """
        export CUDA_VISIBLE_DEVICES=\$(cat /tmp/.gpu_env_${meta.id})
        echo "Using GPU: \$CUDA_VISIBLE_DEVICES"

        /opt/deepvariant/bin/run_deepvariant \\
            --num_shards=${task.cpus} \\
            --model_type=PACBIO \\
            --disable_small_model \\
            --postprocess_variants_extra_args='only_keep_pass=true' \\
            --ref=${fasta} \\
            --reads=${cram} \\
            --output_vcf=${meta.id}.deepvariant.vcf.gz

        # cleanup
        rm -f /tmp/.gpu_env_${meta.id}

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            deepvariant: \$(echo \$(/opt/deepvariant/bin/run_deepvariant --version) | sed 's/^.*version //; s/ .*\$//' )
        END_VERSIONS
        """
}
