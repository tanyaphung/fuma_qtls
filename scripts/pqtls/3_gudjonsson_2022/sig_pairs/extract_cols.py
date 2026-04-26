import pandas as pd
import os
import numpy as np

supp_path = "/pQTLs/3_gudjonsson_2022/3_gudjonsson_2022_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="Data 3",
                       skiprows=4,
                       header=None,
                       usecols='D, F, G, H, J, K, M, O', 
                       names=["protein", "variant_id", "chr", "pos", "type", "a2", "beta", "P"])

print(f"The number of variants: {data.shape[0]}")

# convert X to 23
data.loc[data["chr"].isin(["X", "x"]), "chr"] = 23

# add columns
data["a1"] = np.nan

data_out = data[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]
print(data_out.head)
data_out.to_csv("/pQTLs/3_gudjonsson_2022/3_gudjonsson_2022_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
