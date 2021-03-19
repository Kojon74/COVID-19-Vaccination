from datetime import datetime, timedelta

import dash
from dash.dependencies import Input, Output, State

from .navbar import Navbar
from .dashboard import Dashboard
from .country_rankings import CountryRankings
from .top_stats import TopStats
from .vaccination_progress import VaccinationProgress


class Callbacks:
    def __init__(self, app, data):
        self.app = app
        self.data = data

        self.navbar = Navbar(data)
        self.dashboard = Dashboard(data)
        self.country_rankings = CountryRankings(data)
        self.top_stats = TopStats(data)
        self.vaccination_progress = VaccinationProgress(data)

        app.callback(
            Output("url", "pathname"),
            Output("region", "value"),
            Input("region", "value"),
            Input("nav-header", "n_clicks"),
        )(self.change_url)

        app.callback(
            Output("dashboard", "children"),
            Output("update-date-stat", "children"),
            Output("vaccinated-stat", "children"),
            Output("threshold-stat", "children"),
            Output("today-stat", "children"),
            Output("sparkline-stat", "figure"),
            Output("pred-full-vacc", "figure"),
            Input("url", "pathname"),
            Input("change-axis", "value"),
        )(self.change_page)

        app.callback(
            Output("percent-countries", "figure"),
            Input("country-rankings", "value"),
            prevent_initial_call=True,
        )(self.switch_ranking_graph)

        app.callback(
            Output("update-date-stat", "style"),
            Output("vaccinated-stat", "style"),
            Output("threshold-stat", "style"),
            Output("today-stat", "style"),
            Output("sparkline-stat", "style"),
            Output("update-date-header", "children"),
            Output("vaccinated-header", "children"),
            Output("threshold-header", "children"),
            Output("today-header", "children"),
            Output("sparkline-header", "children"),
            Input("update-date-info", "n_clicks"),
            Input("vaccinated-info", "n_clicks"),
            Input("threshold-info", "n_clicks"),
            Input("today-info", "n_clicks"),
            Input("sparkline-info", "n_clicks"),
            prevent_initial_call=True,
        )(self.show_info)

    def change_url(self, dropdown_value, n_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            input_id = None
        else:
            input_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if input_id and input_id == "nav-header":  # If home button clicked
            self.data.cur_ctry, self.data.cur_iso = "Global", ""
        elif input_id:  # If dropdown clicked
            self.data.cur_ctry, self.data.cur_iso = dropdown_value.split(",")
        new_dd_val = f"{self.data.cur_ctry},{self.data.cur_iso}"
        return self.data.cur_ctry, new_dd_val

    def change_page(self, country, change_axis):
        ctx = dash.callback_context
        if not ctx.triggered:
            input_id = None
        else:
            input_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if input_id == "change-axis":
            pred = self.vaccination_progress.pred_full_vacc_fig(change_axis)
            return [dash.no_update] * 6 + [pred]
        self.data.set_cur_df()
        page = (
            self.dashboard.homepage()
            if self.data.cur_ctry == "Global"
            else self.dashboard.countrypage(self.data.cur_ctry)
        )
        date, vaccinated, threshold, today = self.data.get_stats()
        sparkline = self.top_stats.sparkline_fig()
        pred = self.vaccination_progress.pred_full_vacc_fig()
        return page, date, vaccinated, threshold, today, sparkline, pred

    def switch_ranking_graph(self, tab):
        """
        Return the correct figure based on the current tab.
        """
        percent = self.country_rankings.percent_rankings()
        total = self.country_rankings.total_rankings()
        past_week = self.country_rankings.past_week_rankings()
        # map_p = self.country_rankings.map_ranking()
        return (
            percent
            if tab == "percent"
            else total
            if tab == "total"
            else past_week
            # if tab == "past-week"
            # else map_p
        )

    def show_info(self, n0, n1, n2, n3, n4):
        """
        Handles the clicking of the info button on the top stats cards.
        """
        num_clicks = [n0, n1, n2, n3, n4]
        state_stats = [dash.no_update] * len(num_clicks)
        state_header = [dash.no_update] * len(num_clicks)
        input_ids = ["update-date", "vaccinated", "threshold", "today", "sparkline"]
        infos = [
            "Data is delayed by a couple days.",
            "Percentage of total population vaccinated.",
            "Rough estimate of number of people needed to be vaccinated.",
            f"Number of people vaccinated {self.data.most_recent_date(self.data.raw_df)}",
            "Total vaccinations from past 7 days",
        ]
        headers = [
            "Latest Update",
            "Vaccinated",
            "Herd Immunity Threshold",
            "Vaccinated Today",
            "Daily Vaccinations Past 7 Days",
        ]
        ctx = dash.callback_context
        index = input_ids.index(ctx.triggered[0]["prop_id"].split(".")[0][:-5])
        style = "none" if num_clicks[index] % 2 else "block"
        desc = infos if num_clicks[index] % 2 else headers
        state_stats[index] = {"display": style}
        state_header[index] = desc[index]
        return state_stats + state_header