# This script filters the full sumstat results for variant pair where the nominal p < 0.05. 
# This is because in supplementary table 7 that can be downloaded from https://www.nature.com/articles/s41588-021-00801-6#Sec31, this file does contain significant snp-gene pair but it does not separate out by cell types.
# As a results, for this dataset, I will employ a similar strategy to bryois2022Brain datasets, which is to only keep snp-gene pair where nominal p < 0.05 
# from the file such as sceQTL_jerber2021Dopaminergic_D11.FPP.chr22.txt.gz, keep rows where p < 0.05, returns data in format for liftover

import gzip
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--chrom', required=True, help='Chromosome number.')
args = parser.parse_args()

def symbol_lookup():
    gene_conversion_file = "" #TODO: put in the correct path
    ensembl_symbol_dict = {}
    with open(gene_conversion_file, "r") as f:
        for line in f:
            if line.startswith("gene_id"):
                continue
            items = line.strip().split("\t")
            gene_symbol = items[2]
            ensembl_id = items[0].split(".")[0]
            ensembl_symbol_dict[ensembl_id] = gene_symbol
    return ensembl_symbol_dict



def main():
    outfile = open(args.output, "w")
    
    ensembl_symbol_dict = symbol_lookup()
    
    with gzip.open(args.input, "rt") as f:
        for line in f:
            items = line.rstrip("\n").split("\t")
            if float(items[6]) > 0.05:
                continue
            
            out = ["chr"+ items[0], str(int(items[1]) - 1), items[1], items[2], items[3], items[4], ensembl_symbol_dict.get(items[5], "NA"), "cis", items[7], items[6]]
            print("\t".join(out), file=outfile)
            
    outfile.close()
    
    
if __name__ == '__main__':
    main()