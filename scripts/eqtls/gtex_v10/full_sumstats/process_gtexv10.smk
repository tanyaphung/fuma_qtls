import os

rule all:
    input:
        expand("{base_dir}/{type}/gtex_v10/GTEx_Analysis_v10_{type}_all_associations/{type}_gtex_v10_{region}.chr{chrom}.txt.gz.tbi", 
               base_dir=config["base_dir"], 
               region=config["regions"], 
               chrom=config["chromosome"], 
               type=config["types"])

rule format_parquet: 
    input:
        "{base_dir}/{type}/gtex_v10/GTEx_Analysis_v10_{type}_all_associations/{region}.v10.allpairs.chr{chrom}.parquet"
    output:
        "{base_dir}/{type}/gtex_v10/GTEx_Analysis_v10_{type}_all_associations/{type}_gtex_v10_{region}.chr{chrom}_tmp.txt"
    params:
        type=config["types"],
        dbsnp_dir=config["dbsnp_dir"],
        sample_size=lambda wildcards: config[wildcards.region]["sample_size"],
        chrom="{chrom}"
    shell:
        """
        python format_parquet.py -i {input} -o {output} --dbsnp_dir {params.dbsnp_dir} --sample_size {params.sample_size} --type {params.type} --chrom {params.chrom}
        """
        
rule sort: 
    input:
        "{base_dir}/{type}/gtex_v10/GTEx_Analysis_v10_{type}_all_associations/{type}_gtex_v10_{region}.chr{chrom}_tmp.txt"
    output:
        "{base_dir}/{type}/gtex_v10/GTEx_Analysis_v10_{type}_all_associations/{type}_gtex_v10_{region}.chr{chrom}.txt"
    shell:
        """
        sort -k 1n -k 2n {input} > {output}
        """

rule format_bgzip: 
    input:
        "{base_dir}/{type}/gtex_v10/GTEx_Analysis_v10_{type}_all_associations/{type}_gtex_v10_{region}.chr{chrom}.txt"
    output:
        "{base_dir}/{type}/gtex_v10/GTEx_Analysis_v10_{type}_all_associations/{type}_gtex_v10_{region}.chr{chrom}.txt.gz"
    shell:
        """
        bgzip {input}
        """

rule format_tabix: 
    input:
        "{base_dir}/{type}/gtex_v10/GTEx_Analysis_v10_{type}_all_associations/{type}_gtex_v10_{region}.chr{chrom}.txt.gz"
    output:
        "{base_dir}/{type}/gtex_v10/GTEx_Analysis_v10_{type}_all_associations/{type}_gtex_v10_{region}.chr{chrom}.txt.gz.tbi"
    shell:
        """
        tabix -p vcf {input}
        """

