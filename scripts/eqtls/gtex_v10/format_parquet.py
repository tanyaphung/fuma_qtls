# this script is used to format the file {TISSUE}.v10.allpairs.chr{CHR}.parquet
import pandas as pd
import argparse
import os
import tabix

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True)
parser.add_argument('-o', '--output', required=True)
parser.add_argument('--dbsnp_dir', help='directory containing dbSNP tabix files')
parser.add_argument('--sample_size', required=True, help='Sample size.')
parser.add_argument('--type', required=True, help='type of QTL: eQTL, sQTL, etc.')
parser.add_argument('--chrom', required=True, help='Chromosome number.')
args = parser.parse_args()

def check_alleles(tb, chrom, pos, ref, alt, beta, maf):
    """Check if the alleles match, are flipped, or do not match."""
    query_region = f"{chrom}:{pos}-{pos}"
    # print(f"Querying dbSNP for region: {query_region}")
    queried_results = tb.querys(query_region)
    
    db_rsid = "NA"
    
    beta_f = float(beta)
    maf_f = float(maf)
    
    for query in queried_results:
        db_ref = query[3]
        db_alt_alleles = set(query[4].split(','))
        rsid = query[2]
        
        if ref == db_ref and alt in db_alt_alleles:
            # alleles match
            return ref, alt, rsid, beta, maf, 0
        
        if ref in db_alt_alleles and alt == db_ref:
            # alleles are flipped
            # print(f"Warning: Alleles are flipped for {chrom}:{pos}. Input REF: {ref}, ALT: {alt}. Flipping alleles and effect size.")
            return (
                alt,
                ref,
                rsid,
                str(-beta_f),
                1.0 - maf_f,
                0,
            )
    # else:
    #     # no match found
    #     print(f"Warning: Alleles do not match dbSNP for {chrom}:{pos}. Skipping this SNP.")
    #     return ref, alt, db_rsid, beta, maf, 1
    
    return ref, alt, db_rsid, beta, maf, 1
        

# get the tabix file for dbSNP
tb = tabix.open(os.path.join(args.dbsnp_dir, f"dbSNP157.chr{args.chrom}.vcf.gz"))


    
def format_parquet():
    
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
        gene = row[gene_col]
        pvalue = row['pval_nominal']
        beta = row['slope']
        maf = row['af']
        
        ref, alt, db_rsid, beta, maf, skip_count = check_alleles(tb, chrom, pos, ref, alt, beta, maf)
        if skip_count > 0:
            skipped_snps += 1
            continue  # skip this SNP
        
        

        out = [str(chrom), str(pos), ref, alt, db_rsid, gene, str(pvalue), str(beta), str(maf), str(args.sample_size)]
        print("\t".join(out), file=output)
    
    output.close()
    print(f"Total SNPs processed: {total_snps}")
    print(f"SNPs skipped: {skipped_snps}")

if __name__ == '__main__':
    format_parquet()