# this script is used to format the file {CELLTYPE}_eqtl_top_assoc.tsv.gz
import pandas as pd
import argparse
import os
import tabix
import gzip

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--dbsnp_dir', help='directory containing dbSNP tabix files')
parser.add_argument('--chrom', required=True, help='Chromosome number.')
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

# get the tabix file for dbSNP
tb = tabix.open(os.path.join(args.dbsnp_dir, f"dbSNP157.chr{args.chrom}.vcf.gz"))

def main():
    
    ensembl_symbol_dict = symbol_lookup()

    input_fn = args.input
    output = open(args.output, "w")
    
    fix_beta_idx = 0
    fix_p_idx = 0
    
    with gzip.open(input_fn, 'rt') as f:
        for line in f:
            if line.startswith("feature"):
                headers = line.rstrip("\n").split("\t")
                fix_beta_idx = headers.index("fixed_beta")
                fix_p_idx = headers.index("Fixed_P")
                continue
            items = line.rstrip("\n").split("\t")
            chrom = items[2].split("chr")[1]
            if chrom != args.chrom:
                continue
            pos = items[3]
            alt_allele = items[6]
            tmp_allele_1 = items[4]
            tmp_allele_2 = items[5]
            if alt_allele == tmp_allele_1:
                ref_allele = tmp_allele_2
            elif alt_allele == tmp_allele_2:
                ref_allele = tmp_allele_1
            else: 
                continue #the allele is not matching, skip it
                
            ensemble_id = items[0].split(".")[0]
            gene_symbol = ensembl_symbol_dict.get(ensemble_id, "NA")
            
            pvalue = items[fix_p_idx]
            beta = items[fix_beta_idx]
            
            ref, alt, db_rsid, beta, skip_count = check_alleles(tb, chrom, pos, ref_allele, alt_allele, beta)
            if skip_count > 0:
                continue  # skip this SNP
        
            out = ["chr" + chrom, str(int(pos)-1), str(pos), ref, alt, db_rsid, gene_symbol, "cis", str(beta), str(pvalue)]
            print("\t".join(out), file=output)
            
        output.close()

if __name__ == '__main__':
    main()