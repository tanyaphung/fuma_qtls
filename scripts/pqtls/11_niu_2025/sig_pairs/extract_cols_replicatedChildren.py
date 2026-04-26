import pandas as pd
import os
import numpy as np

supp_path = "/pQTLs/11_niu_2025/11_niu_2025_supp.xlsx"

print("---Replication in children---")
data = pd.read_excel(supp_path, 
                       sheet_name="ST13",
                       skiprows=2,
                       header=None,
                       usecols='A, F, K, N, P', 
                       names=["id", "gene", "replicated", "beta", "P"])

data[["chr", "pos", "a1", "a2"]] = data["id"].str.split("_", expand=True)
data["beta"] = data["beta"].str.replace("[", "")
data["beta"] = data["beta"].str.replace("]", "")
data["P"] = data["P"].str.replace("[", "")
data["P"] = data["P"].str.replace("]", "")

# convert X to 23
data.loc[data["chr"].isin(["X", "x"]), "chr"] = 23

# add other columns as NA
data["variant_id"] = np.nan
data["type"] = np.nan

print(f"The number of variants: {data.shape[0]}")

data_replicated = data[data["replicated"]=="exact"]
print(f"The number of replicated variants (exact): {data_replicated.shape[0]}")



data_replicated_out = data_replicated[["chr", "pos", "a1", "a2", "variant_id", "gene", "type", "beta", "P"]]
print(data_replicated_out.head)
data_replicated_out.to_csv("/pQTLs/11_niu_2025/11_niu_2025_replicatedChildren_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
