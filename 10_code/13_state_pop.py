############
# Imports
###########

import pandas as pd
import numpy as np
import janitor
import os

##############
# Read in Data
##############

df00_09 = pd.read_excel(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/statepop_00_09.xls",
    skipfooter=10,
    skiprows=1,
).rename_columns({"Unnamed: 0": "state"})

df10_20 = pd.read_excel(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/statepop_10_20.xlsx",
    skiprows=3,
    skipfooter=5,
).rename_columns({"Unnamed: 0": "state"})

##############
# Clean and merge
##############

df = pd.merge(df00_09, df10_20, on="state", validate="1:1")

df.state = df.state.str[1:]

df.columns = df.columns.astype("str")

df = df.melt(
    id_vars="state", value_vars=df.columns[1:], value_name="population", var_name="year"
)

df = df[(df.year != "Census") & (df.year != "Estimates Base")]
df.year = df.year.astype("int")

# Checks
assert len(df.year.unique()) * len(df.state.unique()) == len(df)
assert df.isna().any().any() == False

##############
# Save
##############

# Change file to local path

df.to_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/population_data_clean.csv",
    index=False,
)

print("done")
