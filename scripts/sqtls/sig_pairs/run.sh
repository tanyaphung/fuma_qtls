#!/bin/bash

snakemake -s process.smk -j5 --configfile config.json --rerun-incomplete --config chrom="1"
# then repeats for all chromosomes.

cd /QTL/aQTL/gtex_v10/sig_pairs

for tissue in Adipose_Subcutaneous Adipose_Visceral_Omentum Adrenal_Gland Artery_Aorta Artery_Coronary Artery_Tibial Bladder Brain_Amygdala Brain_Anterior_cingulate_cortex_BA24 Brain_Caudate_basal_ganglia Brain_Cerebellar_Hemisphere Brain_Cerebellum Brain_Cortex Brain_Frontal_Cortex_BA9 Brain_Hippocampus Brain_Hypothalamus Brain_Nucleus_accumbens_basal_ganglia Brain_Putamen_basal_ganglia Brain_Spinal_cord_cervical_c-1 Brain_Substantia_nigra Breast_Mammary_Tissue Cells_Cultured_fibroblasts Cells_EBV-transformed_lymphocytes Colon_Sigmoid Colon_Transverse Esophagus_Gastroesophageal_Junction Esophagus_Mucosa Esophagus_Muscularis Heart_Atrial_Appendage Heart_Left_Ventricle Kidney_Cortex Liver Lung Minor_Salivary_Gland Muscle_Skeletal Nerve_Tibial Ovary Pancreas Pituitary Prostate Skin_Not_Sun_Exposed_Suprapubic Skin_Sun_Exposed_Lower_leg Small_Intestine_Terminal_Ileum Spleen Stomach Testis Thyroid Uterus Vagina Whole_Blood

do
for chr in {1..22}
do
grep -w chr${chr} ${tissue}.chr${chr}_tmp.txt | sed 's/chr//g' | awk '{print$1"\t"$3"\t"$4"\t"$5"\t"$6"\t"$7"\t"$8"\t"$9"\t"$10}' | sort -k1,1 -k2,2n > ${tissue}.chr${chr}.txt

cat ${tissue}.chr${chr}.txt >> gtex_v10_${tissue}.txt
done

bgzip gtex_v10_${tissue}.txt
tabix -p vcf gtex_v10_${tissue}.txt.gz

done



