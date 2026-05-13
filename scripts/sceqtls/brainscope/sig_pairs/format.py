# this script is used to format the file {CELLTYPE}_eqtl_top_assoc.tsv.gz
import pandas as pd
import argparse
import os
import tabix

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--dbsnp_dir', help='directory containing dbSNP tabix files')
parser.add_argument('--chrom', required=True, help='Chromosome number. ')
args = parser.parse_args()

def check_alleles(tb, chrom, pos, ref, alt, beta):
    """Check if the alleles match, are flipped, or do not match."""
    query_region = f"{chrom}:{pos}-{pos}"
    # print(f"Querying dbSNP for region: {query_region}")
    queried_results = tb.querys(query_region)
    
    db_rsid = "NA"
    
    beta_f = float(beta)
    
    for query in queried_results:
        db_ref = query[3]
        db_alt_alleles = set(query[4].split(','))
        rsid = query[2]
        
        if ref == db_ref and alt in db_alt_alleles:
            # alleles match
            return ref, alt, rsid, beta, 0
        
        if ref in db_alt_alleles and alt == db_ref:
            # alleles are flipped
            # print(f"Warning: Alleles are flipped for {chrom}:{pos}. Input REF: {ref}, ALT: {alt}. Flipping alleles and effect size.")
            return (
                alt,
                ref,
                rsid,
                str(-beta_f),
                0,
            )
    
    return ref, alt, db_rsid, beta, 1


# get the tabix file for dbSNP
tb = tabix.open(os.path.join(args.dbsnp_dir, f"dbSNP157.chr{args.chrom}.vcf.gz"))

def main():

    input_fn = args.input
    output = open(args.output, "w")
    
    with open(input_fn, 'r') as f:
        for line in f:
            items = line.rstrip("\n").split()
            chrom_orig, pos, ref_allele, alt_allele = items[7].split(":")
            chrom = chrom_orig.split("chr")[1]
            if chrom != args.chrom:
                continue
                
            gene_symbol = items[0]
            
            pvalue = items[11]
            beta = items[13]
            
            ref, alt, db_rsid, beta, skip_count = check_alleles(tb, chrom, pos, ref_allele, alt_allele, beta)
            if skip_count > 0:
                continue  # skip this SNP
        
            out = ["chr" + chrom, str(int(pos)-1), str(pos), ref, alt, db_rsid, gene_symbol, "cis", str(beta), str(pvalue)]
            print("\t".join(out), file=output)
            
        output.close()

if __name__ == '__main__':
    main()