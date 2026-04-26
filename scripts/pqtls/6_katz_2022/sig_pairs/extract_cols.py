import pandas as pd
import os
import numpy as np

# create 2 sets
# - `6_katz_2021_discovery`
# - `6_katz_2021_meta`
supp_path = "/pQTLs/6_katz_2021/6_katz_2021_supp.xlsx"

# 6_katz_2021_discovery
print("---Processing for 6_katz_2022_discovery---")
set1 = pd.read_excel(supp_path, 
                       sheet_name="S3 - pQTLs",
                       skiprows=2,
                       header=None,
                       usecols='A, F, H, I, J, K, P, Z, AB',
                       names=["somamer_id", "chr", "chr:pos", "variant_id", "a2", "a1", "type", "beta", "P"])
print(f"The number of variants: {set1.shape[0]}")

#if the column "chr:pos" has NaN, drop it
set1 = set1.dropna(subset=["chr:pos"])
print(f"The number of variants after dropping NaN in the column chr:pos: {set1.shape[0]}")

#get position
set1["pos"] = set1["chr:pos"].str.split(":").str[1]

# get the protein
set1["protein"] = set1["somamer_id"].str.split(".").str[0]

set1_out = set1[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]

# convert X to 23
set1_out.loc[set1_out["chr"].isin(["X", "x"]), "chr"] = 23
print(set1_out.head)

set1_out.to_csv("/pQTLs/6_katz_2021/6_katz_2021_discovery_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')

# 6_katz_2021_meta
print("---Processing for 6_katz_2021_meta---")
#because in this sheet, the SOMA ID does not contain the gene/protein name, I am looking this up from the sheet S3 - pQTLs
somaid_lookup = pd.read_excel(supp_path, 
                       sheet_name="S3 - pQTLs",
                       skiprows=2,
                       header=None,
                       usecols='A, B',
                       names=["somamer_id", "soma_id"])
somaid_lookup = somaid_lookup.drop_duplicates(subset=["somamer_id"])
set2 = pd.read_excel(supp_path, 
                       sheet_name="S5-meta-analysis",
                       skiprows=2,
                       header=None,
                       usecols='A, D, I, H, F, G, P, S, U',
                       names=["soma_id", "chr", "a2", "a1", "variant_id", "chr:pos", "type", "beta", "P"])
print(f"The number of variants: {set2.shape[0]}")

set2 = set2.merge(somaid_lookup, on="soma_id", how="inner")
print(f"After merging to get the soma ID, the number of variants: {set2.shape[0]}")
print(set2.head)

#if the column "chr:pos" has NaN, drop it
set2 = set2.dropna(subset=["chr:pos"])
print(f"The number of variants after dropping NaN in the column chr:pos: {set2.shape[0]}")

#get position
set2["pos"] = set2["chr:pos"].str.split(":").str[1]

# get the protein
set2["protein"] = set2["somamer_id"].str.split(".").str[0]
set2_out = set2[["chr", "pos", "a1", "a2", "variant_id", "protein", "type", "beta", "P"]]

set2_out.loc[set2_out["chr"].isin(["X", "x"]), "chr"] = 23
print(set2_out.head)

set2_out.to_csv("/pQTLs/6_katz_2021/6_katz_2021_meta_fmt.txt", index=False, header=False, sep="\t", na_rep='NA')
