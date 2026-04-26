# this script is used to format the file {TISSUE}.v10.sQTLs.signif_pairs.parquet
import pandas as pd
import argparse
import os
import tabix

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--dbsnp_dir', help='directory containing dbSNP tabix files') 
parser.add_argument('--type', required=True, help='type of QTL: eQTL, sQTL, etc.')
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

def format_parquet():
    
    ensembl_symbol_dict = symbol_lookup()
    
    total_snps = 0
    skipped_snps = 0

    input_fn = args.input
    output = open(args.output, "w")
    
    if args.type == 'eQTL':
        gene_col = 'gene_id'
    else: 
        gene_col = 'phenotype_id'

    data = pd.read_parquet(input_fn, engine='pyarrow', columns=['variant_id', gene_col, 'pval_nominal', 'slope', 'af'])

    for index, row in data.iterrows():
        
        total_snps += 1
        
        chrom, pos, ref, alt = row['variant_id'].split('_')[:4]
        chrom = chrom.replace('chr', '')
        if chrom != args.chrom:
            continue
        ensembl = row[gene_col].split(":")[-1].split(".")[0]
        gene = ensembl_symbol_dict.get(ensembl, "NA")
        # gene = row[gene_col]
        pvalue = row['pval_nominal']
        beta = row['slope']
        
        ref, alt, db_rsid, beta, skip_count = check_alleles(tb, chrom, pos, ref, alt, beta)
        if skip_count > 0:
            skipped_snps += 1
            continue  # skip this SNP
        
        out = ["chr" + chrom, str(int(pos)-1), str(pos), ref, alt, db_rsid, gene, "cis", str(beta), str(pvalue)]
        print("\t".join(out), file=output)
    
    output.close()
    print(f"Total SNPs processed: {total_snps}")
    print(f"SNPs skipped: {skipped_snps}")

if __name__ == '__main__':
    format_parquet()