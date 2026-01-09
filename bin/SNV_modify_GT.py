#!/usr/bin/env python3

from cyvcf2 import VCF, Writer
import sys
import argparse
import shutil
import csv
import os

# Argument parser
parser = argparse.ArgumentParser(description="Adjust SNV genotypes within a deletion region.")
parser.add_argument("--sv_vcf", required=True, help="Input SV VCF file (bgzipped and indexed).")
parser.add_argument("--snv_vcf", required=True, help="Input SNV VCF file (bgzipped and indexed).")
parser.add_argument("--regions_csv", required=True, help="CSV file with chrom,start,end per line.")
parser.add_argument("--output_vcf", required=True, help="Output VCF file with adjusted genotypes.")
args = parser.parse_args()


# # Ensure output directory exists following project conventions
# output_dir = os.path.dirname(args.output_vcf)
# if output_dir and not os.path.exists(output_dir):
#     os.makedirs(output_dir)


# Load query regions from CSV
regions = []
with open(args.regions_csv, "r") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if len(row) < 3:
            continue
        chrom, start, end = row[0], int(row[1]), int(row[2])
        regions.append((chrom, start, end))

if not regions:
    print("No valid regions in CSV — copying original SNV VCF to output.")
    shutil.copyfile(args.snv_vcf, args.output_vcf)
    sys.exit(0)

# Step 1: Scan SV VCF to find overlapping deletion
sv_vcf = VCF(args.sv_vcf)
adjust_regions = []

for chrom, qstart, qend in regions:
    region_found = False

    for variant in sv_vcf(f"{chrom}:{qstart}-{qend}"):
        if variant.is_sv and variant.INFO.get("SVTYPE") == "DEL":
            sv_start = variant.POS
            sv_end = int(variant.INFO.get("END", 0))
            sv_gt = variant.genotypes[0]  # Assuming single sample VCF

            if sv_start <= qend and sv_end >= qstart:
                
                #FUTURE WORK: Check genotype is het or hom alt

                # Collect genotype info per sample
                genotypes = variant.genotypes  # list of tuples [(0, 1, True), (1, 1, False), ...]
 
                # Optional: format as strings like '0/1', '1/1', etc.
                gt_strings = [
                    f"{gt[0]}/{gt[1]}" if gt[0] is not None else "./."
                    for gt in genotypes
                ]
 
                adjust_regions.append((chrom, sv_start, sv_end))

                print(f"Found deletion: {chrom}:{sv_start}-{sv_end} overlapping region {chrom}:{qstart}-{qend}")
                region_found = True
                break

    if not region_found:
        print(f"No deletion overlap found for region {chrom}:{qstart}-{qend}")

sv_vcf.close()

# If no regions require adjustment, simply copy file
# if not adjust_regions:
#     print("No overlapping deletions found — copying original SNV VCF.")
#     # shutil.copyfile(args.snv_vcf, args.output_vcf)
    
#     sys.exit(0)

# Step 2: Modify SNV VCF based on detected region
snv_vcf = VCF(args.snv_vcf)
out = open(args.output_vcf, "w")

# Write header
for line in snv_vcf.raw_header.strip().split("\n"):
    out.write(line + "\n")

# Process variants
for variant in snv_vcf:
    chrom = variant.CHROM
    pos = variant.POS
    fields = str(variant).strip().split("\t")

    # Check whether SNV falls inside any deletion interval
    if adjust_regions:
        
        # There are deletion regions to adjust
        for variant in snv_vcf:
            
            chrom = variant.CHROM
            pos = variant.POS
            fields = str(variant).strip().split("\t")
    
            # Check whether SNV falls inside any deletion interval
            for (rch, rstart, rend) in adjust_regions:
                if chrom == rch and rstart <= pos <= rend:
                    format_keys = fields[8].split(":")
                    if "GT" in format_keys:
                        gt_index = format_keys.index("GT")
                        # Adjust genotypes
                        for i in range(9, len(fields)):
                            sample_data = fields[i].split(":")
                            gt = sample_data[gt_index]
                            if gt in ("0/0", "0|0", "1/1", "1|1"):
                                sample_data[gt_index] = "0/1"
                                fields[i] = ":".join(sample_data)
                    break  # stop checking further regions for this SNV
    
            out.write("\t".join(fields) + "\n")
    
    else:
        # No deletion regions to adjust — write SNVs unchanged
        print("No deletion regions found — writing SNVs unchanged.")
        for variant in snv_vcf:
            out.write(str(variant).strip() + "\n")
 
out.close()
snv_vcf.close()
