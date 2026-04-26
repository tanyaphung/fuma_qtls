import pandas as pd
import argparse
import os
import tabix

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True)
parser.add_argument('-o', '--output', required=True)
parser.add_argument('--dbsnp_dir', required=True)
parser.add_argument('--sample_size', required=True)
parser.add_argument('--type', required=True)
parser.add_argument('--chrom', required=True)
args = parser.parse_args()


# --- Load dbSNP ---
tb = tabix.open(os.path.join(args.dbsnp_dir, f"dbSNP157.chr{args.chrom}.vcf.gz"))

# cache to avoid repeated tabix queries
cache = {}


def check_alleles_cached(chrom, pos, ref, alt, beta, maf):
    key = (chrom, pos, ref, alt)
    
    db_rsid = "NA"
    beta_f = float(beta)
    maf_f = float(maf)

    if key in cache:
        if cache[key][-1] == "flip":
            return cache[key][:4] + (str(-beta_f), str((1-maf_f)))
        else:
            return cache[key][:4] + (beta_f, maf_f)
            

    query_region = f"{chrom}:{pos}-{pos}"

    try:
        queried_results = tb.querys(query_region)
    except Exception:
        # cache[key] = (ref, alt, db_rsid, beta, maf, 1)
        # return cache[key]
        cache[key] = (ref, alt, db_rsid, 1)
        out = (ref, alt, db_rsid, 1, beta, maf)
        return out

    for query in queried_results:
        db_ref = query[3]
        db_alt_alleles = set(query[4].split(','))
        rsid = query[2]

        if ref == db_ref and alt in db_alt_alleles:
            result = (ref, alt, rsid, 0, beta, maf)
            cache[key] = (ref, alt, rsid, 0, "no_flip")
            return result

        if ref in db_alt_alleles and alt == db_ref:
            result = (alt, ref, rsid, 0, str(-beta_f), 1.0 - maf_f)
            cache[key] = (alt, ref, rsid, 0, "flip")
            return result

    result = (ref, alt, db_rsid, 1, beta, maf)
    cache[key] = (ref, alt, db_rsid, 1)
    return result


def format_parquet():
    # total_snps = 0
    # skipped_snps = 0

    df = pd.read_parquet(
        args.input,
        engine='pyarrow',
        columns=['variant_id', 'phenotype_id', 'pval_nominal', 'slope', 'af']
    )

    with open(args.output, "w") as out:
        write = out.write

        for row in df.itertuples(index=False):
            # total_snps += 1

            chrom, pos, ref, alt = row.variant_id.split('_')[:4]
            chrom = chrom.replace('chr', '')

            gene = getattr(row, 'phenotype_id')

            ref, alt, rsid, skip, beta, maf,  = check_alleles_cached(
                chrom, pos, ref, alt,
                row.slope, row.af
            )

            if skip:
                # skipped_snps += 1
                continue

            write(
                f"{chrom}\t{pos}\t{ref}\t{alt}\t{rsid}\t{gene}\t"
                f"{row.pval_nominal}\t{beta}\t{maf}\t{args.sample_size}\n"
            )

    # print(f"Total SNPs processed: {total_snps}")
    # print(f"SNPs skipped: {skipped_snps}")


if __name__ == '__main__':
    format_parquet()