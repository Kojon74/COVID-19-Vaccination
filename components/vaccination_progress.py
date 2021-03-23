import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go


class VaccinationProgress:
    def __init__(self, data):
        self.data = data

    def pred_full_vacc_fig(self, change_axis=False):
        """
        Returns line chart of cumulative vaccination percentage over time.
        """
        daily_vacc, dates = self.data.cum_vacc_percent()
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=dates, y=daily_vacc, line=dict(color=self.data.clrs["primary"])
            )
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Percentage of Population Vaccinated (%)",
            plot_bgcolor="lightgray",
            margin=dict(t=3, l=10, b=3, r=10),
        )
        if change_axis:
            fig.update_xaxes(range=[dates[0], self.data.sept])
            fig.update_yaxes(range=[0, 70])
        return fig

    def map_fig(self, tab="percent"):
        """
        Returns a map visually representing vaccination progress by country.
        Param:
            tab: Indicates what data to use (percent, total, or past week)
        """
        func_map_data = (
            self.data.top_countries_percent
            if tab == "percent"
            else self.data.top_countries_total
            if tab == "total"
            else self.data.top_countries_past_week
        )
        top_ctrys, log_ctrys = func_map_data(all_ctrys=True)
        percent = "%" if tab == "percent" else ""
        fig = go.Figure(
            data=go.Choropleth(
                # marker_line_color="lightgray",
                marker_line_width=0.1,
                locationmode="country names",
                locations=top_ctrys[0],
                z=top_ctrys[1],
                text=[
                    "{:,}".format(int(top_ctry[1])) + f"{percent}<br>{top_ctry[0]}"
                    for top_ctry in list(zip(*top_ctrys))
                ],
                hoverinfo="text",
                colorbar=dict(ticksuffix=percent),
                colorscale=[[0, self.data.clrs["secondary"]], [1, "black"]],
            ),
        )
        fig.update_geos(
            showframe=False,
            showcoastlines=False,
            projection_type="orthographic",
        )
        fig.update_layout(
            # dragmode=False,
            margin=dict(t=5, l=10, b=5, r=10),
        )
        return fig

    def vaccination_progress(self):
        """
        Returns a chart that visually represents the vaccination progress with a map or line chart.
        """
        fig = self.map_fig()
        return html.Div(
            className="pred-full-vacc-container-container",
            children=[
                html.Div(
                    className="pred-full-vacc-container card",
                    children=[
                        html.Div(
                            className="header-cont",
                            children=[
                                html.H3(
                                    className="header", children="Vaccination Progress"
                                ),
                                html.Div(
                                    className="toggle-cont",
                                    id="toggle-cont",
                                    children=[
                                        daq.ToggleSwitch(
                                            className="change-axis",
                                            id="change-axis",
                                            value=False,
                                        ),
                                        html.P("Zoom out"),
                                    ],
                                ),
                            ],
                        ),
                        dcc.Graph(
                            className="pred-full-vacc-graph",
                            id="pred-full-vacc",
                            figure=fig,
                            config=dict(scrollZoom=True),
                        ),
                    ],
                )
            ],
        )