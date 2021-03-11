import boto3
import pandas as pd
import numpy as np
import pypopulation
from datetime import datetime, timedelta
from io import StringIO


class VaccinationData:
    """
    Process data, 'backend' for Dash application.
    """

    def __init__(self):
        self.months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        self.connect_aws()
        self.set_cur_df("_raw_data.csv", True)
        self.globl_pop = 7_800_000_000
        self.herd_imm_thrsh = 70
        self.set_home()
        self.excld_ctry = [
            "Anguilla",
            "Guernsey",
            "Jersey",
            "Northern Cyprus",
            "Saint Helena",
        ]
        self.ctry_totl = self.country_totals(self.raw_df)
        self.num_ctrys = 195
        self.dropdown_options = self.dropdown_options()
        self.clrs = {
            "primary": "#87ceeb",
            "secondary": "#166484",
            "tertiary": "#fdfeff",
            "red": "#ff0000",
            "white": "#fff",
            "black": "#000",
        }

    def set_home(self):
        self.cur_ctry = "Global"
        self.set_cur_df()
        self.cur_iso = ""
        self.cur_pop = self.globl_pop
        self.cur_stats = self.get_stats()

    def connect_aws(self):
        """
        Connect to AWS using credentials and create a client to connect to S3.
        """
        self.client = boto3.client("s3")
        self.bucket_name = "covid-19-vaccination-data3"

    def get_auth(self):
        file_name = "auth.csv"
        object_key = file_name
        csv_obj = self.client.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj["Body"]
        csv_string = body.read().decode("utf-8")
        return pd.read_csv(StringIO(csv_string)).values[0]

    def set_cur_df(self, file_name=None, raw=False):
        """
        Set cur_df by reading csv file from S3 bucket.
        Params:
            file_name: file name of the csv file to read from, use current country file if none passed
            raw: Sets raw_df if true, cur_df if false
        """
        if file_name is None:
            file_name = f"{self.cur_ctry}_vaccinations.csv"
        object_key = file_name
        csv_obj = self.client.get_object(Bucket=self.bucket_name, Key=object_key)
        body = csv_obj["Body"]
        csv_string = body.read().decode("utf-8")
        if raw:
            self.raw_df = pd.read_csv(StringIO(csv_string))
        else:
            self.cur_df = pd.read_csv(StringIO(csv_string))

    def dropdown_options(self):
        """
        Gets a list of all the countries included in the dataset (for the dropdown).
        Excludes countries that we can't get population data for.
        Returns:
            dropdown_options: The list of countries that will be used in the dropdown
        """
        dropdown_options = [
            {"label": country, "value": f"{country},{iso_code}"}
            for country, iso_code in np.unique(
                self.raw_df[["country", "iso_code"]].dropna().values.astype("<U22"),
                axis=0,
            )
            if country not in self.excld_ctry
        ]
        dropdown_options.sort(key=lambda x: x["label"])
        global_option = {"label": "Global", "value": "Global,"}
        dropdown_options.insert(0, global_option)
        return dropdown_options

    def country_totals(self, cur_df):
        """
        Condense raw_df such that each column represents the total for a country.
        Params:
            cur_df: The df to condense
        Returns:
            ctry_totl: The df with each countries totals per row
        """
        ctry_totl = cur_df.groupby(["country", "iso_code"], as_index=False)[
            "daily_vaccinations"
        ].sum()  # Total vaccinations by country
        ctry_totl["iso_code"].fillna("", inplace=True)  # Clean dataset
        self.country_iso_dict = dict(zip(ctry_totl.country, ctry_totl.iso_code))
        return ctry_totl

    def get_stats(self):
        """
        Returns all the stats for the top cards.
        Returns:
            date: The most recent date in the dataframe
            vaccinated: Percentage of population vaccinated
            threshold: Percentage of people to be vaccinated for herd immunity
            today: Number of vaccinations today
        """
        date = datetime.strptime(self.most_recent_date(self.raw_df).strip(), "%Y-%m-%d")
        date = "{} {}".format(self.months[date.month - 1], date.day)
        self.cur_pop = (
            self.globl_pop
            if self.cur_ctry == "Global"
            else pypopulation.get_population(self.cur_iso)
        )
        vaccinated = (
            str(
                round(
                    self.cur_df["daily_vaccinations"].sum(axis=0) / self.cur_pop * 100,
                    1,
                )
            )
            + "%"
        )
        threshold = f"{self.herd_imm_thrsh}%"
        today = "{:,}".format(
            int(
                float(
                    self.cur_df.iloc[[-1]]["daily_vaccinations"].to_string(index=False)
                )
            )
        )
        return date, vaccinated, threshold, today

    def most_recent_date(self, cur_df):
        """
        Get the most recent date from cur_df.
        Params:
            cur_df: The df to get the most recent date from (must have a 'date' column)
        Returns:
            date: The most recent date in the cur_df
        """
        date = cur_df.iloc[[-1]]["date"].to_string(index=False).strip()
        return date

    def get_top_countries(self, ctrys):
        """
        Sort list of countries and get the top 10 and Canada.
        Params:
            ctrys: List of countries (Country name, measure to order by)
        Returns:
            top_ctrys: Top 10 countries ordered by percentage/total and Canada
        """
        ctrys.sort(key=lambda x: x[1], reverse=True)
        top_ctrys = ctrys[:10]
        can, i = next(((x, i) for i, x in enumerate(ctrys) if x[0] == "Canada"), None)
        can[0] = f"Canada #{i}"
        top_ctrys.append(can)  # Add Canada to end of
        top_ctrys.reverse()
        top_ctrys = list(zip(*top_ctrys))
        return top_ctrys

    def top_countries_percent(self):
        """
        Get top 10 countries with highest vaccination percentages.
        Returns:
            top_ctrys: The top 10 countries by percentage and Canada
            bar_clrs: List of colors for bar graph
        """
        pctg = []  # Percentage
        for i, ctry_row in self.ctry_totl.iterrows():
            c_ctry, c_iso, c_vacc = ctry_row
            pop = 0
            if c_iso != "":
                pop = pypopulation.get_population(c_iso)
            if pop:
                pctg.append([c_ctry, int(c_vacc / pop * 100)])
        top_ctrys = self.get_top_countries(pctg)
        num_over_thrsh = sum(1 for x in top_ctrys[1] if x > 70)
        bar_clrs = [self.clrs["primary"]] * num_over_thrsh + [self.clrs["white"]] * (
            11 - num_over_thrsh
        )
        bar_clrs[10] = self.clrs["red"]  # Make Canada bar red
        bar_clrs.reverse()
        return top_ctrys, bar_clrs

    def top_countries_total(self):
        """
        Get top 10 countrieswith highest total vaccinations.
        Returns:
            top_ctrys: The top 10 countries by total and Canada
            bar_clrs: List of colors for bar graph
        """
        totl = []
        for i, ctry_row in self.ctry_totl.iterrows():
            c_ctry, c_iso, c_vacc = ctry_row
            pop = 0
            if c_iso != "":
                pop = pypopulation.get_population(c_iso)
            if pop:
                totl.append([c_ctry, c_vacc])
        top_ctrys = self.get_top_countries(totl)
        bar_clrs = [self.clrs["primary"]] * 10 + [self.clrs["red"]]
        bar_clrs.reverse()
        return top_ctrys, bar_clrs

    def top_countries_past_week(self):
        """
        Get top 10 countries with highest total vaccinations in past week.
        Returns:
            top_ctrys: The top 10 countries by total in the past week and Canada
            bar_clrs: List of colors for bar graph
        """
        totl = []
        date = self.most_recent_date(self.raw_df)
        date_week_ago = datetime.strptime(date.strip(), "%Y-%m-%d") - timedelta(days=7)
        cur_df = self.raw_df.drop(
            self.raw_df[
                self.raw_df.date.map(lambda x: datetime.strptime(x, "%Y-%m-%d"))
                < date_week_ago
            ].index
        )
        ctry_totl = self.country_totals(cur_df)
        for i, ctry_row in ctry_totl.iterrows():
            c_ctry, c_iso, c_vacc = ctry_row
            pop = 0
            if c_iso != "":
                pop = pypopulation.get_population(c_iso)
            if pop:
                totl.append([c_ctry, c_vacc])
        top_ctrys = self.get_top_countries(totl)
        bar_clrs = [self.clrs["primary"]] * 10 + [self.clrs["red"]]
        bar_clrs.reverse()
        return top_ctrys, bar_clrs

    def past_week(self):
        """
        Return last 7 days of current dataframe (exclude most recent day on global dataframe).
        Returns:
            past_week: Data corrisponding to last 7 days of current dataframe
        """
        past_week = self.cur_df.tail(7) if self.cur_iso else self.cur_df.tail(8)[:-1]
        return past_week

    def cum_vacc_percent(self):
        """
        Returns cumulative percentage of population vaccinated over time.
        Returns:
            daily_vacc: Cumulative percentage of vaccinations per day
            dates: array of all dates in the current df
        """
        daily_vacc = (
            np.nancumsum(self.cur_df["daily_vaccinations"].values) / self.cur_pop * 100
        )
        dates = self.cur_df["date"].values
        return daily_vacc, dates