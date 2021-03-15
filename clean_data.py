import pandas as pd
import os

os.rename("./data/country_vaccinations.csv", "./data/_raw_data.csv")
df = pd.read_csv("./data/_raw_data.csv")

countries = list(set(df["country"]))
dates = list(set(df["date"]))
dates.sort()

new_headers = ["date", "daily_vaccinations", "people_fully_vaccinated"]

for i, country in enumerate(countries):
    country_df = df[df["country"] == country][new_headers]
    country_df.to_csv(f"./data/{country}_vaccinations.csv", index=False, header=True)

data = []
for i, date in enumerate(dates):
    cur_dates_df = df[df["date"] == date][new_headers]
    sum_column = list(cur_dates_df.sum(axis=0, numeric_only=True))
    sum_column.insert(0, date)
    data.append(sum_column)
dates_df = pd.DataFrame(data, columns=new_headers)
dates_df.head

dates_df.to_csv("./data/Global_vaccinations.csv", index=False, header=True)
