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
            Output("country-rankings-cont", "style"),
            Output("update-date-stat", "children"),
            Output("vaccinated-stat", "children"),
            Output("threshold-stat", "children"),
            Output("today-stat", "children"),
            Output("sparkline-stat", "figure"),
            Output("percent-countries", "figure"),
            Output("pred-full-vacc", "figure"),
            Output("toggle-cont", "style"),
            Input("url", "pathname"),
            Input("change-axis", "value"),
            Input("country-rankings", "value"),
        )(self.change_page)

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

    def change_page(self, country, change_axis, tab):
        ctx = dash.callback_context
        if not ctx.triggered:
            input_id = None
        else:
            input_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if input_id == "change-axis":
            print("True")
            pred = self.vaccination_progress.pred_full_vacc_fig(change_axis)
            return [dash.no_update] * 7 + [pred, dash.no_update]

        if input_id == "country-rankings":
            percent = self.country_rankings.percent_rankings()
            total = self.country_rankings.total_rankings()
            past_week = self.country_rankings.past_week_rankings()
            tab_fig = (
                percent if tab == "percent" else total if tab == "total" else past_week
            )
            pred = self.vaccination_progress.map_fig(tab)
            return [dash.no_update] * 6 + [tab_fig, pred, dash.no_update]

        self.data.set_cur_df()
        style = "block" if self.data.cur_ctry == "Global" else "none"
        page = {"display": style}
        date, vaccinated, threshold, today = self.data.get_stats()
        sparkline = self.top_stats.sparkline_fig()
        print(self.data.cur_ctry)
        pred = (
            self.vaccination_progress.map_fig()
            if self.data.cur_ctry == "Global"
            else self.vaccination_progress.pred_full_vacc_fig()
        )
        show_toggle = "none" if self.data.cur_ctry == "Global" else "block"
        show_toggle = {"display": show_toggle}
        return (
            page,
            date,
            vaccinated,
            threshold,
            today,
            sparkline,
            dash.no_update,
            pred,
            show_toggle,
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