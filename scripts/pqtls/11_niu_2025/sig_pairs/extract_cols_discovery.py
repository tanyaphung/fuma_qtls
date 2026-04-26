import pandas as pd
import os
import numpy as np

supp_path = "/pQTLs/11_niu_2025/11_niu_2025_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="ST4",
                       skiprows=2,
                       header=None,
                       usecols='B, C, D, H, I, K, M, O, P, R', 
                       names=["variant_id", "chr", "pos", "a1", "a2", "P", "beta", "genome_sig", "type", "gene"])

print(f"The number of variants: {data.shape[0]}")

# convert X to 23
data.loc[data["chr"].isin(["X", "x"]), "chr"] = 23

data_out = data[["chr", "pos", "a1", "a2", "variant_id", "gene", "type", "beta", "P"]]
print(data_out.head)
data_out.to_csv("/pQTLs/11_niu_2025/11_niu_2025_discovery_relaxedP_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')

# Filter based on genome-wide significant (when using a more stringent threshold)
data_stringent = data[data["genome_sig"]=="yes"]
print(f"The number of variants passing the stringent threshold: {data_stringent.shape[0]}")
data_stringent_out = data_stringent[["chr", "pos", "a1", "a2", "variant_id", "gene", "type", "beta", "P"]]
print(data_stringent_out.head)
data_stringent.to_csv("/pQTLs/11_niu_2025/11_niu_2025_discovery_stringentP_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
