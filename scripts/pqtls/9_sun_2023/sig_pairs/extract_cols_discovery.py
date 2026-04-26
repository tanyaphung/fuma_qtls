import pandas as pd
import os
import numpy as np

# create:
# - `9_sun_2023_discovery`

supp_path = "/pQTLs/9_sun_2023/9_sun_2023_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="ST9",
                       skiprows=5,
                       header=None,
                       usecols='A, I, K, M, O, T', 
                       names=["id", "protein", "variant_id", "beta", "P", "type"])
print(f"The number of variants: {data.shape[0]}")

#extract chr, pos, a1, a2
data[["chr", "pos", "a1", "a2"]] = data["id"].str.split(":", expand=True).iloc[:, :4]

# convert X to 23
data.loc[data["chr"].isin(["X", "x"]), "chr"] = 23

data_out = data[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]
print(data_out.head)
data_out.to_csv("/pQTLs/9_sun_2023/9_sun_2023_discovery_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
