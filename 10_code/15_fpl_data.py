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

df = pd.read_stata(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/raw_fpl_data.dta",
)  # state federal poverty level

pop = pd.read_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/population_data_clean.csv",
)  # population of each state

##############
# Clean data
##############

# select one person per household and drop 1970s observations that I accidentally extracted, whoops
df.year = df.year.astype("int")
df = df[(df.year != 1970) & (df.pernum == 1)]
df = df[["year", "hhwt", "statefip", "poverty"]]  # subset

df.poverty.replace({0: np.nan}, inplace=True)  # replace NaNs

df = df.sort_values(["year", "statefip"]).reset_index(drop=True)

# Below 100% of federal poverty level? (FPL)
df["hhs_below_fpl"] = 0
df.loc[(df.poverty < 100), "below_fpl"] = 1

df["hhs_above_fpl"] = 0
df.loc[(df.poverty >= 100), "above_fpl"] = 1

df["below_fpl"] = df["hhs_below_fpl"] * df.hhwt
df["hhs_above_fpl"] = (
    df["hhs_above_fpl"] * df.hhwt
)  # Weight by # of households that are represented by this observation


##############
# Groupby and Merge
##############

# sum up households below povety line per state-year
df2 = (
    df.groupby(["year", "statefip"])
    .below_fpl.size()
    .to_frame("num_below_fpl")
    .reset_index()
    .rename_columns({"statefip": "state"})
)

# Merge in population

merged = pd.merge(
    df2, pop, on=["state", "year"], validate="1:1", how="outer", indicator=True
)

merged = merged[
    (merged.year != 2020) & (merged.state != "State not identified")
]  # no 2020 data available for poverty level, and one weird coding

assert (merged._merge == "both").all()
merged.drop("_merge", axis=1, inplace=True)

merged["percap_num_below_fpl"] = merged.num_below_fpl / merged.population


##############
# Save
##############

# Change file to local path

merged.to_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/fpl_rate_clean.csv",
    index=False,
)

print("done")
