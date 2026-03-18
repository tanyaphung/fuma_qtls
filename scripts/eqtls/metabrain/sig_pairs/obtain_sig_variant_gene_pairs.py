import argparse
import gzip

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--top_effect_fp', required=True)
    parser.add_argument('--full_sumstat', required=True)
    parser.add_argument('--outfile', required=True)
    args = parser.parse_args()
    return args

def get_pthreshold(infile):
    """
    returns a dictionary of {gene:threshold}
    example input: 2021-07-23-basalganglia-EUR-30PCs-TopEffects.txt.gz
    """
    gene_thresh_dict = {}
    with gzip.open(infile, "rt") as f:
        for line in f:
            if line.startswith("Gene"):
                continue
            items = line.rstrip("\n").split("\t")
            gene_thresh_dict[items[4]] = float(items[25])
    return gene_thresh_dict
            
def main():
    args = parse_args()
    
    gene_thresh_dict = get_pthreshold(args.top_effect_fp)
    
    output = open(args.outfile, "w")
    
    with gzip.open(args.full_sumstat, "rt") as f:
        for line in f:
            if line.startswith("Gene"):
                continue
            items = line.rstrip("\n").split("\t")
            gene = items[4]
            pval = items[11]
            if float(pval) < gene_thresh_dict[gene]:
                chrom = items[6]
                pos_grch38 = int(items[7])
                alleles = items[8].split("/")
                tmp_alt_allele = items[9]
                if len(alleles) > 2: 
                    continue
                if alleles[1] == tmp_alt_allele:
                    alt_allele = alleles[1]
                    ref_allele = alleles[0]
                else:
                    alt_allele = alleles[0]
                    ref_allele = alleles[1]
                variant_id = items[5].split(":")[2]
                beta = items[14]
                
                out = ["chr"+ chrom, str(pos_grch38 - 1), str(pos_grch38), ref_allele, alt_allele, variant_id, gene, "cis", beta, str(pval)]
                print("\t".join(out), file=output)
    output.close()
        
if __name__ == "__main__":
    main()
    
    
