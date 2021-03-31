############
# Imports
###########

import pandas as pd
import numpy as np
import janitor

##############
# Read in Data
##############

df = pd.read_csv(
    "/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/00_source_data/unemployment_data/monthly_state_unemployment_data.txt",
    sep="\t",
)

df = df.clean_names().remove_empty()
df = df[df.series_id.str.endswith("03")]  # 03 codes for unemployment rate

codes = pd.read_csv("https://download.bls.gov/pub/time.series/la/la.area", sep="\t")
codes = codes[codes.area_code.str.startswith("ST")]  # codes for state level
codes["area_code"] = codes["area_code"].str[0:4]  # truncate code to relevant portion

area_codes = codes.area_code.to_list()
area_text = codes.area_text.to_list()
code_dict = {
    area_codes[i]: area_text[i] for i in range(len(area_codes))
}  # make dictionary of codes and states

df["series_id"] = df["series_id"].str[3:7]  # match to dictionary

df["state"] = df.series_id.replace(code_dict)  # add states instead of codes

##############
# Format Data: Long
##############

value_variables = df.columns[df.columns.str.contains("2")]

# Melt
df = pd.melt(
    df,
    id_vars=["state"],
    value_vars=value_variables,
    var_name="date",
    value_name="unemp_rate",
)

# Put date column in to DateTime
df[["month", "year"]] = df.date.str.split("_", expand=True)
df['date'] = pd.to_datetime(df['month'].astype(str)  + df['year'], format='%b%Y')

#drop anything after 2020
df.year = df.year.astype(int)
df = df[df.year<=2020]

##############
# Other Cleaning
##############

# Remove (r) from unemployment rate

df["unemp_rate"] = df["unemp_rate"].str[0:3]

df["unemp_rate"] = pd.to_numeric(df.unemp_rate, errors='coerce') # make number not string

# Drop NA and extra columns

df.dropna(inplace=True)
df = df[['state', 'date', 'unemp_rate']]

##############
#Save
##############

df.to_csv("/Users/samsloate/Desktop/720_Data_Science/Policy-Stats-Team/20_intermediate_data/unemployment_rate_clean.csv",
    index=False,
)

print("done")
