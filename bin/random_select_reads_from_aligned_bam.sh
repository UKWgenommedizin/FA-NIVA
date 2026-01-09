#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e 

# Input and output files
input_bam="$1"           # Aligned BAM file
output_bam="filtered.bam"  # Output BAM file
temp_dir="temp_files"      # Temporary directory for intermediate files

# Create a temporary directory for intermediate files
mkdir -p "$temp_dir"

# Step 1: Extract unique read names from the BAM file
samtools view "$input_bam" | awk '{print $1}' | sort | uniq > "$temp_dir/unique_read_names.txt"

# Step 2: Randomly select 10% of the unique read names
total_reads=$(wc -l < "$temp_dir/unique_read_names.txt")
sample_size=$((total_reads / 100))
shuf -n "$sample_size" "$temp_dir/unique_read_names.txt" > "$temp_dir/sample_read_names.txt"

# Step 3: Extract aligned records of the selected reads and save them as a new BAM file
samtools view -H "$input_bam" > "$temp_dir/header.sam"  # Extract header
samtools view "$input_bam" | grep -F -f "$temp_dir/sample_read_names.txt" > "$temp_dir/body.sam"
cat "$temp_dir/header.sam" "$temp_dir/body.sam" | samtools view -b - > "$temp_dir/unsorted.bam"

# Step 4: Sort and index the new BAM file
samtools sort "$temp_dir/unsorted.bam" -o "$output_bam"
samtools index "$output_bam"

# Clean up temporary files
rm -r "$temp_dir"

echo "Filtered BAM file created: $output_bam"