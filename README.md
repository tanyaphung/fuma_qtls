# Purpose: 
- This repository hosts scripts and readmes for processing of QTL datasets for FUMA
    - Note that for all of the scripts are shared here, any paths that are hard-coded have been removed. As a result, you may not be able to replicate all of the scripts right out of the box. Rather, you need to update some of the paths. I have added the key words "#TODO" to denote where correct paths should be added. 
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
- Python script to format the parquet file: `scripts/eqtls/gtex_v10/sig_pairs/format_parquet.py`
- Snakemake script: `scripts/eqtls/gtex_v10/sig_pairs/process.smk`
- How to batch run: `scripts/eqtls/gtex_v10/sig_pairs/run.sh`


## metabrain
- Fill out the form on https://www.metabrain.nl/cis-eqtls.html for getting access to download

### full_sumstats
- Processing steps: 
    - snakemake script: `scripts/eqtls/metabrain/full_sumstats/process_metabrain.smk`
    - check script `scripts/eqtls/metabrain/full_sumstats/run_process_metabrain.sh` for how to run the snakemake script and follow-up steps

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
### full_sumstats
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

### sig_pairs
- In supplementary table 7 that can be downloaded from https://www.nature.com/articles/s41588-021-00801-6#Sec31, this file does contain significant snp-gene pair but it does not separate out by cell types.
- As a results, for this dataset, I will employ a similar strategy to bryois2022Brain datasets, which is to only keep snp-gene pair where nominal p < 0.05 
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
- Use the files ending in `eqtl_top_assoc.tsv.gz`
- Coordinates in GRCh38 so liftover to GRCh37 is needed
- snakemake script: `scripts/sceqtls/singlebrain/sig_pairs/process.smk`
- check script `scripts/sceqtls/singlebrain/sig_pairs/run.sh` for how to run the snakemake script and follow-up steps

# sQTLs (splice QLTs)
## gtex_v10
### full_sumstats
- snakemake script: `scripts/sqtls/full_sumstats/process_gtexv10.smk`
- check script `scripts/sqtls/full_sumstats/run_process_gtexv10.sh` for how to run the snakemake script and follow-up steps

### sig_pairs
- Downloaded the file `GTEx_Analysis_v10_sQTL.tar` from https://www.gtexportal.org/home/downloads/adult-gtex/qtl, then untar
    - There are 50 files ending in `*signif_pairs.parquet`, one file for each tissue
- snakemake script: `scripts/sqtls/sig_pairs/process.smk`
- check script `scripts/sqtls/sig_pairs/run.sh` for how to run the snakemake script and follow-up steps

# pQTLs

## 1_suhre_2017
- platform: 
    - KORA: SOMAscan
- tissue: plasma
- population: 
    - KORA: European (German)
- n_participants: 
    - KORA: 1000 blood samples
- n_pQTLs: 
    - 539 pQTLs
        - 284 unique proteins
        - 451 independent SNPs
        - P < 8.72e-11
- study: 
    - KORA F4 study
        - a population-based cohort of 3,080 subjects living in Southern Germany

### sig_pairs
- sheet: `Supplemental Data 1`
- additional notes: 
	- build: GRCh37
    - rs4525: 1-169511734-T-C. Verified on gnomad: https://gnomad.broadinstitute.org/variant/1-169511734-T-C?dataset=gnomad_r2_1
        -  This is a missense variant of the gene F5
        - In spreadsheet `Supplemental Data 1`, column F indicates CAMPK1 and is a trans pQTLs. Therefore, I think that column F is the protein column of the association
    - rs505922: 9-136149229-G-C. Verified on gnomad: https://gnomad.broadinstitute.org/variant/9-136149229-T-C?dataset=gnomad_r2_1
        - This is an intron variant of the gene ABO
        - In spreadsheet `Supplemental Data 1`, column F indicates CD209 and is a trans pQTLs. 

```
python extract_cols.py 
The number of variants: 539
The number of variants after spliting by |: 565
<bound method NDFrame.head of      chr        pos a1 a2  variant_id   protein   type    beta              P
0     19   10395683  A  G      rs5498     ICAM1    CIS -1.2170  5.595407e-276
1     19   10395683  A  G      rs5498     ICAM5    CIS  0.5107   1.815787e-24
2      1  154426264  C  T   rs4129267      IL6R    CIS  1.2080  1.209856e-294
3      2     272203  C  T  rs11553746      ACP1    CIS  1.2370  2.029567e-280
4      3   49701983  G  A   rs9858542      MST1    CIS -1.2990   0.000000e+00
..   ...        ... .. ..         ...       ...    ...     ...            ...
560    9  120327400  C  T   rs1159787      TLR4    CIS -0.3492   1.535361e-07
561    9  120327400  C  T   rs1159787      LY96    CIS -0.3492   1.535361e-07
562   17   34163565  G  A   rs4239252      CCL5    CIS -0.3458   7.750004e-10
563    6   42861581  A  C   rs9462846      MED1  TRANS  0.3261   5.574167e-01
564   14   95007744  T  C  rs10135681  SERPINA4    CIS  0.2771   8.090823e-11

[565 rows x 9 columns]>
```

```
sort -k 1n -k 2n 1_suhre_2017_fmt.txt > 1_suhre_2017_fmt_sort.txt
cat ../header.txt 1_suhre_2017_fmt_sort.txt > 1_suhre_2017.txt
bgzip <1_suhre_2017.txt >1_suhre_2017.txt.gz
tabix -p vcf 1_suhre_2017.txt.gz
```

## 2_sun_2016
- meta-analysis from 2 large cohorts of current and former smokers with and without COPD
- platform: custom 13-panel multiplex assays
    - 114 candidate blood biomarkers
- tissue: 
    - SPIROMICS cohort: EDTA plasma and serum
    - COPDGene cohort: plasma
- population: unclear (American?)
- n_participants:  
    - SPIROMICS cohort: 750
    - COPDGene cohort: 590
- n_pQTLs: 
    - SPIROMICS cohort: 290 pQTLs
    - COPDGene cohort: 182 pQTLs
    - meta-analysis: 527 pQTLs
- study: 
    - SPIROMICS cohort
    - COPDGene cohort

### sig_pairs
- sheet: `S4 Table`
- additional notes: 
	- build: GRCh37
    - No information on alleles
    - added a column to denote cis/trans based on whether the rows are highlighted yellow
        - for the snp rs633862 that is highlighted in red, I denote this one as trans
    - For the meta-analyses, there were no column for the combined beta

```
python extract_cols.py 
The number of variants: 527
<bound method NDFrame.head of      chr        pos  a1  a2  variant_id protein   type  beta             P
0      6   32151443 NaN NaN   rs2070600    AGER    cis   NaN  2.940000e-22
1      6   31864674 NaN NaN   rs2844456    AGER    cis   NaN  4.440000e-16
2      6   32156489 NaN NaN   rs2022059    AGER    cis   NaN  1.110000e-15
3      6   32157364 NaN NaN   rs2856437    AGER    cis   NaN  1.330000e-15
4      6   32020961 NaN NaN  rs34562262    AGER    cis   NaN  2.220000e-15
..   ...        ...  ..  ..         ...     ...    ...   ...           ...
522    9  136131188 NaN NaN   rs8176749     VWF  trans   NaN  9.290000e-12
523    9  136131322 NaN NaN   rs8176746     VWF  trans   NaN  9.670000e-12
524    9  136128546 NaN NaN   rs7857390     VWF  trans   NaN  1.410000e-11
525    9  136323754 NaN NaN   rs4962153     VWF  trans   NaN  9.630000e-11
526    9  136184526 NaN NaN  rs11244079     VWF  trans   NaN  4.590000e-10

[527 rows x 9 columns]>
```

```
sort -k 1n -k 2n 2_sun_2016_meta_fmt.txt >2_sun_2016_meta_fmt_sort.txt
cat ../header.txt 2_sun_2016_meta_fmt_sort.txt >2_sun_2016_meta.txt
bgzip <2_sun_2016_meta.txt >2_sun_2016_meta.txt.gz
tabix -p vcf 2_sun_2016_meta.txt.gz
```

## 3_gudjonsson_2022
- platform: SOMAmer
    - 4135 human proteins targeted by 4782 SOMAmers
- tissue: serum
- population: European (Icelandic)
- n_participants: 5,368 individuals 
- n_pQTLs: 
    - 269,637 variants exhibited study-wide significant associations (P<1.046e-11)
    - 4,035 independent associations between genetic variants and 2,091 serum proteins
- study: AGES-Reykjavik cohort of elderly Icelanders

### sig_pairs
- sheet: `Supplementary Data 3`
- additional notes: 
	- build: GRCh37
        - rs144926861 1:5218635 EA is A. Verified on gnomad: https://gnomad.broadinstitute.org/variant/1-5218635-G-A?dataset=gnomad_r2_1
        - Note that the EA is not consistent with what is reported on gnomad. For example: 
            - rs6682671 1:17311882 EA is C. On gnomad: https://gnomad.broadinstitute.org/variant/1-17311882-C-T?dataset=gnomad_r2_1 C is the ref allele. 
    - beta and P are from the single variant model

```
python extract_cols.py 
The number of variants: 4290
<bound method NDFrame.head of       chr        pos  a1 a2   variant_id  protein   type      beta             P
0       1     945111 NaN  C   rs13303172    ISG15    cis -0.707278  3.469370e-20
1       1     995481 NaN  T    rs9442393    ISG15    cis  0.165803  1.912160e-18
2       1    1144653 NaN  A   rs78021605  B3GALT6    cis -0.243576  8.161640e-16
3       1    1462479 NaN  T   rs41285834     VWA1    cis -1.170260  2.419030e-68
4       1    1776269 NaN  A    rs4648727     NADK    cis -0.159103  1.129580e-17
...   ...        ...  .. ..          ...      ...    ...       ...           ...
4285   23  128884155 NaN  A   rs12690359     SOD2  trans  0.061222  1.081410e-03
4286   23  135741443 NaN  A  rs148594123   CD40LG    cis -0.688280  3.900080e-23
4287   23  140493131 NaN  A   rs56376703     MNX1  trans  0.116563  6.226940e-12
4288   23  142716114 NaN  G    rs5907446  SLITRK4    cis  0.129343  2.871290e-18
4289   23  150017550 NaN  C    rs4240082  SCGB3A1  trans -0.133064  4.142750e-17

[4290 rows x 9 columns]>
```

```
sort -k 1n -k 2n 3_gudjonsson_2022_fmt.txt > 3_gudjonsson_2022_fmt_sort.txt
cat ../header.txt 3_gudjonsson_2022_fmt_sort.txt > 3_gudjonsson_2022.txt
bgzip <3_gudjonsson_2022.txt >3_gudjonsson_2022.txt.gz
tabix -p vcf 3_gudjonsson_2022.txt.gz
```

## 4_sun_2018
- platform: aptamer-based multiplex protein assay (SOMAscan)
- tissue: plasma
- population: European
- n_participants: 3,301 individuals
- n_pQTLs: 1,927 pQTLs (P<1.5e-11)
    - 549 cis-pQTLs
    - cis-pQTLs definition: variant within 1Mb of the gene encoding the protein
    - trans-pQTLs definition: variant >1Mb from the gene envoding the protein
- study: INTERVAL

### sig_pairs
- sheet: `ST4 - pQTL summary`
    - a1: `Other Allele (OA)`
    - a2: `Effect Allele (EA)`
- additional notes:
    - build: GRCh37
        - rs1891906 1:950243 with EA C and OA A. Verified on gnomad https://gnomad.broadinstitute.org/variant/1-950243-A-C?dataset=gnomad_r2_1 that the position is in GRCh37 build and OA is the reference allele and EA is the alternate allele
        - rs618184 1:57394731 with EA G and OA A. Verified on gnomad https://gnomad.broadinstitute.org/variant/1-57394731-A-G?dataset=gnomad_r2_1 
    - Column P `Mapped gene` is the gene where the variant is mapped (or closest) to. For example: 
        - rs9439082 is an intron of gene GJA9. Since it is annotated that this is a trans pQTL, GJA9 is not the protein that this variant is having an effect on. 
        - rs11390840 is an intron of gene CFH. Since it is annotated that this is a trans pQTL, CFH is not the protein that this variant is having an effect on. 
    - To get the gene name of the protein, extract from the SOMAmerID

```
python extract_cols.py 
            somamer_id  variant_id  chr       pos a2 a1 type    beta              P
0      ISG15.14151.4.3   rs1891906    1    950243  C  A  cis  0.2592   1.400000e-24
1        CA6.3352.80.3   rs3765963    1   9034598  G  A  cis  0.6766  4.100000e-185
2       H6PD.7161.25.3  rs34603401    1   9305445  C  A  cis  0.7589  1.000000e-126
3       NPPB.7655.11.3    rs198389    1  11919271  G  A  cis  0.2934   3.500000e-31
4  TNFRSF1B.8368.102.3   rs5746017    1  12251341  C  A  cis -0.4752   3.000000e-15
   chr       pos a1 a2  variant_id   protein type    beta              P
0    1    950243  A  C   rs1891906     ISG15  cis  0.2592   1.400000e-24
1    1   9034598  A  G   rs3765963       CA6  cis  0.6766  4.100000e-185
2    1   9305445  A  C  rs34603401      H6PD  cis  0.7589  1.000000e-126
3    1  11919271  A  G    rs198389      NPPB  cis  0.2934   3.500000e-31
4    1  12251341  A  C   rs5746017  TNFRSF1B  cis -0.4752   3.000000e-15
```

```
tail 4_sun_2018_supp_fmt.txt
22      29476769        A       G       rs77320622      KREMEN1 cis     -0.9951 2.8e-12
22      31012756        T       C       rs4820885       TCN2    cis     -0.7247 3.9e-256
22      32872593        G       A       rs5754109       RRM1    trans   -0.4764 1.3e-75
22      33159919        GCC     G       rs59896920      MMRN2   trans   -0.1897 2.8e-12
22      36638705        C       T       rs71314970      APOL1   cis     -0.3659 3.5e-19
22      36661152        G       A       rs28480494      CISD1   trans   -0.3113 1.7e-23
22      37329448        G       A       rs1534881       CSF2RB  cis     -0.3158 2.6e-38
22      37462936        A       G       rs855791        TFRC    trans   -0.2019 1.9e-16
22      37961353        C       T       rs5756729       LGALS2  cis     -0.275  2.2e-26
22      50727792        T       C       rs28573806      PLXNB2  cis     0.5315  3.5e-116
```

```
sort -k 1n -k 2n 4_sun_2018_supp_fmt.txt > 4_sun_2018_supp_fmt_sort.txt
cat ../header.txt 4_sun_2018_supp_fmt_sort.txt > 4_sun_2018.txt
bgzip <4_sun_2018.txt >4_sun_2018.txt.gz
tabix -p vcf 4_sun_2018.txt.gz
```

## 5_emilsson_2022
- platform: SOMApanel
- tissue: serum
- population: European
- n_participants: 5,343 individuals
- n_pQTLs: 
    - 10.200 exome array variants affecting 2780 human proteins
    - P < 1e-6
- study: AGES-RS 
    - AGES Reykjavik cohort
    - Iceland

### sig_pairs
- sheet: `Supplementary Data 2`
    - gene column: `Protein target`
    - a1: `Allele 2`
    - a2: `Allele 1`
- additional notes: 
    - build: GRCh37
        - rs204896 6:32064098 with Allele 1 T and Allele 2 C. Verified on gnomad https://gnomad.broadinstitute.org/variant/6-32064098-C-T?dataset=gnomad_r2_1 that the position is in GRCh37 and Allele 2 is the reference allele and Allele 1 is the alternate allele
        - rs8176720 9:31613081 with Allele 1 C and Allele 2 T. Verified on gnomad https://gnomad.broadinstitute.org/variant/9-136132873-T-C?dataset=gnomad_r2_1 that the position is incorrect
        - rs7853989 9:31612607. Verified on gnomad https://gnomad.broadinstitute.org/variant/9-136131592-G-C?dataset=gnomad_r2_1 that the position is incorrect
        - rs72559704 10:106014706 with Allele 1 A and Allele 2 G. Verified on gnomad https://gnomad.broadinstitute.org/variant/10-106014706-G-A?dataset=gnomad_r2_1 that the position is in GRCh37 and Allele 2 is the reference allele and Allele 1 is the alternate allele. 
        - **IMPORTANT**: It looks like for some of the variants, the position recorded in the supplementary tables seem to be incorrect. In the future could re-match using rsID. 
- Special note: the list of pQTLs is in Supplement Data 2 but this sheet does not contain cis/trans information. To get the cis/trans information from Supplement Data 1, I had to merge but some of the variants in Supplement Data 2 do not have a record in Supplement Data 1 because of typos, etc... so I just did the merge. 

```
python extract_cols.py 
---Processing supplementary data 1 no conditional---
(37562, 9)
   chr        pos a1 a2   variant_id protein   type    beta             P
0    1   57422484  T  C    rs1013579  SEPT10  Trans -0.8723  2.019000e-35
1    1   57422511  C  T   rs12067507  SEPT10  Trans  0.5878  1.047000e-40
2    1   57415310  G  A   rs12085435  SEPT10  Trans  0.5878  1.047000e-40
3    1  196646176  C  A    rs1329424  SEPT10  Trans  0.1174  5.004000e-10
4    1   57409459  C  A  rs139498867  SEPT10  Trans  0.3997  1.008000e-07
---Processing supplementary data 1 conditional---
(37562, 7)
(9991, 8)
(9531, 9)
   chr       pos a1 a2   variant_id protein   type      beta             P
0    1  57415310  G  A   rs12085435  SEPT10  Trans  0.596005  4.980850e-41
1    1  57422484  T  C    rs1013579  SEPT10  Trans -0.889436  4.228520e-36
2    1  57340727  C  A     rs652785  SEPT10  Trans  0.219452  1.196000e-30
3   17  26694861  A  G        rs704  SEPT10  Trans -0.163200  9.891330e-20
4    1  57373737  G  A  rs143908758  SEPT10  Trans  0.798042  4.961540e-11
```

```
for i in noConditional conditional; do
> sort -k 1n -k 2n 5_emilsson_2022_${i}_fmt.txt > 5_emilsson_2022_${i}_fmt_sort.txt
> cat ../header.txt 5_emilsson_2022_${i}_fmt_sort.txt > 5_emilsson_2022_${i}.txt
> bgzip <5_emilsson_2022_${i}.txt >5_emilsson_2022_${i}.txt.gz
> tabix -p vcf 5_emilsson_2022_${i}.txt.gz
> done;
```

## 6_katz_2021
- platform: SomaScan (aptamer-based proteomics)
- tissue: plasma
- population: African
- n_participants: 1852 adults in the discovery cohort
- n_pQTLs: 
    - 569 genetic associations between 479 proteins and 438 unique genetic regions
    - p<3.8e-11
- study: 
    - Jackson Heart Study (discovery cohort)
    - MESA & HERITAGE

### sig_pairs
- sheet:
    - `S3 - pQTLs`
    - `S5-meta-analysis`
- additional notes: 
    - build: GRCh37
        - rs4615788 chr1:948870 with A1 G and A2 C. Verified on gnomad https://gnomad.broadinstitute.org/variant/1-948870-C-G?dataset=gnomad_r2_1 to confirm that the position is in GRCh37 and A2 is the reference allele and A1 is the alternate allele
        - rs73817633 chr3:384691 with A1 T and A2 C. Verified on gnomad https://gnomad.broadinstitute.org/variant/3-384691-C-T?dataset=gnomad_r2_1 to confirm that the position is in GRCh37 and A2 is the reference allele and A1 is the alternate allele
    - The columns U (`Within gene`) and V (`Nearest gene`) denote the gene where the variant falls or is nearby. For example: 
        - rs58800854 is a missense variant in gene CA6. 
        - rs72882747 is an intron variant of gene FCN3 but is a trans pQTL to protein MASP3. 
        - To get the protein, extract from the column A SomamerID
- **Conclusion:** 
    - Because there are 2 related files in the supplementary materials, I will generate 2 datasets for this study
        - `6_katz_2021_discovery`
        - `6_katz_2021_meta`
    - Use `Nearest gene` as the gene
    - There is also a sheet called `S4-Additional cis pQTLs p<5e-6`. However, I am not processing this sheet because it is not clear to me which build the coordinates are in. 

```
python extract_cols.py 
---Processing for 2_katz_2022_discovery---
The number of variants: 569
The number of variants after dropping NaN in the column chr:pos: 540
<bound method NDFrame.head of      chr       pos a1 a2   variant_id      gene   type      beta              P
0      1    948870  G  C    rs4615788      AGRN    cis  0.643184   6.320000e-65
1      1   9009414  T  C   rs58800854       CA6    cis -0.697422   1.260000e-57
2      1  11919271  G  A     rs198389      NPPB    cis  0.218212   1.960000e-11
3      1  12254015  C  T    rs2229700  TNFRSF1B    cis  0.845027   1.840000e-12
4      1  19630143  A  G  rs116348652    AKR7A2    cis -1.033610   4.700000e-40
..   ...       ... .. ..          ...       ...    ...       ...            ...
563   22  36661330  A  G    rs2239785     APOL1    cis  0.547644   2.190000e-54
564   22  36661906  G  A   rs73885319     APOL1  trans  0.335227   1.340000e-17
565   22  37966409  A  G   rs73884090    LGALS2    cis -0.474572   4.840000e-18
567   22  50728062  C  T   rs28379706    PLXNB2    cis  0.500647   4.790000e-47
568   22  51062832  A  G    rs8142033      ARSA    cis  0.953126  4.480000e-122

[540 rows x 9 columns]>
---Processing for 6_katz_2021_meta---
The number of variants: 499
   chr a1 a2   variant_id         chr:pos   type      gene      beta             P
0    1  T  C  rs188468174   chr1:25291697  trans     RUNX3 -1.487413  4.032625e-12
1    2  A  G   rs78909033  chr2:241510903  trans   RNPEPL1  0.468746  1.638556e-19
2    4  G  A    rs4253281  chr4:187164349  trans       F11 -0.248212  3.158736e-12
3    5  G  A  rs145394459   chr5:73229720  trans  ARHGEF28 -1.737246  1.989593e-11
4    6  C  T   rs75993961  chr6:147592377  trans    STXBP5  1.150087  9.817528e-12
The number of variants after dropping NaN in the column chr:pos: 480
<bound method NDFrame.head of      chr        pos a1 a2   variant_id      gene   type      beta             P
0      1   25291697  T  C  rs188468174     RUNX3  trans -1.487413  4.032625e-12
1      2  241510903  A  G   rs78909033   RNPEPL1  trans  0.468746  1.638556e-19
2      4  187164349  G  A    rs4253281       F11  trans -0.248212  3.158736e-12
3      5   73229720  G  A  rs145394459  ARHGEF28  trans -1.737246  1.989593e-11
4      6  147592377  C  T   rs75993961    STXBP5  trans  1.150087  9.817528e-12
..   ...        ... .. ..          ...       ...    ...       ...           ...
494   20   23065122  C  T   rs34513402      CD93    cis  1.401333  3.954184e-26
495   20   37012010  G  T   rs11906988       LBP    cis -0.340860  2.240191e-31
496   21   47572887  T  C   rs61735836      FTCD    cis  0.741743  1.604338e-18
497   22   36667154  A  G   rs60295735      MYH9  trans  0.335685  1.066433e-16
498   22   51055231  G  T   rs28871051      ARSA    cis  0.912578  8.212925e-94

[480 rows x 9 columns]>
```

```
for i in discovery meta; do
> sort -k 1n -k 2n 6_katz_2021_${i}_fmt.txt > 6_katz_2021_${i}_fmt_sort.txt
> bgzip <6_katz_2021_${i}_fmt_sort.txt >6_katz_2021_${i}.txt.gz
> tabix -p vcf 6_katz_2021_${i}.txt.gz
> done;
```

## 7_ferkingstad_2021
- platform: SomaScan version 4
    - analyzed 4,907 aptamers that measure 4,719 proteins
- tissue: plasma
- population: European
- n_participants: 35,559 Icelanders 
- n_pQTLs: 18,084 sentinel pQTL associations
    - p<1.8e-9
    - 1,881 cis
    - 16,203 trans
- study: Icelandic Cancer Project & deCODE genetics

### sig_pairs
- sheet: `ST02`
- additional notes: 
    - build: GRCh38
        - rs145474533 1:1749174:C:G. Verified on gnomad https://gnomad.broadinstitute.org/variant/1-1749174-G-C?dataset=gnomad_r4 that the position is in GRCh37 and Amaj is the reference allele and Amin is the alternate allele
        - rs79412885 1:9181780:A:G. Verified on gnomad https://gnomad.broadinstitute.org/variant/1-9181780-G-A?dataset=gnomad_r4
        - rs12132412:21493549:G:A. Verified on gnomad https://gnomad.broadinstitute.org/variant/1-21493549-A-G?dataset=gnomad_r4
    - p values are actually -log10(P)

```
python extract_cols.py 
The number of variants: 28191
<bound method NDFrame.head of         chr      start        end   a1         a2      variant_id protein   type  beta       P
0      chr1    1013854    1013855    A          G       rs2465124   ISG15    cis -0.65   78.37
1      chr1    1014227    1014228    G          A          rs1921   ISG15    cis  0.31  311.57
2      chr1    1019789    1019790    G          A     rs189343112    AGRN    cis -0.16   17.96
3      chr1    1020989    1020990    C          T     rs568254931    AGRN    cis  0.48   20.60
4      chr1    1027510    1027511    T          C       rs4970394    AGRN    cis -0.24  177.54
...     ...        ...        ...  ...        ...             ...     ...    ...   ...     ...
28186  chrX  154410918  154410919    C          T     rs147967693    G6PD    cis -0.11   13.58
28187  chrX  155013425  155013426    T          C       rs5945273      F8    cis -0.06   11.67
28188  chrX  155418692  155418693  NaN  CTTTTTTTT    rs1214264303   CLIC2    cis  0.10    9.14
28189  chrX  155754458  155754459    C          T    rs1010469653   L1CAM  trans -1.64   25.44
28190  chrX  155930662  155930663  NaN       AATT  chrX:155930663   VAMP7    cis -0.06   14.39

[28191 rows x 10 columns]>
```

- liftover
```
liftOver -bedPlus=3 7_ferkingstad_2021_forLiftOver.txt hg38ToHg19.over.chain.gz 7_ferkingstad_2021_hg19.txt 7_ferkingstad_2021_unMapped
```

```
sed 's/chrX/chr23/g' 7_ferkingstad_2021_hg19.txt | sed 's/chr//g' | awk '{print$1"\t"$3"\t"$4"\t"$5"\t"$6"\t
"$7"\t"$8"\t"$9"\t"$10}' | sort -k 1n -k 2n > 7_ferkingstad_2021.txt

bgzip <7_ferkingstad_2021.txt >7_ferkingstad_2021.txt.gz

tabix -p vcf 7_ferkingstad_2021.txt.gz
```

## 8_pietzner_2021
- platform: Somascan v4 assay
    - 4775 protein targets
- tissue: plasma
- population: European
- n_participants: 10,708 
- build: GRCh37
    - spot-check 1: rs4615788 has chr:pos 1:948870. Verified on gnomad: https://gnomad.broadinstitute.org/variant/1-948870-C-G?dataset=gnomad_r2_1
    - spot-check 2: rs3197999 has chr:pos 3:49721532. Verified on gnomad: https://gnomad.broadinstitute.org/variant/3-49721532-G-A?dataset=gnomad_r2_1
- n_pQTLs: 
    - 10,674 genetic variant-protein target associations (P<1.004e-11)
- study: Fenland

### sig_pairs
- sheet: `ST2`
- additional notes: 
    - for the alleles, I noticed that effect allele = alt and non effect allele = ref. However, this rule does not seem to be universal. In the code, I will assign effect allele to be alt (a2) and non effect allele to be ref (a1). Note that this might become an issue later. 
    - I and D in the allele names: 
    ```
    23      155137183       I       D       X:155137183_I_D VAMP7   cis     0.1387  2.56e-19
    ```
    - gene column is HGNC.symbol.protein
        - for the rows that list 2 proteins (example: 'CCL4L2|CCL4L1) I will make 2 rows
        - for the rows that are empty in this field, I will remove them

```
python extract_cols.py 
The number of variants: 10674
The number of variants after dropping NaN in the column protein: 10547
The number of variants after spliting by |: 10738
<bound method NDFrame.head of        chr       pos a1 a2   variant_id  protein   type    beta              P
0        1    948870  G  C    rs4615788      NaN    cis -1.2085  1.400000e-277
1        1    952003  G  A    rs3128118    ISG15    cis  0.4612  6.960000e-245
2        1    961464  G  T    rs3128125     AGRN    cis -0.3222  9.840000e-109
3        1   1164749  I  D  rs113272753  B3GALT6    cis  0.1971   7.960000e-22
4        1   1261824  G  C     rs307348    MXRA8    cis  0.2502   1.360000e-20
...    ...       ... .. ..          ...      ...    ...     ...            ...
10733    3  33841065  G  A    rs9876986  PDCD6IP    cis  0.1411   1.500000e-24
10734    3  38271881  C  T    rs6599079  S100A11  trans  0.5802  3.110000e-159
10735    3  38274503  G  A  rs114563337    ACAA1    cis -0.7835  1.410000e-124
10736    3  38158982  G  A   rs41285115    ACAA1    cis -0.2643   1.160000e-15
10737    3  39188182  C  T   rs13084580      NOG  trans -0.1614   3.340000e-15

[10738 rows x 9 columns]>
```

```
sort -k 1n -k 2n 8_pietzner_2021_fmt.txt > 8_pietzner_2021_fmt_sort.txt
cat ../header.txt 8_pietzner_2021_fmt_sort.txt > 8_pietzner_2021.txt
bgzip <8_pietzner_2021.txt >8_pietzner_2021.txt.gz
tabix -p vcf 8_pietzner_2021.txt.gz
```

## 9_sun_2023
- platform: antibody-based Olink Explore 3072 PEA
    - measuring 2,941 protein analytes
    - capturing 2,923 unique proteins
- tissue: plasma
- population: European
- n_participants: 54,219 UKB participants
- n_pQTLs: 
    - 14,287 significant primary associations 
    - across 3,760 independent genetic regions (P<1.7e-11)
- study: UKB

### sig_pairs
- sheet:
    - `ST9`
    - `ST10`
    - `ST11`

- additional notes: 
    - build: GRCh37
    - alleles check:
        - rs1260326 (2:27730940:T:C:imp:v1). Verified on gnomad: https://gnomad.broadinstitute.org/variant/2-27730940-T-C?dataset=gnomad_r2_1 to confirm that T is the reference allele and C is the alternate allele
        - rs112875651 (8:126506694:G:A:imp:v1). Verified on gnomad: https://gnomad.broadinstitute.org/variant/8-126506694-G-A?dataset=gnomad_r2_1 to confirm that G is the reference allele and A is the alternate allele
        - rs34307716 (10:20199378:G:A:imp:v1). Verified on gnomad: https://gnomad.broadinstitute.org/variant/10-20199378-G-A?dataset=gnomad_r2_1 to confirm that G is the reference allele and A is the alternate allele

- Use the column `Assay Target` for genes
- The P column is log10(p)
- discovery
```
python extract_cols_discovery.py 
The number of variants: 14287
<bound method NDFrame.head of       chr        pos a1 a2   variant_id protein   type      beta          P
0       2   27730940  T  C    rs1260326    A1BG  trans -0.136559    79.2414
1       7   73012042  G  A   rs35332062    A1BG  trans -0.124821    31.5131
2      12  104000470  T  C    rs2723889    A1BG  trans  0.052951    11.8431
3      19   58861808  A  G  rs145144275    A1BG    cis -2.134440   695.1800
4       3   56849749  T  C    rs1354034   AAMDC  trans  0.054528    14.5676
...    ..        ... .. ..          ...     ...    ...       ...        ...
14282   7   76017997  C  T   rs10281089     ZP3    cis  1.105150  4415.1200
14283  10   28912850  C  G    rs1265831     ZP3  trans -0.105959    90.1242
14284  16   30666367  C  T    rs3747481     ZP3  trans -0.035921    11.0429
14285  17    7435040  G  A    rs8073937     ZP3  trans -0.051158    25.1130
14286  19    1646712  C  T    rs4807125     ZP3  trans -0.069083    26.0150

[14287 rows x 9 columns]>
```

- combined
```
python extract_cols_combined.py 
The number of variants: 23588
<bound method NDFrame.head of       chr        pos           a1       a2   variant_id protein   type      beta         P
0       1  161623025            G        C   rs61804164    A1BG  trans  0.066509   12.7664
1       1  234842856            G        C     rs661955    A1BG  trans  0.042624   12.5463
2       2   27730940            T        C    rs1260326    A1BG  trans -0.127668  103.2090
3       7   73020337            C        G    rs3812316    A1BG  trans -0.134210   53.2479
4       7  150311028            C  CCTCTAT  rs141505392    A1BG  trans -0.047795   11.5199
...    ..        ...          ...      ...          ...     ...    ...       ...       ...
23583  16   30666367            C        T    rs3747481     ZP3  trans -0.040055   20.7723
23584  17    7420294            C        G    rs9675122     ZP3  trans -0.053169   41.7417
23585  18   42288703  AAAAAGAAAAG        A  rs547384781     ZP3  trans  0.028564   12.1690
23586  19    1646712            C        T    rs4807125     ZP3  trans -0.068555   38.9507
23587  11  116649538            A        G   rs61905116    ZPR1    cis  0.110287   16.6535

[23588 rows x 9 columns]>
```

- Per non-EUR population:
```
python extract_cols_nonEUR.py 
The number of variants in ancestry CSA: 732
<bound method NDFrame.head of                            id  protein   variant_id ancestry      beta         P type
2      11:77583266:G:A:imp:v1    AAMDC    rs2186564      CSA -1.081680   44.2238  cis
8     9:136132908:T:TC:imp:v1      ABO    rs8176719      CSA  1.068550  107.5690  cis
11     17:61569732:G:A:imp:v1      ACE       rs4351      CSA -0.518677   26.3228  cis
14    7:100510437:G:GA:imp:v1     ACHE  rs576872277      CSA  0.347380   12.7026  cis
15        2:217334:G:C:imp:v1     ACP1    rs6709534      CSA -0.409014   13.7057  cis
...                       ...      ...          ...      ...       ...       ...  ...
1907   17:48910781:T:C:imp:v1  WFIKKN2    rs4611502      CSA -0.726354   47.9852  cis
1910   1:168505133:G:C:imp:v1     XCL1    rs7543171      CSA  0.891563   58.8686  cis
1916   X:128857203:T:A:imp:v1  XPNPEP2    rs4830165      CSA -0.856157   64.4863  cis
1918   15:41119512:G:A:imp:v1  ZFYVE19    rs6492967      CSA -0.355089   14.5934  cis
1922    7:76038153:A:T:imp:v1      ZP3   rs11486951      CSA  0.946798   98.5482  cis

[732 rows x 7 columns]>

<bound method NDFrame.head of      chr        pos a1  a2   variant_id  protein type      beta         P
2     11   77583266  G   A    rs2186564    AAMDC  cis -1.081680   44.2238
8      9  136132908  T  TC    rs8176719      ABO  cis  1.068550  107.5690
11    17   61569732  G   A       rs4351      ACE  cis -0.518677   26.3228
14     7  100510437  G  GA  rs576872277     ACHE  cis  0.347380   12.7026
15     2     217334  G   C    rs6709534     ACP1  cis -0.409014   13.7057
...   ..        ... ..  ..          ...      ...  ...       ...       ...
1907  17   48910781  T   C    rs4611502  WFIKKN2  cis -0.726354   47.9852
1910   1  168505133  G   C    rs7543171     XCL1  cis  0.891563   58.8686
1916  23  128857203  T   A    rs4830165  XPNPEP2  cis -0.856157   64.4863
1918  15   41119512  G   A    rs6492967  ZFYVE19  cis -0.355089   14.5934
1922   7   76038153  A   T   rs11486951      ZP3  cis  0.946798   98.5482

[732 rows x 9 columns]>
The number of variants in ancestry AFR: 785
<bound method NDFrame.head of                                  id  protein   variant_id ancestry      beta         P type
0           19:58863459:CT:C:imp:v1     A1BG            -      AFR  0.733515   22.0685  cis
4            11:77603261:G:C:imp:v1    AAMDC    rs4245454      AFR -0.989089   41.0931  cis
5     17:41099822:C:CTGAGATT:imp:v1   AARSD1   rs57078218      AFR  0.542362   13.5310  cis
6             3:52002918:C:G:imp:v1  ABHD14B  rs116629706      AFR -1.604010   32.3186  cis
7           9:136132908:T:TC:imp:v1      ABO    rs8176719      AFR  1.432200  123.1070  cis
...                             ...      ...          ...      ...       ...       ...  ...
1906     16:681587:TTAAGAA:T:imp:v1  WFIKKN1            -      AFR  0.424229   13.9078  cis
1908         17:48911989:G:A:imp:v1  WFIKKN2    rs3888213      AFR -0.490377   14.6187  cis
1911         1:168505133:G:C:imp:v1     XCL1    rs7543171      AFR  1.058800   31.0434  cis
1917         X:128860545:A:G:imp:v1  XPNPEP2    rs7885638      AFR -1.040400   77.9919  cis
1920          7:76014174:T:C:imp:v1      ZP3    rs7783542      AFR  0.811594   94.6158  cis

[785 rows x 7 columns]>

<bound method NDFrame.head of      chr        pos       a1        a2   variant_id  protein type      beta         P
0     19   58863459       CT         C            -     A1BG  cis  0.733515   22.0685
4     11   77603261        G         C    rs4245454    AAMDC  cis -0.989089   41.0931
5     17   41099822        C  CTGAGATT   rs57078218   AARSD1  cis  0.542362   13.5310
6      3   52002918        C         G  rs116629706  ABHD14B  cis -1.604010   32.3186
7      9  136132908        T        TC    rs8176719      ABO  cis  1.432200  123.1070
...   ..        ...      ...       ...          ...      ...  ...       ...       ...
1906  16     681587  TTAAGAA         T            -  WFIKKN1  cis  0.424229   13.9078
1908  17   48911989        G         A    rs3888213  WFIKKN2  cis -0.490377   14.6187
1911   1  168505133        G         C    rs7543171     XCL1  cis  1.058800   31.0434
1917  23  128860545        A         G    rs7885638  XPNPEP2  cis -1.040400   77.9919
1920   7   76014174        T         C    rs7783542      ZP3  cis  0.811594   94.6158

[785 rows x 9 columns]>
The number of variants in ancestry EAS: 179
<bound method NDFrame.head of                            id  protein  variant_id ancestry      beta        P type
1     11:77401206:CA:C:imp:v1    AAMDC           -      EAS -1.038600  14.6705  cis
10    9:136132908:T:TC:imp:v1      ABO   rs8176719      EAS  0.979152  23.3047  cis
21     1:147125235:C:T:imp:v1     ACP6   rs4950465      EAS  0.983746  27.2995  cis
56       4:7784085:C:T:imp:v1    AFAP1  rs35617438      EAS  1.196460  13.6566  cis
59    16:68278089:CA:C:imp:v1     AGRP           -      EAS  2.904140  11.6546  cis
...                       ...      ...         ...      ...       ...      ...  ...
1891  12:118509347:T:C:imp:v1   VSIG10   rs9669474      EAS  0.663756  10.9036  cis
1901    7:49818317:T:G:imp:v1     VWC2    rs481076      EAS -0.713621  15.0559  cis
1913   1:168513524:A:G:imp:v1     XCL1  rs12042332      EAS  0.913925  18.2802  cis
1914   X:128836369:G:A:imp:v1  XPNPEP2   rs4830159      EAS -1.028760  15.0683  cis
1921    7:76023029:T:C:imp:v1      ZP3  rs10261314      EAS  0.849053  20.1345  cis

[179 rows x 7 columns]>

<bound method NDFrame.head of      chr        pos  a1  a2  variant_id  protein type      beta        P
1     11   77401206  CA   C           -    AAMDC  cis -1.038600  14.6705
10     9  136132908   T  TC   rs8176719      ABO  cis  0.979152  23.3047
21     1  147125235   C   T   rs4950465     ACP6  cis  0.983746  27.2995
56     4    7784085   C   T  rs35617438    AFAP1  cis  1.196460  13.6566
59    16   68278089  CA   C           -     AGRP  cis  2.904140  11.6546
...   ..        ...  ..  ..         ...      ...  ...       ...      ...
1891  12  118509347   T   C   rs9669474   VSIG10  cis  0.663756  10.9036
1901   7   49818317   T   G    rs481076     VWC2  cis -0.713621  15.0559
1913   1  168513524   A   G  rs12042332     XCL1  cis  0.913925  18.2802
1914  23  128836369   G   A   rs4830159  XPNPEP2  cis -1.028760  15.0683
1921   7   76023029   T   C  rs10261314      ZP3  cis  0.849053  20.1345

[179 rows x 9 columns]>
The number of variants in ancestry MID: 227
<bound method NDFrame.head of                                 id  protein   variant_id ancestry      beta        P type
3           11:77583266:G:A:imp:v1    AAMDC    rs2186564      MID -1.080520  11.8333  cis
9          9:136132908:T:TC:imp:v1      ABO    rs8176719      MID  1.137070  32.6647  cis
20          1:147124310:T:G:imp:v1     ACP6    rs2153463      MID  1.041360  29.6358  cis
26          20:43255220:T:C:imp:v1      ADA   rs11555566      MID  1.398990  19.4724  cis
29          1:155033308:G:A:imp:v1   ADAM15   rs11589479      MID  0.790566  13.9108  cis
...                            ...      ...          ...      ...       ...      ...  ...
1892        19:54545531:T:C:imp:v1    VSTM1    rs2433724      MID -0.674471  16.0599  cis
1909  17:48916511:TTTCCTC:T:imp:v1  WFIKKN2  rs760781487      MID -0.652445  11.8824  cis
1912        1:168513489:T:C:imp:v1     XCL1   rs12043081      MID  0.740582  10.9788  cis
1915        X:128848348:A:G:imp:v1  XPNPEP2    rs4829700      MID -0.906752  17.1561  cis
1919         7:76013265:A:G:imp:v1      ZP3   rs11520962      MID  0.955438  30.5895  cis

[227 rows x 7 columns]>

<bound method NDFrame.head of      chr        pos       a1  a2   variant_id  protein type      beta        P
3     11   77583266        G   A    rs2186564    AAMDC  cis -1.080520  11.8333
9      9  136132908        T  TC    rs8176719      ABO  cis  1.137070  32.6647
20     1  147124310        T   G    rs2153463     ACP6  cis  1.041360  29.6358
26    20   43255220        T   C   rs11555566      ADA  cis  1.398990  19.4724
29     1  155033308        G   A   rs11589479   ADAM15  cis  0.790566  13.9108
...   ..        ...      ...  ..          ...      ...  ...       ...      ...
1892  19   54545531        T   C    rs2433724    VSTM1  cis -0.674471  16.0599
1909  17   48916511  TTTCCTC   T  rs760781487  WFIKKN2  cis -0.652445  11.8824
1912   1  168513489        T   C   rs12043081     XCL1  cis  0.740582  10.9788
1915  23  128848348        A   G    rs4829700  XPNPEP2  cis -0.906752  17.1561
1919   7   76013265        A   G   rs11520962      ZP3  cis  0.955438  30.5895

[227 rows x 9 columns]>
The number of variants in ancestry AMR: 0

```
- Sort, bgzip, and tabix
```
for i in discovery combined CSA AFR EAS MID; do
> sort -k 1n -k 2n 9_sun_2023_${i}_fmt.txt > 9_sun_2023_${i}_fmt_sort.txt
> cat ../header.txt 9_sun_2023_${i}_fmt_sort.txt > 9_sun_2023_${i}.txt
> bgzip <9_sun_2023_${i}.txt >9_sun_2023_${i}.txt.gz
> tabix -p vcf 9_sun_2023_${i}.txt.gz
> done;
```

## 10_carland_2023
- meta-analysis
    - 12 European cohorts
    - 90 circulating proteins
- platform: 
    - Proximity Extension Assay (PEA)
    - 92 proteins on the Olink Target Metabolism
- tissue: plasma
- population: European
- n_participants: 22,997
- build: GRCh37
    - rs2427308 (from the paper: 20:60969451:T:C). Verified on gnomad https://gnomad.broadinstitute.org/variant/20-60969451-C-T?dataset=gnomad_r2_1 to confirm that the coordinate is in GRCh37 and the column Other allele if the reference allele and the column Reference Allele is the alternate allele
    - rs17138667 (from the paper: 5:115351224:A:G). Verified on gnomad https://gnomad.broadinstitute.org/variant/5-115351224-G-A?dataset=gnomad_r2_1 to confirm that the coordinate is in GRCh37 and the column Other allele if the reference allele and the column Reference Allele is the alternate allele
- n_pQTLs: 
    - 178 independent pQTLs (P<5.6e-10)
    - 325 conditionally independent pQTLs (P<5.6e-10)
- study: meta analysis on 12 cohorts

### sig_pairs
- sheet: 
    - `5a Pooled pQTLs`
    - `5b Female pQTLs`
    - `5c Male pQTLs`
- additional notes: 
    - sex-stratified
        - 258 pQTLs among men
        - 552 pQTLs among women
- pooled
```
python extract_cols_pooled.py 
The number of variants: 503
<bound method NDFrame.head of     chr        pos a1 a2   variant_id   protein   type      beta              P
0     8   20150177  G  A   rs28690412      GHRL  trans  0.062193   5.470000e-10
1     8  134470533  A  C   rs72718252    CCDC80  trans  0.064241   5.450000e-10
2    17   64294581  T  C  rs117280021     CDHR5  trans  0.397193   5.290000e-10
3    12  112083162  C  T   rs11065991      TYMP  trans  0.058356   4.970000e-10
4    11   74265980  G  A    rs1791495    CHRDL2    cis  0.069807   4.730000e-10
..   ..        ... .. ..          ...       ...    ...       ...            ...
498  19   51460515  G  C  rs148904561     KLK10    cis  0.627006   2.460000e-62
499  18   61654463  A  G    rs3826616  SERPINB8    cis -0.659544   4.080000e-92
500  19   51523928  G  A  rs148431400     KLK10    cis  0.710987  1.190000e-119
501  15   79234957  G  A   rs34593439      CTSH    cis -0.920372  1.250000e-140
502  15   79167260  T  C   rs77362013      CTSH    cis  0.655568  2.440000e-154

[503 rows x 9 columns]>
```

- female
```
python extract_cols_female.py 
The number of variants: 552
<bound method NDFrame.head of      chr        pos a1 a2   variant_id protein   type      beta              P
0      1  146561330  T  C   rs79566071    ACP6  trans -0.570238   4.110000e-16
1      1  147010866  T  G   rs78300852    ACP6    cis -0.500010   1.830000e-32
2      1  147262276  A  G   rs78010317    ACP6    cis  0.314873   6.280000e-12
3      1  144918246  G  A   rs77955958    ACP6  trans -0.372783   4.030000e-14
4      1  147067648  T  G   rs77245299    ACP6    cis -1.447707  2.270000e-233
..   ...        ... .. ..          ...     ...    ...       ...            ...
547    5   82973084  C  G   rs17206110    VCAN    cis -0.150221   6.010000e-12
548    5   82844579  G  A  rs149879035    VCAN    cis -0.377900   1.710000e-12
549    8   19613739  A  C    rs1492634    VCAN  trans -0.079961   2.370000e-10
550    5   82896062  G  A  rs113066179    VCAN    cis  0.235334   1.010000e-24
551    5   81716027  G  A   rs10491244    VCAN  trans -0.130867   1.490000e-15

[552 rows x 9 columns]>
```

- male
```
python extract_cols_male.py 
The number of variants: 258
<bound method NDFrame.head of      chr        pos a1 a2  variant_id  protein   type      beta             P
0     19   51626237  A  G   rs1039405  SIGLEC7    cis -0.135561  2.420000e-08
1     11  123038062  T  C  rs10750232     CLMP    cis  0.128007  1.200000e-10
2     12     546036  G  C  rs10774190     SOST  trans -0.079722  3.420000e-10
3      3  140433959  T  C  rs10935394   CLSTN2    cis -0.121054  9.260000e-09
4     11   45221963  C  G  rs11038350     TSHB  trans -0.087682  3.900000e-09
..   ...        ... .. ..         ...      ...    ...       ...           ...
253    6    1668720  G  A   rs9502996      GAL  trans  0.142581  3.630000e-10
254   12   29491528  A  G    rs966541    FCRL1  trans  0.081923  4.340000e-08
255    3  139245449  A  T   rs9837167   CLSTN2    cis  0.100170  1.870000e-10
256   17   80963331  C  T   rs9901757   METRNL    cis -0.085855  1.440000e-14
257   16   57002732  T  G   rs9939224    CLUL1  trans  0.107090  5.290000e-11

[258 rows x 9 columns]>
```

- Sort, bgzip, and tabix
```
for i in pooled female male; do
> sort -k 1n -k 2n 10_carland_2023_${i}_fmt.txt > 10_carland_2023_${i}_fmt_sort.txt
> cat ../header.txt 10_carland_2023_${i}_fmt_sort.txt > 10_carland_2023_${i}.txt
> bgzip <10_carland_2023_${i}.txt >10_carland_2023_${i}.txt.gz
> tabix -p vcf 10_carland_2023_${i}.txt.gz
> done;
```

## 11_niu_2025
- platform: MS-based plasma proteome profiling
- tissue: plasma
- population: European (Danish)
- n_participants: 
    - discovery: 
        - 2,147 children and adolescents
        - 55% females, 45% males
        - aged 5-20 years
    - replication
        - 1000 matched by age, sex, and obesity status (58% females, 42% males)
- n_pQTLs: 
    - 5.2 million SNPs were teste for association with plasma levels of 1,216 proteins in 1,909 individuals
    - Stringent threshold: 1,252 primary pQTLs for 327 proteins (P<4.1e-11)
    - Relaxed threshold: 1,947 primary pQTLs for 443 proteins (P<5e-8)
    - Approximate conditional analyses: 733 conditionally independent pQTLs for 443 proteins
- study: HOLBAEK (Denmark)

### sig_pairs
- sheet: 
    - `ST4`
    - `ST5`
    - `ST13`
    - `ST14`
- additional notes:
    - build: GRCh37
        - In `ST4`, rs12406047 is annotated as `1_196677898_A_T`. Verified on gnomad https://gnomad.broadinstitute.org/variant/1-196677898-A-T?dataset=gnomad_r2_1 that the coordinate is in GRCh37 and the convention is chr_pos_ref_alt
        - rs142072893 is annotated as `1_150338310_A_T`. Verified on gnomad https://gnomad.broadinstitute.org/variant/1-150338310-A-T?dataset=gnomad_r2_1 that the coordinate is in GRCh37
    - column `lead_located_gene`: this indicates the gene where the variant is in (or close to). 
    - column `Gene name`: this indicates the gene that the variant is associated with in the GWAS
    - created 5 files: 
        - `11_niu_2025_discovery_relaxedP_fmt.txt`
        - `11_niu_2025_discovery_stringentP_fmt.txt`
        - `11_niu_2025_independent_fmt.txt`
        - `11_niu_2025_replicatedChildren_fmt.txt`
        - `11_niu_2025_replicatedAdult_fmt.txt`

- discovery
```
python extract_cols_discovery.py 
The number of variants: 1947
<bound method NDFrame.head of       chr        pos a1 a2  variant_id      gene   type      beta              P
0       1  196677898  A  T  rs12406047        C3  trans -0.265613   1.374672e-09
1       1  196673430  T  G   rs9970075     CFHR2    cis -0.693247  3.929549e-110
2       1  196696875  G  T    rs419137     CFHR2    cis -0.486135   9.105874e-22
3       1  196887457  G  A  rs10494745     CFHR2    cis  0.488238   7.695789e-22
4       1  196929310  C  T   rs7531555     CFHR2    cis -1.108215  8.840972e-241
...   ...        ... .. ..         ...       ...    ...       ...            ...
1942   22   22551837  A  G   rs5757343  IGLV6-57    cis -0.304317   1.810123e-21
1943   22   23249440  C  A   rs2856876  IGLV7-43    cis  0.359631   1.621257e-12
1944   22   22548492  T  C   rs1543779  IGLV6-57    cis  0.529676   8.218333e-58
1945   22   23249440  C  A   rs2856876  IGLV4-69    cis  0.409795   5.192845e-16
1946   22   22550450  C  G   rs2073447     SOCS5  trans -0.481025   5.527554e-51

[1947 rows x 9 columns]>
The number of variants passing the stringent threshold: 1325
<bound method NDFrame.head of       chr        pos a1 a2  variant_id      gene   type      beta              P
1       1  196673430  T  G   rs9970075     CFHR2    cis -0.693247  3.929549e-110
2       1  196696875  G  T    rs419137     CFHR2    cis -0.486135   9.105874e-22
3       1  196887457  G  A  rs10494745     CFHR2    cis  0.488238   7.695789e-22
4       1  196929310  C  T   rs7531555     CFHR2    cis -1.108215  8.840972e-241
5       1  197062923  T  C  rs10801588     CFHR2    cis -0.403412   2.829004e-14
...   ...        ... .. ..         ...       ...    ...       ...            ...
1942   22   22551837  A  G   rs5757343  IGLV6-57    cis -0.304317   1.810123e-21
1943   22   23249440  C  A   rs2856876  IGLV7-43    cis  0.359631   1.621257e-12
1944   22   22548492  T  C   rs1543779  IGLV6-57    cis  0.529676   8.218333e-58
1945   22   23249440  C  A   rs2856876  IGLV4-69    cis  0.409795   5.192845e-16
1946   22   22550450  C  G   rs2073447     SOCS5  trans -0.481025   5.527554e-51

[1325 rows x 9 columns]>
```

- conditionally independent
```
ython extract_cols_independent.py 
The number of variants: 733
<bound method NDFrame.head of     chr        pos a1 a2  variant_id      gene  type      beta              P
0    16   72078043  C  T         NaN     APOL2   NaN  0.494901   8.886250e-29
1    16   72105965  T  C         NaN     APOL2   NaN  0.356179   2.768370e-16
2     2  202863358  A  T         NaN  IGHV4-61   NaN  0.193848   1.211080e-08
3    14  107163301  A  G         NaN  IGHV4-61   NaN  0.312113   2.069530e-16
4    22   22550450  C  G         NaN     SOCS5   NaN -0.481025   2.211950e-48
..   ..        ... .. ..         ...       ...   ...       ...            ...
728   5   76194625  T  C         NaN     CRHBP   NaN -0.286102   2.905400e-17
729  12   56740682  C  G         NaN      APOF   NaN -0.468026   1.364970e-14
730   9  136142313  A  C         NaN      CDH5   NaN  1.135830   3.067070e-79
731   1  169511755  T  C         NaN     SLIT1   NaN  1.224060  3.800150e-238
732   6  161092438  C  T         NaN       PLG   NaN -0.495324   3.939720e-23

[733 rows x 9 columns]>
```

- Replication in children
```
python extract_cols_replicatedChildren.py 
---Replication in children---
The number of variants: 1729
The number of replicated variants (exact): 1586
<bound method NDFrame.head of      chr        pos a1 a2  variant_id       gene  type    beta                      P
0      1  196677898  A  T         NaN         C3   NaN   -0.26           2.049478e-05
1     13  113820136  C  T         NaN  SERPINA10   NaN   0.293           2.049922e-09
2     13  113846989  G  C         NaN  SERPINA10   NaN   0.225           6.026601e-06
3     13  113967851  G  C         NaN  SERPINA10   NaN  -0.229           4.922681e-06
4     13   46661129  G  C         NaN       CPB2   NaN    0.53           3.560812e-26
...   ..        ... .. ..         ...        ...   ...     ...                    ...
1581   5  135418032  G  A         NaN      TGFBI   NaN   0.417  6.662724999999999e-19
1582   6  160952838  G  A         NaN        LPA   NaN   0.298           3.359356e-09
1583   5  176807191  C  T         NaN        F12   NaN   0.236            0.004369775
1584   5   40380858  A  C         NaN         C7   NaN  -0.305           9.755066e-09
1585   5   42762420  T  C         NaN    SELENOP   NaN   0.187           3.074777e-05

[1586 rows x 9 columns]>
```

- Replication in adutls
```
python extract_cols_replicatedAdult.py 
---Replication in adults---
The number of variants: 1754
The number of replicated variants (exact): 1360
<bound method NDFrame.head of      chr        pos a1 a2  variant_id   gene  type    beta                       P
0      9  136529614  G  C         NaN    DBH   NaN  -0.335            1.064037e-07
1     12  102218899  T  C         NaN   CTBS   NaN  -0.216            0.0007347018
2     12   69756291  A  T         NaN    LYZ   NaN  -0.393            1.656428e-07
3     12    7176204  G  A         NaN   C1QC   NaN  -0.508            1.867504e-08
4     12    7069654  G  A         NaN    C1R   NaN   0.181              0.04686358
...   ..        ... .. ..         ...    ...   ...     ...                     ...
1355   6  133039851  C  A         NaN   VNN1   NaN   0.463            5.042585e-14
1356   6  133022197  A  G         NaN   VNN1   NaN    0.78  1.8563759999999999e-41
1357   6  133036513  T  C         NaN   VNN1   NaN  -0.213            0.0008706926
1358   1  230845977  G  A         NaN  TGFBI   NaN  -0.249             0.002561454
1359   1  230825427  T  G         NaN  TGFBI   NaN  -0.347            0.0007361992

[1360 rows x 9 columns]>
```
- Sort, bgzip, and tabix:
```
for i in discovery_relaxedP discovery_stringentP independent replicatedChildren replicatedAdult; do
> sort -k 1n -k 2n 11_niu_2025_${i}_fmt.txt > 11_niu_2025_${i}_fmt_sort.txt
> cat ../header.txt 11_niu_2025_${i}_fmt_sort.txt > 11_niu_2025_${i}.txt
> bgzip <11_niu_2025_${i}.txt >11_niu_2025_${i}.txt.gz
> tabix -p vcf 11_niu_2025_${i}.txt.gz
> done;
```

## 12_yang_2021
- platform: multiplexed, aptamer-based platform
    - 1,305 proteins
- tissue: 
    - brain (parietal lobe cortex)
    - cerebrospinal fluid
    - plasma
- population: 
- n_participants: 1,537 
- n_pQTLs: number of independent pQTLs 
    - 274 pQTLs for cerebrospinal fluid
    - 127 pQTLs for plasma
    - 32 pQTLs for brain
- study: Washington University School of Medicine in St. Louis

### sig_pairs
- sheet: 
    - `TableS3`
    - `TableS4`
    - `TableS5`
- additional notes: 
	- build: GRCh37
        - 1-120366283-C-T. Verified on gnomad: https://gnomad.broadinstitute.org/variant/1-120366283-C-T?dataset=gnomad_r2_1
        - 1-203079575-A-G. Verified on gnomad: https://gnomad.broadinstitute.org/variant/1-203079575-A-G?dataset=gnomad_r2_1
- CSF
```
python extract_cols_CSF.py 
The number of variants: 33253
The number of variants after merging to get the protein: 33253
<bound method NDFrame.head of        chr        pos a1 a2  variant_id protein   type      beta             P
0        1  156243821  C  T         NaN   BGLAP    cis -0.024689  4.723780e-08
1        1  156245245  C  T         NaN   BGLAP    cis -0.024699  4.593020e-08
2        1  156246473  C  G         NaN   BGLAP    cis -0.024699  4.593020e-08
3        1  156249505  A  G         NaN   BGLAP    cis -0.024699  4.593020e-08
4        1  156272271  C  T         NaN   BGLAP    cis -0.024699  4.593020e-08
...    ...        ... .. ..         ...     ...    ...       ...           ...
33248   22   51064915  A  G         NaN    ARSA    cis -0.067055  3.935840e-20
33249   22   51065600  A  G         NaN    ARSA    cis -0.096947  5.393210e-16
33250   22   33730891  C  T         NaN   PDIA3  trans -0.055198  2.733060e-08
33251   22   33735607  A  G         NaN   PDIA3  trans -0.054507  4.421470e-08
33252   22   33737243  A  G         NaN   PDIA3  trans -0.054507  4.421470e-08

[33253 rows x 9 columns]>
```

- Plasma
```
python extract_cols_plasma.py 
The number of variants: 11605
The number of variants after merging to get the protein: 11605
<bound method NDFrame.head of        chr        pos a1 a2  variant_id protein   type      beta             P
0        1  196675239  C  G         NaN  PDGFRA  trans  0.173375  2.374640e-08
1        1  196692940  A  G         NaN  PDGFRA  trans  0.176632  3.379010e-08
2        1  196712902  C  T         NaN  PDGFRA  trans  0.097751  3.596850e-08
3        1  196715666  G  A         NaN  PDGFRA  trans  0.100038  4.580750e-08
4        1  196851253  G  T         NaN  PDGFRA  trans  0.112749  4.247090e-08
...    ...        ... .. ..         ...     ...    ...       ...           ...
11600   22   17616217  C  T         NaN  IL17RA    cis  0.088618  7.846420e-15
11601   22   17616510  A  C         NaN  IL17RA    cis  0.089790  4.394000e-15
11602   22   17617451  A  G         NaN  IL17RA    cis  0.089142  3.377650e-14
11603   22   17589567  C  T         NaN  IL17RA  trans  0.062100  3.599790e-08
11604   22   50697518  A  G         NaN  PLXNB2    cis -0.027662  2.252920e-08

[11605 rows x 9 columns]>
```

- Brain
```
python extract_cols_brain.py 
The number of variants: 2678
The number of variants after merging to get the protein: 2678
<bound method NDFrame.head of       chr        pos a1 a2  variant_id protein   type      beta             P
0       1  163067873  C  T         NaN  IL10RA  trans -0.039461  8.699730e-09
1       1  154548946  C  T         NaN     JUN  trans  0.071622  3.443130e-08
2       1  154548992  C  T         NaN     JUN  trans  0.071622  3.443130e-08
3       1  203115367  G  T         NaN  CHI3L1    cis  0.191963  1.572600e-08
4       1  203118632  A  G         NaN  CHI3L1    cis  0.190975  1.847780e-08
...   ...        ... .. ..         ...     ...    ...       ...           ...
2673   22   21366206  C  T         NaN    CST7  trans -0.029947  2.572390e-08
2674   22   21366206  C  T         NaN  TNFSF8  trans -0.020762  1.865950e-08
2675   22   51064416  A  G         NaN    ARSA    cis -0.030297  5.302230e-09
2676   22   51064915  A  G         NaN    ARSA    cis -0.028787  8.828180e-10
2677   22   48510196  A  G         NaN    PTEN  trans  0.019072  3.540860e-08

[2678 rows x 9 columns]>
```

- Sort, bgzip, and tabix:
```
for i in CSF plasma brain; do
> sort -k 1n -k 2n 12_yang_2021_${i}_fmt.txt > 12_yang_2021_${i}_fmt_sort.txt
> cat ../header.txt 12_yang_2021_${i}_fmt_sort.txt > 12_yang_2021_${i}.txt
> bgzip <12_yang_2021_${i}.txt >12_yang_2021_${i}.txt.gz
> tabix -p vcf 12_yang_2021_${i}.txt.gz
> done;
```