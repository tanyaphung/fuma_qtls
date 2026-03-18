import os

rule all:
    input:
        expand("{base_dir}/sceQTL_jerber2021Dopaminergic_{cell_type}_chr{chrom}_grch37.txt", base_dir=config["base_dir"], cell_type=config["cell_types"], chrom=config["chroms"]),
        expand("{base_dir}/sceQTL_jerber2021Dopaminergic_{cell_type}_chr{chrom}_grch38.txt", base_dir=config["base_dir"], cell_type=config["cell_types"], chrom=config["chroms"]),
        expand("{base_dir}/sceQTL_jerber2021Dopaminergic_{cell_type}_chr{chrom}_tmp.txt", base_dir=config["base_dir"], cell_type=config["cell_types"], chrom=config["chroms"])

rule prepare_for_liftover:
    input:
        "{base_dir}/{cell_type}.qtl_results_all.sorted.txt.gz"
    output:
        "{base_dir}/sceQTL_jerber2021Dopaminergic_{cell_type}_chr{chrom}_grch37.txt"
    params:
        chrom = "{chrom}"
    shell:
        """
        python prepare_for_liftover.py --input {input} --output {output} --chrom {params.chrom}
        """

rule liftover:
    input:
        "{base_dir}/sceQTL_jerber2021Dopaminergic_{cell_type}_chr{chrom}_grch37.txt"
    output:
        "{base_dir}/sceQTL_jerber2021Dopaminergic_{cell_type}_chr{chrom}_grch38.txt"
    params:
        liftover_command = "liftOver",
        liftover_chain = "hg19ToHg38.over.chain.gz"
    shell:
        """
        {params.liftover_command} -bedPlus=3 {input} {params.liftover_chain} {output} unMapped
        """

rule format:
    input:
        "{base_dir}/sceQTL_jerber2021Dopaminergic_{cell_type}_chr{chrom}_grch38.txt"
    output:
        "{base_dir}/sceQTL_jerber2021Dopaminergic_{cell_type}_chr{chrom}_tmp.txt"
    params:
        chrom="{chrom}",
        dbsnp_dir=config["dbsnp_dir"]

    shell:
        """
        python format.py --input {input} --output {output} --dbsnp_dir {params.dbsnp_dir} --chrom {params.chrom}
        """