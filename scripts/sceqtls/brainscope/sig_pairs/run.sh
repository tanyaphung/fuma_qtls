#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate base

snakemake -s process.smk -j10 --configfile config.json --rerun-incomplete

cd QTL/sceQTL/brainscope/sig_QTLs

for ct in Astro Chandelier__Pvalb L5.6.NP L4.IT L2.3.IT L6.CT L6b L5.IT Micro.PVM Lamp5 Lamp5.Lhx6 L6.IT Sst__Sst.Chodl PC OPC Oligo Vip
do
for chr in {1..22}
do
grep -w chr${chr} ${ct}.chr${chr}_tmp.txt | sed 's/chr//g' | awk '{print$1"\t"$3"\t"$4"\t"$5"\t"$6"\t"$7"\t"$8"\t"$9"\t"$10}' | sort -k1,1 -k2,2n > ${ct}.chr${chr}.txt

cat ${ct}.chr${chr}.txt >> Brain_${ct}.txt
done

bgzip Brain_${ct}.txt
tabix -p vcf Brain_${ct}.txt.gz

done



