import os

rule all:
    input:
        expand("{base_dir}/{region}/eQTL_metabrain_{region}_chr{chrom}_tmp.txt", base_dir=config["base_dir"], region=config["regions"], chrom=config["chroms"])

rule format:
    params:
        basename=lambda wildcards: config[wildcards.region]["basename"],
        region="{region}",
        base_dir=config["base_dir"],
        chrom="{chrom}",
        dbsnp_dir=config["dbsnp_dir"]
    output:
        "{base_dir}/{region}/eQTL_metabrain_{region}_chr{chrom}_tmp.txt"
    shell:
        """
        python format.py --input {params.base_dir}/{params.region}/{params.basename}-chr{params.chrom}.txt.gz --output {output} --dbsnp_dir {params.dbsnp_dir} --chrom {params.chrom}
        """