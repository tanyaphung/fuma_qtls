# this script formats full sumstat file for LAVA
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

def format():
    
    total_snps = 0
    skipped_snps = 0
    output = open(args.output, "w")
    
    with gzip.open(args.input, "rt") as f:
        for line in f:
            if line.startswith("feature"):
                continue
            total_snps += 1
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
                
            gene = items[0]
            pvalue = items[23]
            beta = items[19]
            maf = "NA"
            sample_size = str(983)
            
            ref, alt, db_rsid, beta, skip_count = check_alleles(tb, chrom, pos, ref_allele, alt_allele, beta)
            if skip_count > 0:
                skipped_snps += 1
                continue  # skip this SNP
        
            out = [str(chrom), str(pos), ref, alt, db_rsid, gene, str(pvalue), str(beta), str(maf), str(sample_size)]
            print("\t".join(out), file=output)
            
        output.close()
        print(f"Total SNPs processed: {total_snps}")
        print(f"SNPs skipped: {skipped_snps}")

if __name__ == '__main__':
    format()