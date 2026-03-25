# This script filters the full sumstat results for variant pair where the nominal p < 0.05. 
# This is because the datasets does not include only the significant variant gene pair. Therefore, in this dataset, it is only possible if a threshold is specified
# from the file such as sceQTL_bryois2022Brain_Astrocytes_chr22.txt.gz, keep rows where p < 0.05, returns data in format for liftover

import gzip
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--chrom', required=True, help='Chromosome number.')
args = parser.parse_args()

def symbol_lookup():
    gene_conversion_file = "/GeneConversion/gencode.v39.gene_name_conversion.tsv" #TODO: put in the correct path
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