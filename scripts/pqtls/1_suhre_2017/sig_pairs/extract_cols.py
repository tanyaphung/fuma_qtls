import pandas as pd
import os
import numpy as np

supp_path = "/pQTLs/1_suhre_2017/1_suhre_2017_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="Supplemental Data 1",
                       skiprows=2,
                       header=None,
                       usecols='D, F, G, H, I, J, K, N, R', 
                       names=["type", "protein", "variant_id", "chr", "pos", "a1", "a2", "beta", "P"])

print(f"The number of variants: {data.shape[0]}")

#if there are more than 1 gene, split into different rows
data["protein"] = data["protein"].str.split(" ")
data = data.explode("protein", ignore_index=True)
print(f"The number of variants after spliting by |: {data.shape[0]}")

# convert X to 23
data.loc[data["chr"].isin(["X", "x"]), "chr"] = 23

data_out = data[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]
print(data_out.head)
data_out.to_csv("/pQTLs/1_suhre_2017/1_suhre_2017_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
