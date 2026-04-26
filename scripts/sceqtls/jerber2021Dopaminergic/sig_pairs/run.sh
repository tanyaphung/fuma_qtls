#!/bin/bash

snakemake -s process.smk -j8 --configfile config.json --rerun-incomplete


cd /QTL/sceQTL/jerber2021Dopaminergic/sig_pairs #TODO: put in the correct path

for ct in D11.FPP D30.FPP D11.P_FPP D30.DA D30.Epen1 D30.Sert D52.Astro.ROT_treated D52.Astro.untreated D52.DA.ROT_treated D52.DA.untreated D52.Epen1.ROT_treated D52.Epen1.untreated D52.pseudobulk.untreated D52.Sert.ROT_treated D52.Sert.untreated
do
for chr in {1..22}
do
grep chr${chr} sceQTL_jerber2021Dopaminergic_${ct}.chr${chr}_tmp.txt | sed 's/chr//g' | awk '{print$1"\t"$3"\t"$4"\t"$5"\t"$6"\t"$7"\t"$8"\t"$9"\t"$10}' | sort -k1,1 -k2,2n > sceQTL_jerber2021Dopaminergic_${ct}.chr${chr}.txt

cat sceQTL_jerber2021Dopaminergic_${ct}.chr${chr}.txt >> sceQTL_jerber2021Dopaminergic_${ct}.txt
done

bgzip sceQTL_jerber2021Dopaminergic_${ct}.txt
tabix -p vcf sceQTL_jerber2021Dopaminergic_${ct}.txt.gz

done



