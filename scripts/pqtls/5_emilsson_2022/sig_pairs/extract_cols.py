import pandas as pd
import os
import numpy as np

print("---Processing supplementary data 1 no conditional---")
supp_1_path = "/pQTLs/5_emilsson_2022/5_emilsson_2022_supp_1.xlsx"
supp_1 = pd.read_excel(supp_1_path, 
                       sheet_name="Data 1",
                       skiprows=2,
                       header=None,
                       usecols='B, C, D, E, F, I, P, R, S',
                       names=["variant_id", "chr", "pos", "a2", "a1", "protein", "beta", "P", "type"])
print(supp_1.shape)

supp_1_updated = supp_1[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]

supp_1_updated.loc[supp_1_updated["chr"].isin(["X", "x"]), "chr"] = 23
print(supp_1_updated.head())

supp_1_updated.to_csv("/pQTLs/5_emilsson_2022/5_emilsson_2022_noConditional_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')

print("---Processing supplementary data 1 conditional---")
# match the data on supp_2 with the data on supp_1 to get the cis/trans information
supp_1_path = "/pQTLs/5_emilsson_2022/5_emilsson_2022_supp_1.xlsx"
supp_2_path = "/pQTLs/5_emilsson_2022/5_emilsson_2022_supp_2.xlsx"

supp_1 = pd.read_excel(supp_1_path, 
                       sheet_name="Data 1",
                       skiprows=2,
                       header=None,
                       usecols='B, C, D, E, F, I, S',
                       names=["variant_id", "chr", "pos", "a2", "a1", "protein", "type"])

supp_2 = pd.read_excel(supp_2_path, 
                       sheet_name="Data 2",
                       skiprows=2,
                       header=None,
                       usecols='B, E, F, G, H, K, T, V',
                       names=["variant_id", "chr", "pos", "a2", "a1", "protein", "beta", "P"])

merged_data = supp_2.merge(supp_1, on=["variant_id", "chr", "pos", "a1", "a2", "protein"])

print(supp_1.shape)
print(supp_2.shape)
print(merged_data.shape)

updated_data = merged_data[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]

updated_data.loc[updated_data["chr"].isin(["X", "x"]), "chr"] = 23
print(updated_data.head())

updated_data.to_csv("/pQTLs/5_emilsson_2022/5_emilsson_2022_conditional_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')