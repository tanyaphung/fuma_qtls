import pandas as pd
import os
import numpy as np

supp_path = "/pQTLs/8_pietzner_2021/8_pietzner_2021_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="ST2",
                       skiprows=1,
                       header=None,
                       usecols='G, H, I, J, K, L, N, P, S', 
                       names=["variant_id", "type", "chr", "pos", "a2", "a1", "beta", "P", "protein"])
print(f"The number of variants: {data.shape[0]}")

#if the column "gene" has NaN, drop it
data = data.dropna(subset=["protein"])
print(f"The number of variants after dropping NaN in the column protein: {data.shape[0]}")

data["protein"] = data["protein"].str.split("'").str[1]

#if there are more than 1 gene, split into different rows
data["protein"] = data["protein"].str.split("|")
data = data.explode("protein", ignore_index=True)
print(f"The number of variants after spliting by |: {data.shape[0]}")

# convert X to 23
data.loc[data["chr"].isin(["X", "x"]), "chr"] = 23

data_out = data[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]
print(data_out.head)
data_out.to_csv("/pQTLs/8_pietzner_2021/8_pietzner_2021_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
