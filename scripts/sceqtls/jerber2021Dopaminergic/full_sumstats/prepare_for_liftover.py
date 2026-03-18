# this script prepares the input `D11.FPP.qtl_results_all.sorted.txt.gz` for liftover from GRCh37 to GRCh38
import gzip
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--chrom', required=True, help='Chromosome number.')
args = parser.parse_args()

def main():
    input = args.input
    output = args.output
    curr_chrom = args.chrom
    
    out = open(output, "w")
    
    with gzip.open(input, "rt") as f: 
        for line in f:
            if line.startswith("feature_id"):
                continue
            items = line.rstrip("\n").split("\t")
            gene = items[0]
            snp_info = items[1].split("_")
            chrom = snp_info[0]
            if chrom == curr_chrom:
                pos_grch37 = snp_info[1]
                if items[13] == snp_info[3]:
                    ref = snp_info[2]
                    alt = snp_info[3]
                elif items[13] == snp_info[2]:
                    ref = snp_info[3]
                    alt = snp_info[2]
                else: #something is wrong with the alleles assignment, skip
                    continue
                pval = items[2]
                beta = items[3]
                sample_size = items[9]
                maf = items[15]
                
                out_line = ["chr"+ chrom, str(int(pos_grch37)-1), pos_grch37, ref, alt, gene, pval, beta, sample_size, maf]
                print("\t".join(out_line), file=out)
                
    out.close()
if __name__ == '__main__':
    main()