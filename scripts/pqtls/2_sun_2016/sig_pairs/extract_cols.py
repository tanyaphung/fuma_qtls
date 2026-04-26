import pandas as pd
import os
import numpy as np

supp_path = "/pQTLs/2_sun_2016/2_sun_2016_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="Supplemental Table S4",
                       skiprows=2,
                       header=None,
                       usecols='A, C, D, E, L, Q', 
                       names=["protein", "variant_id", "chr", "pos", "P", "type"])

data = data[:527]
print(f"The number of variants: {data.shape[0]}")

# convert X to 23
data.loc[data["chr"].isin(["X", "x"]), "chr"] = 23

# add columns
data["a1"] = np.nan
data["a2"] = np.nan
data["beta"] = np.nan

# convert to int type
data['chr'] = data['chr'].astype(int)
data['pos'] = data['pos'].astype(int)

data_out = data[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]
print(data_out.head)
data_out.to_csv("/pQTLs/2_sun_2016/2_sun_2016_meta_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
