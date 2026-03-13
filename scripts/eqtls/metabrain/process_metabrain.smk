import os

rule all:
    input:
        expand("{base_dir}/{region}/{region}_chr{chrom}_forliftover.txt", base_dir=config["base_dir"], region=config["regions"], chrom=config["chroms"]),
        expand("{base_dir}/{region}/{region}_chr{chrom}_tmp.txt", base_dir=config["base_dir"], region=config["regions"], chrom=config["chroms"])

rule obtain_sig_variant_gene_pairs:
    params:
        basename=lambda wildcards: config[wildcards.region]["basename"],
        region="{region}",
        base_dir=config["base_dir"],
        chrom="{chrom}"
    output:
        "{base_dir}/{region}/{region}_chr{chrom}_forliftover.txt"
    shell:
        """
        python obtain_sig_variant_gene_pairs.py --top_effect_fp {params.base_dir}/{params.region}/{params.basename}-TopEffects.txt.gz --full_sumstat {params.base_dir}/{params.region}/{params.basename}-chr{params.chrom}.txt.gz --outfile {output}
        """

rule liftover:
    input:
        "{base_dir}/{region}/{region}_chr{chrom}_forliftover.txt"
    output:
        "{base_dir}/{region}/{region}_chr{chrom}_tmp.txt"
    params:
        liftover_command = "/liftover/liftOver",
        liftover_chain = "/liftover/hg38ToHg19.over.chain.gz"
    shell:
        """
        {params.liftover_command} -bedPlus=3 {input} {params.liftover_chain} {output} unMapped
        """