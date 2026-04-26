import os

rule all:
    input:
        expand("{base_dir}/sig_pairs/{tissue}.chr{chrom}_forliftover.txt", base_dir=config["base_dir"], tissue=config["tissues"], chrom=config["chrom"]),
        expand("{base_dir}/sig_pairs/{tissue}.chr{chrom}_tmp.txt", base_dir=config["base_dir"], tissue=config["tissues"], chrom=config["chrom"])

rule format_parquet:
    input:
        "{base_dir}/GTEx_Analysis_v10_sQTL_updated/{tissue}.v10.sQTLs.signif_pairs.parquet" 
    params:
        chrom="{chrom}",
        dbsnp_dir=config["dbsnp_dir"]
    output:
        "{base_dir}/sig_pairs/{tissue}.chr{chrom}_forliftover.txt"
    shell:
        """
        python format_parquet.py --input {input} --output {output} --dbsnp_dir {params.dbsnp_dir} --chrom {params.chrom} --type sQTL
        """

rule liftover:
    input:
        "{base_dir}/sig_pairs/{tissue}.chr{chrom}_forliftover.txt"
    output:
        "{base_dir}/sig_pairs/{tissue}.chr{chrom}_tmp.txt"
    params:
        liftover_command = "liftOver", #TODO: put in the correct path
        liftover_chain = "" #TODO: put in the correct path
    shell:
        """
        {params.liftover_command} -bedPlus=3 {input} {params.liftover_chain} {output} unMapped
        """