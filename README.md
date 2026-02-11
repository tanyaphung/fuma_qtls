# Purpose: 
- This repository hosts scripts and readmes for processing of QTL datasets as part of the QTL Analysis module in FUMA and as part of Phung et al. 202x.

# eQTLs
## gtex_v10
- Data downloaded from Google cloud in January 2025 (link for download was accessed here: https://www.gtexportal.org/home/downloads/adult-gtex/qtl)
- The downloaded data is in `.parquet` format. Use script `scripts/eqtls/gtex_v10/format_parquet.py` which does the following: 
    - use pandas to read in the `.parquet` file and obtain these columns: `variant_id`, `gene_id`, `pval_nominal`, `slope`, `af`
        - assume that `variant_id` is in the chr:pos:ref:alt format
    - match the chr:pos:ref:alt based on dbSNP version 157 and get rsID. Rationale: 
        - if chr:pos:ref:alt matches with chr:pos:ref:alt from dbSNP, great. 
        - if chr:pos:ref:alt matches with chr:pos:alt:ref from dbSNP, swap the ref and alt in the eQLT file and assign beta to have the opposite sign (negative becomes positive and vice versa) and minor allele frequency becomes 1 - minor allele frequency
        - otherwise, the variant is skipped
- After running the script `scripts/eqtls/gtex_v10/format_parquet.py`, sort based on position, bgzip and tabix
- To run the whole pipeline, use a snakemake workflow in `scripts/eqtls/gtex_v10/process_gtexv10.smk`
    - config file: `scripts/eqtls/gtex_v10/config.json`. Note that the directories on lines 41 and 42 have been removed. 
        - For the `dbsnp_dir`, please refer to https://github.com/tanyaphung/commonly_used_codes/tree/master/genome_assembly_conversion for how to process dbSNP files
    - Example on how to run for a chromosome
    ```
    snakemake -s process_gtexv10.smk -j --configfile config.json --rerun-incomplete --config chromosome="1"
    ```
