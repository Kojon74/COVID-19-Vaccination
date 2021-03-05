import math
import pandas as pd
import numpy as np
import pypopulation

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

from vaccination_data import VaccinationData

external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
]


df = pd.read_csv("./data/Global_vaccinations.csv")

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)

application = app.server
data = VaccinationData()


def navbar():
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


def percent_rankings(cur_df):
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


def total_rankings(cur_df):
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


def past_week_rankings(cur_df):
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
    cur_df = pd.read_csv("./data/_raw_data.csv")
    fig = percent_rankings(cur_df)
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
    return html.Div(
        children=[
            html.H2(className="stat", id=f"{class_id}-stat", children=stat),
            html.H6(className="header", id=f"{class_id}-header", children=heading),
        ]
    )


def top_stat(stat, heading, class_id):
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
    Draw sparkline.
    """
    past_week = data.past_week()
    fig = go.Figure(
        go.Scatter(
            x=np.arange(7),
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
    return html.Div(
        className="top-stats card",
        children=[
            html.Button(
                className="info-button",
                id=f"sparkline-info",
                children=html.P(className="info", children="?"),
            ),
            html.Div(id="sparkline", children=sparkline_content(sparkline_fig())),
        ],
    )


def top_stats():
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


def pred_full_vacc_fig():
    daily_vacc, dates = data.cum_vacc_percent()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=daily_vacc))
    fig.update_layout(
        title="Predicted Fully Vaccinated Date",
        xaxis_title="Date",
        yaxis_title="Percentage of Population Vaccinated (%)",
    )
    return fig


def pred_full_vacc():
    fig = pred_full_vacc_fig()
    return html.Div(
        className="pred-full-vacc-container",
        children=[
            dcc.Graph(
                className="pred-full-vacc-graph card", id="pred-full-vacc", figure=fig
            ),
        ],
    )


def right():
    return html.Div(
        className="right",
        children=[top_stats(), pred_full_vacc()],
    )


def homepage():
    return html.Div(
        className="country-page",
        children=[country_rankings(), right()],
    )


def countrypage(country):
    return html.Div(className="country-page", children=[right()])


def dashboard():
    return html.Div(className="dashboard", id="dashboard", children=[homepage()])


app.layout = html.Div(children=[navbar(), dashboard()])


@app.callback(
    Output(component_id="dashboard", component_property="children"),
    Output(component_id="update-date-stat", component_property="children"),
    Output(component_id="vaccinated-stat", component_property="children"),
    Output(component_id="threshold-stat", component_property="children"),
    Output(component_id="today-stat", component_property="children"),
    Output(component_id="sparkline-stat", component_property="figure"),
    Output(component_id="pred-full-vacc", component_property="figure"),
    Output(component_id="nav-header", component_property="n_clicks"),
    Output(component_id="region", component_property="value"),
    Input(component_id="region", component_property="value"),
    Input(component_id="nav-header", component_property="n_clicks"),
)
def change_page(dropdown_value, n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        input_id = None
    else:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id and input_id == "nav-header":  # If home button clicked
        data.cur_ctry, data.cur_iso = "Global", None
    elif input_id:  # If dropdown clicked
        data.cur_ctry, data.cur_iso = dropdown_value.split(",")
    data.cur_df = pd.read_csv(f"./data/{data.cur_ctry}_vaccinations.csv")
    page = homepage() if data.cur_ctry == "Global" else countrypage(data.cur_ctry)
    date, vaccinated, threshold, today = data.get_stats()
    sparkline = sparkline_fig()
    pred = pred_full_vacc_fig()
    new_dd_val = f"{data.cur_ctry},{data.cur_iso}"
    return page, date, vaccinated, threshold, today, sparkline, pred, 0, new_dd_val


@app.callback(
    Output(component_id="percent-countries", component_property="figure"),
    Input(component_id="country-rankings", component_property="value"),
    prevent_initial_call=True,
)
def switch_ranking_graph(tab):
    cur_df = pd.read_csv("./data/_raw_data.csv")
    percent = percent_rankings(cur_df)
    total = total_rankings(cur_df)
    past_week = past_week_rankings(cur_df)
    return percent if tab == "percent" else total if tab == "total" else past_week


@app.callback(
    Output(component_id="update-date", component_property="children"),
    Output(component_id="vaccinated", component_property="children"),
    Output(component_id="threshold", component_property="children"),
    Output(component_id="today", component_property="children"),
    Output(component_id="sparkline", component_property="children"),
    Input(component_id="update-date-info", component_property="n_clicks"),
    Input(component_id="vaccinated-info", component_property="n_clicks"),
    Input(component_id="threshold-info", component_property="n_clicks"),
    Input(component_id="today-info", component_property="n_clicks"),
    Input(component_id="sparkline-info", component_property="n_clicks"),
    State(component_id="update-date", component_property="children"),
    State(component_id="vaccinated", component_property="children"),
    State(component_id="threshold", component_property="children"),
    State(component_id="today", component_property="children"),
    State(component_id="sparkline", component_property="children"),
    prevent_initial_call=True,
)
def show_info(n0, n1, n2, n3, n4, s0, s1, s2, s3, s4):
    num_clicks = [n0, n1, n2, n3, n4]
    cur_states = [s0, s1, s2, s3, s4]
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
    print(index, num_clicks[index])
    if num_clicks[index] % 2:
        if index == 4:
            cur_states[index] = sparkline_content(sparkline_fig(), infos[index])
        else:
            cur_states[index] = top_stat_content("", infos[index], input_ids[index])
        return cur_states[0], cur_states[1], cur_states[2], cur_states[3], cur_states[4]
    else:
        if index == 4:
            cur_states[index] = sparkline_content(sparkline_fig())
        else:
            cur_states[index] = top_stat_content(
                data.cur_stats[index], headers[index], input_ids[index]
            )
        return cur_states[0], cur_states[1], cur_states[2], cur_states[3], cur_states[4]


if __name__ == "__main__":
    # app.run_server(debug=True)
    application.run(debug=True, port=8080)