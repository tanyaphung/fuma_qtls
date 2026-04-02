#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate base

# break down by chromosome for efficiency
snakemake -s format.smk -j5 --configfile config.json --rerun-incomplete --config chrom="1"
# repeat for all chromosomes

cd /QTL/sceQTL/singlebrain

for ct in Ast1 OD OPC1 OPC OPC2 IN3 Ast2 Ext2 Ast Ast3 Ext1 Ast4 Ext5 Ext3 Ext4 End IN1 IN5 Ext6 Ext7 IN4 Ext IN Ext8 IN6 MG3 IN7 IN2 OD1 OD2 MG MG4 MiGA3 MG1 MG2 OD3
do
for chr in {1..22}
do
sort -k1,1 -k2,2n sceQTL_singlebrain_${ct}_chr${chr}_tmp.txt > sceQTL_singlebrain_${ct}_chr${chr}.txt

bgzip sceQTL_singlebrain_${ct}_chr${chr}.txt
tabix -p vcf sceQTL_singlebrain_${ct}_chr${chr}.txt.gz

done
done


