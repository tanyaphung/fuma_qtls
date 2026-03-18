#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate base

snakemake -s process_metabrain.smk -j10 --configfile config.json --rerun-incomplete

cd /QTL/eQTL/metabrain

for region in basalganglia cerebellum cortex hippocampus spinalcord
do
for chr in {1..22}
do
sort -k1,1 -k2,2n ${region}/eQTL_metabrain_${region}_chr${chr}_tmp.txt > ${region}/eQTL_metabrain_${region}_chr${chr}.txt

bgzip ${region}/eQTL_metabrain_${region}_chr${chr}.txt
tabix -p vcf ${region}/eQTL_metabrain_${region}_chr${chr}.txt.gz

done
done


