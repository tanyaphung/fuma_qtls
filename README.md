# Purpose: 
- This repository hosts scripts and readmes for processing of QTL datasets as part of the QTL Analysis module in FUMA and as part of Phung et al. 202x.
- Document for: 
    - processing of full summary statistics for implementation of coloc/LAVA analysis in QTLs analysis
    - processing of significant variant-gene pairs for QTLs mapping

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

## metabrain
### significant variant-gene pairs for qtl mapping
- Fill out the form on https://www.metabrain.nl/cis-eqtls.html for getting access to download
- Understand the data structure
    - The file `*TopEffects.txt.gz` has the column PvalueNominalThreshold for each gene. Use this for filtering.

    ```
    zless 2021-07-23-basalganglia-EUR-30PCs-TopEffects.txt.gz | grep ENSG00000130538.5 | awk '{print$12"\t"$26"\t"$27}'
    0.0181322749462725      0.000183932     0.524521572829835
    ```
    - So this means that the top snps for this gene has p value 0.0181322749462725
    ```
    zless 2021-07-23-basalganglia-EUR-30PCs-chr22.txt.gz | grep ENSG00000130538.5 | awk '{print$12}' | sort | head
    0.01813227494627249
    0.024551509867757382
    0.02530276602259235
    0.026172886246108203
    0.02680128567007011
    0.02719315015385728
    0.027287265632118862
    0.027787685454157954
    0.03331884864620144
    0.03456411981875567
    ```
- Processing steps: 
    - snakemake script: `scripts/eqtls/metabrain/process_metabrain.smk`
    - check script `scripts/eqtls/metabrain/run_process_metabrain.sh` for how to run the snakemake script and follow-up steps