import os

rule all:
    input:
        expand("{base_dir}/sig_pairs/sceQTL_bryois2022Brain_{cell_type}.chr{chrom}_forliftover.txt", base_dir=config["base_dir"], cell_type=config["cell_types"], chrom=config["chroms"]),
        expand("{base_dir}/sig_pairs/sceQTL_bryois2022Brain_{cell_type}.chr{chrom}_tmp.txt", base_dir=config["base_dir"], cell_type=config["cell_types"], chrom=config["chroms"])

rule get_sig_pairs:
    input:
        "{base_dir}/sceQTL_bryois2022Brain_{cell_type}_chr{chrom}.txt.gz" 
    params:
        chrom="{chrom}"
    output:
        "{base_dir}/sig_pairs/sceQTL_bryois2022Brain_{cell_type}.chr{chrom}_forliftover.txt"
    shell:
        """
        python get_sig_pairs.py --input {input} --output {output} --chrom {params.chrom}
        """

rule liftover:
    input:
        "{base_dir}/sig_pairs/sceQTL_bryois2022Brain_{cell_type}.chr{chrom}_forliftover.txt"
    output:
        "{base_dir}/sig_pairs/sceQTL_bryois2022Brain_{cell_type}.chr{chrom}_tmp.txt"
    params:
        liftover_command = "liftOver", #TODO: put in the correct path
        liftover_chain = "hg38ToHg19.over.chain.gz" #TODO: put in the correct path
    shell:
        """
        {params.liftover_command} -bedPlus=3 {input} {params.liftover_chain} {output} unMapped
        """