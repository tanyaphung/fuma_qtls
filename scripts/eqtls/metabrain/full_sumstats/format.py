# this script is used to format the file 2021-07-23-{region}-EUR-30PCs-chr{i}.txt.gz
import pandas as pd
import argparse
import os
import tabix
import gzip

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True)
parser.add_argument('-o', '--output', required=True)
parser.add_argument('--dbsnp_dir', help='directory containing dbSNP tabix files')
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
            return (
                alt,
                ref,
                rsid,
                str(-beta_f),
                1.0 - maf_f,
                0,
            )
    return ref, alt, db_rsid, beta, maf, 1
        

# get the tabix file for dbSNP
tb = tabix.open(os.path.join(args.dbsnp_dir, f"dbSNP157.chr{args.chrom}.vcf.gz"))

def format():
    total_snps = 0
    skipped_snps = 0

    input_fn = args.input
    output = open(args.output, "w")
    
    with gzip.open(input_fn, "rt") as f:
        for line in f:
            if line.startswith("Gene"):
                continue
            total_snps += 1
            items = line.rstrip("\n").split("\t")
            chrom = items[6]
            pos = items[7]
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
            gene = items[0]
            pvalue = items[11]
            beta = items[14]
            maf = items[10]
            sample_size = int(items[12])
            
            ref, alt, db_rsid, beta, maf, skip_count = check_alleles(tb, chrom, pos, ref_allele, alt_allele, beta, maf)
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