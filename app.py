from datetime import datetime, timedelta

import dash
import dash_auth
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from vaccination_data import VaccinationData

data = VaccinationData()

auth = data.get_auth()
VALID_USERNAME_PASSWORD_PAIRS = {auth[0]: auth[1]}

external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

server = app.server


def navbar():
    """
    Layout for navbar.
    """
    return html.Div(
        className="nav",
        children=[
            html.Button(
                className="header",
                id="nav-header",
                children="Covid-19 Vaccination Progress",
                n_clicks=0,
            ),
            dcc.Dropdown(
                className="dropdown",
                id="region",
                options=data.dropdown_options,
                value="Global,",
                placeholder="Select Country",
            ),
        ],
    )


def percent_rankings():
    """
    Returns bar chart of top 10 countries with highest vaccination percentages.
    """
    top_ctrys, bar_clrs = data.top_countries_percent()
    fig = go.Figure(
        go.Bar(x=top_ctrys[1], y=top_ctrys[0], orientation="h", marker_color=bar_clrs),
    )
    fig.update_layout(
        xaxis=dict(title="Percentage of Population Vaccinated", titlefont_size=12),
        yaxis=dict(tickfont_size=8),
        margin=dict(t=5, l=10, b=5, r=10),
    )
    fig.update_xaxes(range=[0, 100])
    fig.add_vline(
        x=data.herd_imm_thrsh,
        annotation={
            "text": "Herd Immunity Threshold",
            "textangle": 90,
            "yref": "paper",
            "yanchor": "bottom",
            "y": 0,
        },
    )
    return fig


def total_rankings():
    """
    Returns bar chart of top 10 countries with highest total vaccinations.
    """
    top_ctrys, bar_clrs = data.top_countries_total()
    fig = go.Figure(
        go.Bar(x=top_ctrys[1], y=top_ctrys[0], orientation="h", marker_color=bar_clrs),
    )
    fig.update_layout(
        xaxis=dict(title="Total number of Vaccinations", titlefont_size=12),
        yaxis=dict(tickfont_size=8),
        margin=dict(t=5, l=10, b=5, r=10),
    )
    return fig


def past_week_rankings():
    """
    Returns bar chart of top 10 countries with highest total vaccinations in past week.
    """
    top_ctrys, bar_clrs = data.top_countries_past_week()
    fig = go.Figure(
        go.Bar(x=top_ctrys[1], y=top_ctrys[0], orientation="h", marker_color=bar_clrs),
    )
    fig.update_layout(
        xaxis=dict(title="Total number of Vaccinations (Past Week)", titlefont_size=12),
        yaxis=dict(tickfont_size=8),
        margin=dict(t=5, l=10, b=5, r=10),
    )
    return fig


def country_rankings():
    """
    Returns layout for country ranking chart.
    """
    fig = percent_rankings()
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
                        label="Past Week",
                        value="past-week",
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
                            f"({data.num_ctrys} countries total)",
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


def top_stat_content(stat, heading, class_id):
    """
    Returns layout for statistics contained within the top statistic cards.
    """
    return html.Div(
        children=[
            html.H2(className="stat", id=f"{class_id}-stat", children=stat),
            html.H6(className="header", id=f"{class_id}-header", children=heading),
        ],
    )


def top_stat(stat, heading, class_id):
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
            html.Div(id=class_id, children=top_stat_content(stat, heading, class_id)),
        ],
    )


def sparkline_fig():
    """
    Returns sparkline visualizing vaccination trend in the past week for the current country.
    """
    past_week = data.past_week()
    fig = go.Figure(
        go.Scatter(
            x=list(range(7)),
            y=past_week["daily_vaccinations"],
            marker=dict(size=1),
            line=dict(color="#87ceeb"),
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


def sparkline_content(fig):
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


def sparkline():
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
            html.Div(id="sparkline", children=sparkline_content(sparkline_fig())),
        ],
    )


def top_stats():
    """
    Returns layout for top stats container.
    """
    return html.Div(
        className="top-stats-container",
        children=[
            top_stat("", "Latest Update", "update-date"),
            top_stat("", "Vaccinated", "vaccinated"),
            top_stat("", "Herd Immunity Threshold", "threshold"),
            top_stat("", "Vaccinnated Today", "today"),
            sparkline(),
        ],
    )


def pred_full_vacc_fig(change_axis=False):
    """
    Returns line chart of cumulative vaccination percentage over time.
    """
    daily_vacc, dates = data.cum_vacc_percent()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=daily_vacc))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Percentage of Population Vaccinated (%)",
        margin=dict(t=3, l=10, b=3, r=10),
    )
    if change_axis:
        fig.update_xaxes(range=[dates[0], datetime(2021, 9, 1)])
        fig.update_yaxes(range=[0, 70])
    return fig


def pred_full_vacc():
    """
    Returns layout of predicted fuly vaccinated date chart.
    """
    fig = pred_full_vacc_fig()
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


def right():
    """
    Returns layout for right hand side component.
    """
    return html.Div(
        className="right",
        children=[top_stats(), pred_full_vacc()],
    )


def homepage():
    """
    Returns layout for homepage.
    """
    return html.Div(
        className="country-page",
        children=[country_rankings(), right()],
    )


def countrypage(country):
    """
    Returns layout for specific coutry's page.
    """
    return html.Div(className="country-page", children=[right()])


def dashboard():
    """
    Returns top-level layout
    """
    return html.Div(className="dashboard", id="dashboard", children=[homepage()])


app.layout = html.Div(
    children=[dcc.Location(id="url", refresh=False), navbar(), dashboard()]
)


@app.callback(
    Output("url", "pathname"),
    Output("region", "value"),
    Input("region", "value"),
    Input("nav-header", "n_clicks"),
)
def change_url(dropdown_value, n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        input_id = None
    else:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id and input_id == "nav-header":  # If home button clicked
        data.cur_ctry, data.cur_iso = "Global", ""
    elif input_id:  # If dropdown clicked
        data.cur_ctry, data.cur_iso = dropdown_value.split(",")
    new_dd_val = f"{data.cur_ctry},{data.cur_iso}"
    return data.cur_ctry, new_dd_val


@app.callback(
    Output("dashboard", "children"),
    Output("update-date-stat", "children"),
    Output("vaccinated-stat", "children"),
    Output("threshold-stat", "children"),
    Output("today-stat", "children"),
    Output("sparkline-stat", "figure"),
    Output("pred-full-vacc", "figure"),
    Input("url", "pathname"),
    Input("change-axis", "value"),
)
def change_page(country, change_axis):
    ctx = dash.callback_context
    if not ctx.triggered:
        input_id = None
    else:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "change-axis":
        pred = pred_full_vacc_fig(change_axis)
        return [dash.no_update] * 6 + [pred]
    data.set_cur_df()
    page = homepage() if data.cur_ctry == "Global" else countrypage(data.cur_ctry)
    date, vaccinated, threshold, today = data.get_stats()
    sparkline = sparkline_fig()
    pred = pred_full_vacc_fig()
    return page, date, vaccinated, threshold, today, sparkline, pred


@app.callback(
    Output("percent-countries", "figure"),
    Input("country-rankings", "value"),
    prevent_initial_call=True,
)
def switch_ranking_graph(tab):
    """
    Return the correct figure based on the current tab.
    """
    percent = percent_rankings()
    total = total_rankings()
    past_week = past_week_rankings()
    return percent if tab == "percent" else total if tab == "total" else past_week


@app.callback(
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
)
def show_info(n0, n1, n2, n3, n4):
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
        f"Number of people vaccinated {data.most_recent_date(data.raw_df)}",
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


if __name__ == "__main__":
    app.run_server(debug=True)