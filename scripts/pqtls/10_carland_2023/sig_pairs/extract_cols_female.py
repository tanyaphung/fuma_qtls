import pandas as pd
import os
import numpy as np

supp_path = "../../../data/pQTLs/10_carland_2023/10_carland_2023_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="5b Female pQTLs",
                       skiprows=1,
                       header=None,
                       usecols='A, B, C, D, F, L, M, N, O', 
                       names=["chr", "pos", "a2", "a1", "beta", "P", "protein_id", "type", "variant_id"])

print(f"The number of variants: {data.shape[0]}")

data["protein"] = data["protein_id"].str.split("_").str[0]

# convert X to 23
data.loc[data["chr"].isin(["X", "x"]), "chr"] = 23

data_out = data[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]
print(data_out.head)
data_out.to_csv("../../../data/pQTLs/10_carland_2023/10_carland_2023_female_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
