#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate base

# run snakemake script

snakemake -s process_metabrain.smk -j10 --configfile config.json --rerun-incomplete

# post snakemake, sort, bgzip, and tabix

cd g/QTL/eQTL/metabrain #TODO: put in the correct path

for region in basalganglia cerebellum cortex hippocampus spinalcord
do
for chr in {1..22}
do
grep chr${chr} ${region}/${region}_chr${chr}_tmp.txt | sed 's/chr//g' | awk '{print$1"\t"$3"\t"$4"\t"$5"\t"$6"\t"$7"\t"$8"\t"$9"\t"$10}' | sort -k1,1 -k2,2n > ${region}/${region}_chr${chr}.txt

cat ${region}/${region}_chr${chr}.txt >> ${region}/${region}.txt
done

bgzip ${region}/${region}.txt
tabix -p vcf ${region}/${region}.txt.gz

done



