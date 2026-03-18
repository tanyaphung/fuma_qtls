import os

rule all:
    input:
        expand("{base_dir}/sceQTL_bryois2022Brain_{cell_type}_chr{chrom}_tmp.txt", base_dir=config["base_dir"], cell_type=config["cell_types"], chrom=config["chroms"])

rule format:
    input:
        "{base_dir}/{cell_type}.{chrom}.gz"
    output:
        "{base_dir}/sceQTL_bryois2022Brain_{cell_type}_chr{chrom}_tmp.txt"
    params:
        basename="{cell_type}.{chrom}",
        chrom="{chrom}",
        dbsnp_dir=config["dbsnp_dir"]

    shell:
        """
        python format_full_sumstat.py --input {input} --input_info {params.basename}.info.txt --output {output} --dbsnp_dir {params.dbsnp_dir} --chrom {params.chrom}
        """