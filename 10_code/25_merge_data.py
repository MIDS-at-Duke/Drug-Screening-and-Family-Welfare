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

unemp = pd.read_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/unemployment_rate_clean.csv"
)

fpl = pd.read_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/fpl_rate_clean.csv"
)

tanf = pd.read_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/tanf_data_clean.csv",
)

drug_states = pd.read_excel(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/drug_test_years.xlsx",
    usecols=[0, 1, 2],
).clean_names()


##############
# Merge
##############

df = pd.merge(
    unemp, fpl, on=["state", "year"], how="outer", validate="m:1", indicator=True
)
assert len(
    df[df._merge != "both"].year.unique() == 1
)  # just 2020 didn't merge since no 2020 unemployment data
df.drop("_merge", axis=1, inplace=True)

df = pd.merge(
    df, tanf, on=["state", "month", "year"], how="outer", validate="1:1", indicator=True
)
assert len(
    df[df._merge != "both"].year.unique() == 1
)  # just 2020 didn't merge since no 2020 unemployment data
df.drop("_merge", axis=1, inplace=True)

df = df.loc[:, ~df.columns.str.endswith("_x")]
df.rename({"date_y": "datetime", "population_y": "population"}, axis=1, inplace=True)
df.reset_index()

################################
# Indicate if Drug Policy State
#################################

# Convert Month and Year Columns to DateTime
cols = ["year", "month"]

drug_states["date"] = drug_states[cols].apply(
    lambda x: "-".join(x.values.astype(str)), axis="columns"
)
drug_states["datetime"] = pd.to_datetime(drug_states["date"])


df = df[df.datetime.notna()]
df["datetime"] = pd.to_datetime(df["datetime"])

# Indicator
drug_law_states = drug_states.state.unique()
drug_law_years = drug_states.datetime.tolist()

df["drug_law"] = 0

for i in range(len(drug_law_states)):
    df.loc[
        (df.state == drug_law_states[i]) & (df.datetime >= drug_law_years[i]),
        "drug_law",
    ] = 1

# Distance from Cutoff
df["days_from_policy"] = np.nan

for i in range(len(drug_states)):
    date = drug_states.datetime[i]
    print(date)
    df.loc[
        (df.datetime >= drug_states.datetime[i]) & (df.state == drug_states.state[i]),
        "days_from_policy",
    ] = (
        df.datetime - date
    )


# Drop 2000 and 2020
df = df[(df.year != 2000) & (df.year != 2020)]

# Reorder Columns
df = df[
    [
        "state",
        "year",
        "month",
        "datetime",
        "population",
        "num_below_fpl",
        "tanf_fams",
        "percap_num_below_fpl",
        "unemp_rate",
        "percap_tanf_fams",
        "drug_law",
        "days_from_policy",
    ]
]


################################
# Save
#################################

df.to_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/final_dataset_clean.csv",
    index=False,
)

print("done")
