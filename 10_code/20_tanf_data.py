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

cols2skip = [1, 2, 3]  # previous 3 months (sheets are 15 months, we only want 12)
cols = [i for i in range(30) if i not in cols2skip]

# read in initial file to get States in empty in dataframe
df = pd.read_excel(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/ofa_data/family_sheet/2000_15months_tan.xls",
    sheet_name="Family",
    skiprows=3,
    usecols=cols,
)
df.dropna(inplace=True)
df = df[["State"]]

# Excel files with "Family" Sheet
filesnames = os.listdir(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/ofa_data/family_sheet"
)

for i in range(len(filesnames)):
    print(filesnames[i])

    df2 = pd.read_excel(
        f"/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/ofa_data/family_sheet/{filesnames[i]}",
        sheet_name="Family",
        skiprows=3,
        usecols=cols,
    )
    df2.replace("Montan", "Montana", inplace=True)  # corrects file-specific issue
    df2.replace("Missouri ", "Missouri", inplace=True)  # corrects file-specific issue
    df = pd.merge(df, df2, on="State", how="outer", validate="1:1")
    df.dropna(inplace=True)

# Excel files with "TFam" sheet

filesnames = os.listdir(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/ofa_data/tfam_sheet"
)

for i in range(len(filesnames)):
    print(filesnames[i])
    df2 = pd.read_excel(
        f"/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/ofa_data/tfam_sheet/{filesnames[i]}",
        sheet_name="tfam",
        skiprows=3,
        usecols=cols,
    )
    df2.replace("District of Columbia", "Dist. of Col.", inplace=True)
    df2.replace("District of Columbia*", "Dist. of Col.", inplace=True)
    df = pd.merge(df, df2, on="State", how="outer", validate="1:1")
    df.dropna(inplace=True)

df.replace("Dist. of Col.", "District of Columbia", inplace=True)

assert len(df.State.unique() == 52)  # includes DC and PR

# Population Data
pop = pd.read_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/population_data_clean.csv",
)  # population of each state

##############
# Format and Clean
##############

df.columns = df.columns.astype(str)

df = df[
    df.columns.drop(list(df.filter(regex="\n")))
]  # Drop columns with "Average" and "Total" and stuff

df = df[(df.State != "Puerto Rico") & (df.State != "Virgin Islands")]


# Format Long to Wide
df = df.melt(
    id_vars="State",
    value_vars=df.columns[~df.columns.str.contains("State")],
    value_name="tanf_fams",
    var_name="date",
)


# Make Month/Year columns in case needed
df["year"] = pd.DatetimeIndex(df["date"]).year
df["month"] = pd.DatetimeIndex(df["date"]).month

# Reorder and sort
df = df.clean_names()
df.tanf_fams.replace("*", np.nan, inplace=True)
df = df[["state", "date", "year", "month", "tanf_fams"]].sort_values(
    ["state", "year", "month"]
)


######################
# Merge in Population
#######################

merged = pd.merge(
    df, pop, on=["state", "year"], validate="m:1", how="outer", indicator=True
)

merged = merged[
    (merged.state != "Puerto Rico") & (merged.state != "Virgin Islands")
]  # no 2020 data available for poverty level, and remove PR

assert len(
    merged[merged._merge == "both"].state.unique() == 1
)  # just 2020 didn't match up, since no population data for 2020
merged.drop("_merge", axis=1, inplace=True)

# Per Capita
merged.tanf_fams = merged.tanf_fams.astype("float")

merged["percap_tanf_fams"] = merged.tanf_fams / merged.population


##############
# Save
##############

# Change file to local path

merged.to_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/tanf_data_clean.csv",
    index=False,
)

print("done")
