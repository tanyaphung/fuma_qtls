import pandas as pd
import os
import numpy as np

supp_path = "/pQTLs/11_niu_2025/11_niu_2025_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="ST5",
                       skiprows=2,
                       header=None,
                       usecols='A, J, L, N', 
                       names=["id", "beta", "P", "phenotype"])

data[["chr", "pos", "a1", "a2"]] = data["id"].str.split("_", expand=True)
data["gene"] = data["phenotype"].str.split("_").str[1]

print(f"The number of variants: {data.shape[0]}")

# convert X to 23
data.loc[data["chr"].isin(["X", "x"]), "chr"] = 23

# add other columns as NA
data["variant_id"] = np.nan
data["type"] = np.nan

data_out = data[["chr", "pos", "a1", "a2", "variant_id", "gene", "type", "beta", "P"]]
print(data_out.head)
data_out.to_csv("/pQTLs/11_niu_2025/11_niu_2025_independent_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
