# this script splits the file `snp_pos.txt.gz` for per chromosome
import os
import gzip
import sys

input_file = "snp_pos.txt.gz"

chrom = sys.argv[1] #1, 2, ...

outfile = open("snp_pos_" + chrom + ".txt", "w")
header = ["SNP", "chrom", "pos_grch38", "effect_allele", "other_allele", "MAF"]
print("\t".join(header), file=outfile)

with gzip.open(input_file, "rt") as f:
    for line in f:
        if line.startswith("SNP"):
            continue
        items = line.rstrip("\n").split("\t")
        snp_chrom = items[1].split(":")[0]
        snp_pos = items[1].split(":")[1]
        if snp_chrom == 'chr' + chrom:
            out = [items[0], chrom, snp_pos, items[3], items[4], items[5]]
            print("\t".join(out), file=outfile)
outfile.close()
        