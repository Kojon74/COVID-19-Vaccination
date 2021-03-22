import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go


class TopStats:
    def __init__(self, data):
        self.data = data

    def top_stat_content(self, stat, heading, class_id):
        """
        Returns layout for statistics contained within the top statistic cards.
        """
        return html.Div(
            children=[
                html.H2(className="stat", id=f"{class_id}-stat", children=stat),
                html.H6(className="header", id=f"{class_id}-header", children=heading),
            ],
        )

    def top_stat(self, stat, heading, class_id):
        """
        Returns layout for each statistic card.
        """
        return html.Div(
            className="top-stats card",
            children=[
                html.Button(
                    className="info-button",
                    id=f"{class_id}-info",
                    children=html.P(className="info", children="?"),
                ),
                html.Div(
                    id=class_id, children=self.top_stat_content(stat, heading, class_id)
                ),
            ],
        )

    def sparkline_fig(self):
        """
        Returns sparkline visualizing vaccination trend in the past week for the current country.
        """
        past_week = self.data.past_week()
        fig = go.Figure(
            go.Scatter(
                x=list(range(7)),
                y=past_week["daily_vaccinations"],
                marker=dict(size=1),
                line=dict(color=self.data.clrs["primary"]),
            )
        )
        fig.update_xaxes(visible=False, fixedrange=True)
        fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_layout(
            height=38,
            showlegend=False,
            plot_bgcolor="white",
            margin=dict(t=3, l=10, b=3, r=10),
        )
        return fig

    def sparkline_content(self, fig):
        """
        Returns layout for sparkline statistics contained within the top statistic cards.
        """
        return html.Div(
            children=[
                dcc.Graph(
                    id="sparkline-stat", figure=fig, config={"displayModeBar": False}
                ),
                html.H6(
                    className="header",
                    id="sparkline-header",
                    children="Daily Vaccinations Past 7 Days",
                ),
            ]
        )

    def sparkline(self):
        """
        Returns layout for sparkline card.
        """
        return html.Div(
            className="top-stats card",
            children=[
                html.Button(
                    className="info-button",
                    id="sparkline-info",
                    children=html.P(className="info", children="?"),
                ),
                html.Div(
                    id="sparkline",
                    children=self.sparkline_content(self.sparkline_fig()),
                ),
            ],
        )

    def top_stats(self):
        """
        Returns layout for top stats container.
        """
        return html.Div(
            className="top-stats-container",
            children=[
                self.top_stat("", "Latest Update", "update-date"),
                self.top_stat("", "Vaccinated", "vaccinated"),
                self.top_stat("", "Herd Immunity Threshold", "threshold"),
                self.top_stat("", "Vaccinnated Today", "today"),
                self.sparkline(),
            ],
        )