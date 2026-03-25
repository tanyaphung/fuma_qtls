import os

rule all:
    input:
        expand("{base_dir}/sceQTL_singlebrain_{cell_type}_chr{chrom}_tmp.txt", base_dir=config["base_dir"], cell_type=config["cell_types"], chrom=config["chroms"])

rule format:
    input:
        "{base_dir}/{cell_type}_eqtl_full_assoc.tsv.gz"
    output:
        "{base_dir}/sceQTL_singlebrain_{cell_type}_chr{chrom}_tmp.txt"
    params:
        basename="{cell_type}.{chrom}",
        chrom="{chrom}",
        dbsnp_dir=config["dbsnp_dir"]

    shell:
        """
        python format.py --input {input} --output {output} --dbsnp_dir {params.dbsnp_dir} --chrom {params.chrom}
        """