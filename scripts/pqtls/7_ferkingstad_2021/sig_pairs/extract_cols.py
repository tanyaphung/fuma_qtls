import pandas as pd
import os
import numpy as np

supp_path = "/pQTLs/7_ferkingstad_2021/7_ferkingstad_2021_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="ST02",
                       skiprows=3,
                       header=None,
                       usecols='C, K, N, O, R, S, V, Z, AB',
                       names=["protein", "variant_id", "chr", "end", "a2", "a1", "type", "beta", "P"])
print(f"The number of variants: {data.shape[0]}")

data["a1"] = data["a1"].replace("!", np.nan)
data["a2"] = data["a2"].replace("!", np.nan)
data["start"] = data["end"].astype(int) - 1

data_out = data[["chr", "start", "end", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]
print(data_out.head)

data_out.to_csv("/pQTLs/7_ferkingstad_2021/7_ferkingstad_2021_forLiftOver.txt", index=False, header=False, sep="\t", na_rep='NA')