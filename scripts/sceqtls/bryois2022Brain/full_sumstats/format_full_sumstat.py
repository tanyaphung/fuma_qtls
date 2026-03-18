# this script formats full sumstat file for coloc/LAVA
import pandas as pd
import argparse
import os
import tabix
import gzip

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--input_info', required=True)
parser.add_argument('--output', required=True)
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
    # get chrom, pos, alt, ref, maf
    data = pd.read_csv(args.input, sep=" ", names=["phenotype", "SNP", "distanceTSS", "P", "beta"])
    snp_info = pd.read_csv(f"snp_pos_{args.chrom}.txt", sep="\t")
    data = data.merge(snp_info, left_on="SNP", right_on="SNP", how="left")
    data = data[["chrom", "pos_grch38", "effect_allele", "other_allele", "MAF", "phenotype", "P", "beta"]]
    data.to_csv(args.input_info, sep="\t", index=False)
    
    total_snps = 0
    skipped_snps = 0
    output = open(args.output, "w")
    
    with open(args.input_info, "r") as f:
        for line in f:
            if line.startswith("chrom"):
                continue
            total_snps += 1
            items = line.rstrip("\n").split("\t")
            chrom = items[0]
            pos = items[1]
            alt_allele = items[2]
            ref_allele = items[3]
            gene = items[5].split("_")[1]
            pvalue = items[6]
            beta = items[7]
            maf = items[4]
            sample_size = str(373)
            
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