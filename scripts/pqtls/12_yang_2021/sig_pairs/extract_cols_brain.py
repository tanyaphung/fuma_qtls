import pandas as pd
import os
import numpy as np

supp_path = "/pQTLs/12_yang_2021/12_yang_2021_supp.xlsx"

protein_lookup = pd.read_excel(supp_path, 
                       sheet_name="TableS2",
                       skiprows=2,
                       header=None,
                       usecols='A, E', 
                       names=["SOMAseqID", "protein"])

data = pd.read_excel(supp_path, 
                       sheet_name="TableS5",
                       skiprows=2,
                       header=None,
                       usecols='A, C, D, F, G, I, J, K', 
                       names=["id", "chr", "pos", "a1", "a2", "type", "beta", "P"])

print(f"The number of variants: {data.shape[0]}")

# get the protein
data["SOMAseqID"] = data["id"].str.split("_").str[0]

data_protein = data.merge(protein_lookup, on="SOMAseqID", how="inner")
print(f"The number of variants after merging to get the protein: {data.shape[0]}")

# convert X to 23
data_protein.loc[data_protein["chr"].isin(["X", "x"]), "chr"] = 23

# add empty variant_id
data_protein["variant_id"] = np.nan

data_protein_out = data_protein[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]
print(data_protein_out.head)
data_protein_out.to_csv("/pQTLs/12_yang_2021/12_yang_2021_brain_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
