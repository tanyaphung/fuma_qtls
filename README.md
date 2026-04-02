# Purpose: 
- This repository hosts scripts and readmes for processing of QTL datasets for FUMA
- Document for: 
    - processing of full summary statistics for implementation of coloc/LAVA analysis in the module QTLs analysis
    - processing of significant variant-gene pairs for QTLs mapping

- For the full summary statistics, note the following: 
    - The processed data contains the following columns in this particular order: 
        - chr
        - pos (in GRCh38)
        - ref
        - alt
        - rsID
        - gene/protein
        - pval
        - beta
        - maf
        - N
    - Each chromosome is a separate file
- For the significant variant-gene pairs for QTLs mapping, note the following: 
    - The data contains the following columns in this order: 
        - chr
        - pos (in GRCh37)
        - ref
        - alt
        - rsID
        - gene symbol 
        - cis/trans
        - beta
        - pval 
    - In datasets where the authors provided the significant variant-gene pairs, those are used. Otherwise, in the case that the authors provided the full sumstat and without instructions for additional filtering to obtain the significant variant-gene pairs, only the variant-gene pairs with nominal p value < 0.05 are kept. For these datasets, it is only possible to run them with a p threshold specified by the users (default is less than 1e-3). 

**NOTE THAT THIS REPO IS STILL IN DEVELOPMENT**

# eQTLs
## gtex_v10
### full_sumstats
- Data downloaded from Google cloud in January 2025 (link for download was accessed here: https://www.gtexportal.org/home/downloads/adult-gtex/qtl)
- The downloaded data is in `.parquet` format. Use script `scripts/eqtls/gtex_v10/full_sumstats/format_parquet.py` which does the following: 
    - use pandas to read in the `.parquet` file and obtain these columns: `variant_id`, `gene_id`, `pval_nominal`, `slope`, `af`
        - assume that `variant_id` is in the chr:pos:ref:alt format
    - match the chr:pos:ref:alt based on dbSNP version 157 and get rsID. Rationale: 
        - if chr:pos:ref:alt matches with chr:pos:ref:alt from dbSNP, great. 
        - if chr:pos:ref:alt matches with chr:pos:alt:ref from dbSNP, swap the ref and alt in the eQLT file and assign beta to have the opposite sign (negative becomes positive and vice versa) and minor allele frequency becomes 1 - minor allele frequency
        - otherwise, the variant is skipped
- After running the script `scripts/eqtls/gtex_v10/full_sumstats/format_parquet.py`, sort based on position, bgzip and tabix
- To run the whole pipeline, use a snakemake workflow in `scripts/eqtls/gtex_v10/full_sumstats/process_gtexv10.smk`
    - config file: `scripts/eqtls/gtex_v10/full_sumstats/config.json`. Note that the directories on lines 41 and 42 have been removed. 
        - For the `dbsnp_dir`, please refer to https://github.com/tanyaphung/commonly_used_codes/tree/master/genome_assembly_conversion for how to process dbSNP files
    - Example on how to run for a chromosome
    ```
    snakemake -s process_gtexv10.smk -j --configfile config.json --rerun-incomplete --config chromosome="1"
    ```

### sig_pairs
- Downloaded the file `GTEx_Analysis_v10_eQTL.tar` from https://www.gtexportal.org/home/downloads/adult-gtex/qtl, then untar
    - There are 50 files ending in `*signif_pairs.parquet`, one file for each tissue
- Verify that this file contains only the significant variant-gene pair association
    - The p threshold is in the 30th column in the file `*eGenes.txt.gz`
    ```
    zless Heart_Left_Ventricle.v10.eGenes.txt.gz | head -n1 | awk '{print$30}'
    pval_nominal_threshold
    ```
    - Find the p threshold for the gene ENSG00000227232.5
    ```
    zless Heart_Left_Ventricle.v10.eGenes.txt.gz | grep ENSG00000227232.5 | awk '{print$30}'
    0.000285255
    ```
    - Now, extract the variant-gene pair associations from the file `*signif_pairs.parquet`
    ```
    import pandas as pd
    data = pd.read_parquet("Heart_Left_Ventricle.v10.eQTLs.signif_pairs.parquet", engine='pyarrow', columns=['variant_id', 'gene_id', 'pval_nominal', 'slope', 'af'])
    test = data[data["gene_id"]=="ENSG00000227232.5"]
    test["pval_nominal"]<0.000285255
    0     True
    1     True
    2     True
    3     True
    4     True
    5     True
    6     True
    7     True
    8     True
    9     True
    10    True
    11    True
    12    True
    13    True
    14    True
    15    True
    16    True
    17    True
    ```


## metabrain
- Fill out the form on https://www.metabrain.nl/cis-eqtls.html for getting access to download

### sig_pairs

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
    - snakemake script: `scripts/eqtls/metabrain/sig_pairs/process_metabrain.smk`
    - check script `scripts/eqtls/metabrain/sig_pairs/run_process_metabrain.sh` for how to run the snakemake script and follow-up steps

### full_sumstats
- Processing steps: 
    - snakemake script: `scripts/eqtls/metabrain/full_sumstats/process_metabrain.smk`
    - check script `scripts/eqtls/metabrain/full_sumstats/run_process_metabrain.sh` for how to run the snakemake script and follow-up steps

# sceQTLs (single-cell eQTLs)

## bryois2022Brain
- Download data from: https://zenodo.org/records/7276971
- Data overview: 
    - Columns: (1) Gene_id, (2) SNP_id, (3) Distance to TSS, (4) Nominal p-value, (5) Beta
    ```
    zless Astrocytes.22.gz | head
    IL17RA_ENSG00000177663 rs112435201 -716044 0.607765 0.057825
    IL17RA_ENSG00000177663 rs7287956 -715646 0.576995 0.0671856
    IL17RA_ENSG00000177663 rs5748209 -715180 0.525675 0.074597
    IL17RA_ENSG00000177663 rs5746874 -714392 0.425798 0.0935307
    IL17RA_ENSG00000177663 rs5748581 -714261 0.473547 0.0857912
    IL17RA_ENSG00000177663 rs9605127 -714156 0.554399 0.0964225
    IL17RA_ENSG00000177663 rs5748583 -714128 0.889617 -0.012636
    IL17RA_ENSG00000177663 rs5748589 -713977 0.437265 0.0913829
    IL17RA_ENSG00000177663 rs5748596 -713944 0.430008 0.0925751
    IL17RA_ENSG00000177663 rs78025685 -713718 0.464524 0.0857131
    ```

    - 
    ```
    zless snp_pos.txt.gz | head
    SNP     SNP_id_hg38     SNP_id_hg19     effect_allele   other_allele    MAF
    rs8179466       chr1:264562     chr1:234313     T       C       0.09635
    rs6680723       chr1:598812     chr1:534192     T       C       0.2552
    rs12025928      chr1:611317     chr1:546697     A       G       0.08947
    rs12238997      chr1:758351     chr1:693731     G       A       0.1302
    rs72631875      chr1:770502     chr1:705882     A       G       0.07552
    rs12029736      chr1:770988     chr1:706368     A       G       0.487
    rs116030099     chr1:787290     chr1:722670     C       T       0.09115
    rs116587930     chr1:792461     chr1:727841     A       G       0.0625
    rs4951859       chr1:794299     chr1:729679     C       G       0.1589
    ```

    - For the sample size, I will be using the total N_samples (postQC) from Table S1 of the article which is equal to 373.

- Processing overview: 
    - Preprocessing the file `snp_pos.txt.gz` for each chromosome
    - Merge files `Astrocytes.22.gz` and `snp_pos_22.txt`

- Preprocessing the file `snp_pos.txt.gz`
```
for i in {1..22}
do
python format_snp_pos.py ${i}
done
```

### full_sumstats
- snakemake script: `scripts/sceqtls/bryois2022Brain/full_sumstats/format_full_sumstat.smk`
- check script `scripts/sceqtls/bryois2022Brain/full_sumstats/run.sh` for how to run the snakemake script and follow-up steps

### sig_pairs
- snakemake script: `scripts/sceqtls/bryois2022Brain/sig_pairs/process.smk`
- check script `scripts/sceqtls/bryois2022Brain/sig_pairs/run.sh` for how to run the snakemake script and follow-up steps
- rename `OPCs...COPs` to `OPCs`

## jerber2021Dopaminergic
- Download data (eqtl_summary_stats.tar.gz) from: https://zenodo.org/records/4333872
- Viewing one of the files:
```
feature_id      snp_id  p_value beta    beta_se empirical_feature_p_value       feature_chromosome      feature_start      feature_end     n_samples       n_e_samples     snp_chromosome  snp_position    assessed_allele    call_rate       maf     hwe_p
ENSG00000225880 1_662622_G_A    1.7083567865864062e-07  0.5211826808015152      0.0996799714446961      -1.0       1       761586  762902  173     173     1       662622  A       1.0     0.08092485549132948     1.0
ENSG00000187961 1_662622_G_A    0.05892174837573025     -0.16135667326680556    0.08542919251703184     -1.0       1       895967  901095  173     173     1       662622  A       1.0     0.08092485549132948     1.0
```
- Overview of processing steps: 
    - Extract only relevant columns and prepare file for liftover
    - Liftover from GRCh37 to GRCh38
    - Format (get rsID, etc...)
- snakemake script: `scripts/sceqtls/jerber2021Dopaminergic/full_sumstats/process.smk`
- check script `scripts/sceqtls/jerber2021Dopaminergic/full_sumstats/run.sh` for how to run the snakemake script and follow-up steps

## singlebrain
- Download the data from: https://zenodo.org/records/14908182
- The file does not have MAF. coloc can be implemented with beta and se (or slope and se) and sdY (and not MAF), but will need to modify the code a bit. Source: https://github.com/chr1swallace/coloc/issues/178
    - Because the implementation of coloc without MAF requires some code change on the functionalities, this will be saved for FUMA releave version 2.0.x. 
    - For intiial release of FUMA version 2.0.0, singlebrain datasets can only be run with LAVA. 

### full_sumstats
- Overview of the data: 
    - coordinates in GRCh38

- snakemake script: `scripts/sceqtls/singlebrain/full_sumstats/format.smk`
- check script `scripts/sceqtls/singlebrain/full_sumstats/run.sh` for how to run the snakemake script and follow-up steps

### sig_pairs