import pandas as pd
import os
import numpy as np

input_path = "/pQTLs/4_sun_2018/4_sun_2018_supp.xlsx"

data = pd.read_excel(input_path, 
                     sheet_name="ST4 - pQTL summary", 
                     skiprows=6, 
                     header=None, 
                     usecols='B, F, G, H, K, L, O, W, Y', 
                     names=["somamer_id", "variant_id", "chr", "pos", "a2", "a1", "type", "beta", "P"])
print(data.head())

data["protein"] = data["somamer_id"].str.split(".").str[0]

updated_data = data[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]

updated_data.loc[updated_data["chr"].isin(["X", "x"]), "chr"] = 23
print(updated_data.head())

updated_data.to_csv("/pQTLs/4_sun_2018/4_sun_2018_supp_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')