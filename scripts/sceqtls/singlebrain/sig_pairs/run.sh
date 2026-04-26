#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate base

snakemake -s process.smk -j10 --configfile config.json --rerun-incomplete

cd /QTL/sceQTL/singlebrain/sig_pairs

for ct in Ast1 OD OPC1 OPC OPC2 IN3 Ast2 Ext2 Ast Ast3 Ext1 Ast4 Ext5 Ext3 Ext4 End IN1 IN5 Ext6 Ext7 IN4 Ext IN Ext8 IN6 MG3 IN7 IN2 OD1 OD2 MG MG4 MiGA3 MG1 MG2 OD3
do
for chr in {1..22}
do
grep -w chr${chr} ${ct}.chr${chr}_tmp.txt | sed 's/chr//g' | awk '{print$1"\t"$3"\t"$4"\t"$5"\t"$6"\t"$7"\t"$8"\t"$9"\t"$10}' | sort -k1,1 -k2,2n > ${ct}.chr${chr}.txt

cat ${ct}.chr${chr}.txt >> singlebrain_${ct}.txt
done

bgzip singlebrain_${ct}.txt
tabix -p vcf singlebrain_${ct}.txt.gz

done



