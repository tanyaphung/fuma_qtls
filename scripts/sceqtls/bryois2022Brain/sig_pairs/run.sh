#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate base

snakemake -s process.smk -j10 --configfile config.json --rerun-incomplete

cd /QTL/sceQTL/bryois2022Brain/sig_pairs #TODO: put in the correct path

for ct in Microglia Oligodendrocytes Pericytes OPCs...COPs Excitatory.neurons Endothelial.cells Inhibitory.neurons Astrocytes
do
for chr in {1..22}
do
grep chr${chr} sceQTL_bryois2022Brain_${ct}.chr${chr}_tmp.txt | sed 's/chr//g' | awk '{print$1"\t"$3"\t"$4"\t"$5"\t"$6"\t"$7"\t"$8"\t"$9"\t"$10}' | sort -k1,1 -k2,2n > sceQTL_bryois2022Brain_${ct}.chr${chr}.txt

cat sceQTL_bryois2022Brain_${ct}.chr${chr}.txt >> sceQTL_bryois2022Brain_${ct}.txt
done

bgzip sceQTL_bryois2022Brain_${ct}.txt
tabix -p vcf sceQTL_bryois2022Brain_${ct}.txt.gz

done



