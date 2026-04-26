import pandas as pd
import os
import numpy as np

# create:
# - `9_sun_2023_CSA`
# - `9_sun_2023_AFR`
# - `9_sun_2023_EAS`
# - `9_sun_2023_MID`
# - `9_sun_2023_AMR`

supp_path = "/pQTLs/9_sun_2023/9_sun_2023_supp.xlsx"

data = pd.read_excel(supp_path, 
                       sheet_name="ST11",
                       skiprows=6,
                       header=None,
                       usecols='A, H, J, K, M, O, Q', 
                       names=["id", "protein", "variant_id", "ancestry", "beta", "P", "type"])

populations = ["CSA", "AFR", "EAS", "MID", "AMR"]

for pop in populations:
    pop_data = data[data["ancestry"] == pop]
    print(f"The number of variants in ancestry {pop}: {pop_data.shape[0]}")
    print(pop_data.head)

    #extract chr, pos, a1, a2
    pop_data[["chr", "pos", "a1", "a2"]] = pop_data["id"].str.split(":", expand=True).iloc[:, :4]

    # convert X to 23
    pop_data.loc[pop_data["chr"].isin(["X", "x"]), "chr"] = 23

    pop_data_out = pop_data[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]
    print(pop_data_out.head)
    pop_data_out.to_csv(os.path.join("/pQTLs/9_sun_2023/9_sun_2023_" + pop + "_fmt.txt"), index=False, header=False, sep="\t", na_rep='NA')

