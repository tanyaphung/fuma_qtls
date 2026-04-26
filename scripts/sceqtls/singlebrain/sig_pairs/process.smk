import os

rule all:
    input:
        expand("{base_dir}/{celltype}.chr{chrom}_forliftover.txt", base_dir=config["base_dir"], celltype=config["cell_types"], chrom=config["chroms"]),
        expand("{base_dir}/{celltype}.chr{chrom}_tmp.txt", base_dir=config["base_dir"], celltype=config["cell_types"], chrom=config["chroms"])

rule format:
    input:
        "{base_dir}/{celltype}_eqtl_top_assoc.tsv.gz" 
    params:
        chrom="{chrom}",
        dbsnp_dir=config["dbsnp_dir"]
    output:
        "{base_dir}/{celltype}.chr{chrom}_forliftover.txt"
    shell:
        """
        python format.py --input {input} --output {output} --dbsnp_dir {params.dbsnp_dir} --chrom {params.chrom}
        """

rule liftover:
    input:
        "{base_dir}/{celltype}.chr{chrom}_forliftover.txt"
    output:
        "{base_dir}/{celltype}.chr{chrom}_tmp.txt"
    params:
        liftover_command = "liftOver", #TODO: put in the correct path
        liftover_chain = "hg38ToHg19.over.chain.gz" #TODO: put in the correct path
    shell:
        """
        {params.liftover_command} -bedPlus=3 {input} {params.liftover_chain} {output} unMapped
        """