import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go


class CountryRankings:
    def __init__(self, data):
        self.data = data

    def percent_rankings(self):
        """
        Returns bar chart of top 10 countries with highest vaccination percentages.
        """
        top_ctrys, bar_clrs = self.data.top_countries_percent()
        fig = go.Figure(
            go.Bar(
                x=top_ctrys[1], y=top_ctrys[0], orientation="h", marker_color=bar_clrs
            ),
        )
        fig.update_layout(
            xaxis=dict(title="Percentage of Population Vaccinated", titlefont_size=12),
            yaxis=dict(tickfont_size=8),
            margin=dict(t=5, l=10, b=5, r=10),
        )
        fig.update_xaxes(range=[0, 100])
        fig.add_vline(
            x=self.data.herd_imm_thrsh,
            annotation={
                "text": "Herd Immunity Threshold",
                "textangle": 90,
                "yref": "paper",
                "yanchor": "bottom",
                "y": 0,
            },
        )
        return fig

    def total_rankings(self):
        """
        Returns bar chart of top 10 countries with highest total vaccinations.
        """
        top_ctrys, bar_clrs = self.data.top_countries_total()
        fig = go.Figure(
            go.Bar(
                x=top_ctrys[1], y=top_ctrys[0], orientation="h", marker_color=bar_clrs
            ),
        )
        fig.update_layout(
            xaxis=dict(title="Total number of Vaccinations", titlefont_size=12),
            yaxis=dict(tickfont_size=8),
            margin=dict(t=5, l=10, b=5, r=10),
        )
        return fig

    def past_week_rankings(self):
        """
        Returns bar chart of top 10 countries with highest total vaccinations in past week.
        """
        top_ctrys, bar_clrs = self.data.top_countries_past_week()
        fig = go.Figure(
            go.Bar(
                x=top_ctrys[1], y=top_ctrys[0], orientation="h", marker_color=bar_clrs
            ),
        )
        fig.update_layout(
            xaxis=dict(
                title="Total number of Vaccinations (Past Week)", titlefont_size=12
            ),
            yaxis=dict(tickfont_size=8),
            margin=dict(t=5, l=10, b=5, r=10),
        )
        return fig

    # def map_ranking(self):
    #     """"""
    #     top_ctrys, log_ctrys, _ = self.data.top_countries_percent(all_ctrys=True)
    #     fig = go.Figure(
    #         data=go.Choropleth(
    #             locationmode="country names",
    #             locations=top_ctrys[0],
    #             z=log_ctrys[1],
    #             text=top_ctrys[1],
    #             # colorbar_title="Covid-19 Vaccination (%)",
    #         )
    #     )
    #     fig.update_geos(projection_type="orthographic")
    #     fig.update_layout(
    #         margin=dict(t=5, l=10, b=5, r=10),
    #     )
    #     return fig

    def country_rankings(self):
        """
        Returns layout for country ranking chart.
        """
        fig = self.percent_rankings()
        return html.Div(
            className="percent-countries-container",
            children=[
                dcc.Tabs(
                    className="tabs",
                    parent_className="parent-tabs",
                    id="country-rankings",
                    value="percent",
                    children=[
                        dcc.Tab(
                            className="custom-tab",
                            selected_className="tab-selected",
                            label="Percentage",
                            value="percent",
                        ),
                        dcc.Tab(
                            className="custom-tab",
                            selected_className="tab-selected",
                            label="Total",
                            value="total",
                        ),
                        dcc.Tab(
                            className="custom-tab",
                            selected_className="tab-selected",
                            label="7 Days",
                            value="past-week",
                        ),
                        dcc.Tab(
                            className="custom-tab",
                            selected_className="tab-selected",
                            label="Map",
                            value="map",
                        ),
                    ],
                ),
                html.Div(
                    className="ranking-graph-container card",
                    children=[
                        html.H6(
                            className="header",
                            children=[
                                "Vaccination Progress Ranking",
                                html.Br(),
                                f"({self.data.num_ctrys} countries total)",
                            ],
                        ),
                        dcc.Graph(
                            className="percent-countries-graph",
                            id="percent-countries",
                            figure=fig,
                            config={"displayModeBar": False},
                        ),
                    ],
                ),
            ],
        )