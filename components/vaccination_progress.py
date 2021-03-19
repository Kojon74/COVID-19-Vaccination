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
        fig.add_trace(go.Scatter(x=dates, y=daily_vacc))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Percentage of Population Vaccinated (%)",
            margin=dict(t=3, l=10, b=3, r=10),
        )
        if change_axis:
            fig.update_xaxes(range=[dates[0], self.data.sept])
            fig.update_yaxes(range=[0, 70])
        return fig

    def pred_full_vacc(self):
        """
        Returns layout of predicted fuly vaccinated date chart.
        """
        fig = self.pred_full_vacc_fig()
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
                        ),
                    ],
                )
            ],
        )

    def map(self):
        return html.Div()

    def vaccination_progress(self, page):
        component = self.map() if page == "Global" else self.pred_full_vacc()
