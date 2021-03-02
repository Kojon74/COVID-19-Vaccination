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

external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
]
colors = {
    "primary": "#87ceeb",
    "secondary": "#166484",
    "tertiary": "#fdfeff",
    "white": "#fff",
    "black": "#000",
}
months = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "Jun",
    "07": "Jul",
    "08": "Aug",
    "09": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}
global_pop = 7_800_000_000
exclude_countries = [
    "Anguilla",
    "Guernsey",
    "Jersey",
    "Northern Cyprus",
    "Saint Helena",
]

global_df = pd.read_csv("./data/_raw_data.csv")
df = pd.read_csv("./data/Global_vaccinations.csv")

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)

server = app.server


def navbar():
    dropdown_options = [
        {"label": country, "value": f"{country},{iso_code}"}
        for country, iso_code in np.unique(
            global_df[["country", "iso_code"]].dropna().values.astype("<U22"), axis=0
        )
        if country not in exclude_countries
    ]
    dropdown_options.sort(key=lambda x: x["label"])
    global_option = {"label": "Global", "value": "Global,"}
    dropdown_options.insert(0, global_option)
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
                options=dropdown_options,
                value="Global,",
            ),
        ],
    )


def percent_rankings(cur_df):
    cur_df = cur_df.groupby(["country", "iso_code"], as_index=False)[
        "daily_vaccinations"
    ].sum()
    cur_df["iso_code"].fillna("", inplace=True)
    percentage = []
    for i, row in cur_df.iterrows():
        population = 0
        if row["iso_code"] != "":
            population = pypopulation.get_population(row["iso_code"])
        if population:
            percentage.append(
                [
                    row["country"],
                    int(row["daily_vaccinations"] / population * 100),
                ],
            )
    num_countries = len(percentage)
    percentage.sort(key=lambda x: x[1], reverse=True)
    top_countries = percentage[:10]
    canada, i = next(
        ((x, i) for i, x in enumerate(percentage) if x[0] == "Canada"), None
    )
    canada[0] = f"Canada #{i}"
    top_countries.append(canada)
    top_countries.reverse()
    flipped = list(zip(*top_countries))
    num_over_threshold = sum(1 for x in top_countries if x[1] > 70)
    bar_colors = [colors["primary"]] * num_over_threshold + [colors["white"]] * (
        11 - num_over_threshold
    )
    bar_colors[10] = "#ff0000"
    bar_colors.reverse()
    fig = go.Figure(
        go.Bar(x=flipped[1], y=flipped[0], orientation="h", marker_color=bar_colors),
    )
    fig.update_layout(
        title=f"Vaccination Progress Ranking ({num_countries} total)",
        xaxis=dict(title="Percentage of Population Vaccinated"),
        yaxis=dict(tickfont_size=10),
        margin=dict(t=30, l=10, b=5, r=10),
    )
    fig.update_xaxes(range=[0, 100])
    fig.add_vline(
        x=70,
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
    cur_df = cur_df.groupby(["country", "iso_code"], as_index=False)[
        "daily_vaccinations"
    ].sum()
    cur_df["iso_code"].fillna("", inplace=True)
    percentage = []
    for i, row in cur_df.iterrows():
        population = 0
        if row["iso_code"] != "":
            population = pypopulation.get_population(row["iso_code"])
        if population:
            percentage.append(
                [
                    row["country"],
                    row["daily_vaccinations"],
                ],
            )
    num_countries = len(percentage)
    percentage.sort(key=lambda x: x[1], reverse=True)
    top_countries = percentage[:10]
    canada, i = next(
        ((x, i) for i, x in enumerate(percentage) if x[0] == "Canada"), None
    )
    canada[0] = f"Canada #{i}"
    top_countries.append(canada)
    top_countries.reverse()
    flipped = list(zip(*top_countries))
    num_over_threshold = sum(1 for x in top_countries if x[1] > 70)
    bar_colors = [colors["primary"]] * 11
    bar_colors[10] = "#ff0000"
    bar_colors.reverse()
    fig = go.Figure(
        go.Bar(x=flipped[1], y=flipped[0], orientation="h", marker_color=bar_colors),
    )
    fig.update_layout(
        title=f"Vaccination Progress Ranking ({num_countries} total)",
        xaxis=dict(title="Percentage of Population Vaccinated"),
        yaxis=dict(tickfont_size=10),
        margin=dict(t=30, l=10, b=5, r=10),
    )
    return fig


def country_rankings():
    cur_df = pd.read_csv("./data/_raw_data.csv")
    fig = percent_rankings(cur_df)
    return html.Div(
        className="percent-countries-container",
        children=[
            dcc.Tabs(
                id="country-rankings",
                value="percent",
                children=[
                    dcc.Tab(label="Percentage", value="percent"),
                    dcc.Tab(label="Total", value="total"),
                ],
            ),
            dcc.Graph(
                className="percent-countries-graph card",
                id="percent-countries",
                figure=fig,
                config={"displayModeBar": False},
            ),
        ],
    )


def vacc_velocity():
    return html.Div()


def top_stat(stat, heading, class_id):
    return html.Div(
        className="top-stats card",
        id=class_id,
        children=[
            html.Button(
                className="info-button",
                id=f"{class_id}-info",
                children=html.P(className="info", children="?"),
            ),
            html.H2(className="stat", id=f"{class_id}-stat", children=stat),
            html.H6(className="header", id=f"{class_id}-header", children=heading),
        ],
    )


def sparkline_fig(cur_df):
    """
    Draw sparkline.
    """
    df_tail = cur_df.tail(7)
    fig = go.Figure(
        go.Scatter(
            x=np.arange(7),
            y=df_tail["daily_vaccinations"],
            marker=dict(size=1),
            line=dict(color="#87ceeb"),
        )
    )
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        height=45,
        showlegend=False,
        plot_bgcolor="white",
        margin=dict(t=5, l=10, b=5, r=10),
    )
    return fig


def sparkline(cur_df):
    fig = sparkline_fig(cur_df)
    return html.Div(
        className="top-stats card",
        children=[
            html.Button(
                className="info-button",
                id=f"sparkline-info",
                children=html.P(className="info", children="?"),
            ),
            dcc.Graph(id="sparkline", figure=fig, config={"displayModeBar": False}),
            html.H6(
                className="header",
                id="sparkline-header",
                children="Daily Vaccinations Past 7 Days",
            ),
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
            sparkline(df),
        ],
    )


def pred_full_vacc_fig(cur_df, population):
    daily_vaccinated = (
        np.nancumsum(cur_df["daily_vaccinations"].values) / population * 100
    )
    dates = cur_df["date"].values
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=daily_vaccinated))
    fig.update_layout(
        title="Predicted Fully Vaccinated Date",
        xaxis_title="Date",
        yaxis_title="Percentage of Population Vaccinated (%)",
    )
    return fig


def pred_full_vacc(cur_df, population):
    fig = pred_full_vacc_fig(cur_df, population)
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
        children=[top_stats(), pred_full_vacc(df, global_pop)],
    )


def homepage():
    return html.Div(
        className="country-page",
        children=[country_rankings(), right()],
    )


def countrypage(country):
    return html.Div(className="country-page", children=[vacc_velocity(), right()])


def dashboard():
    return html.Div(className="dashboard", id="dashboard", children=[homepage()])


app.layout = html.Div(children=[navbar(), dashboard()])


@app.callback(
    Output(component_id="dashboard", component_property="children"),
    Output(component_id="update-date-stat", component_property="children"),
    Output(component_id="vaccinated-stat", component_property="children"),
    Output(component_id="threshold-stat", component_property="children"),
    Output(component_id="today-stat", component_property="children"),
    Output(component_id="sparkline", component_property="figure"),
    Output(component_id="pred-full-vacc", component_property="figure"),
    Output(component_id="nav-header", component_property="n_clicks"),
    Output(component_id="region", component_property="value"),
    Input(component_id="region", component_property="value"),
    Input(component_id="nav-header", component_property="n_clicks"),
)
def change_page(dropdown_value, n_clicks):
    if n_clicks == 1:  # If home button clicked
        country, iso_code = "Global", None
    else:  # If dropdown clicked
        country, iso_code = dropdown_value.split(",")
    new_df = pd.read_csv(f"./data/{country}_vaccinations.csv")
    page = homepage() if country == "Global" else countrypage(country)
    date = new_df.iloc[[-1]]["date"].to_string(index=False)
    update_date = "{} {}".format(months[date[6:8]], date[9:])
    # update_date = "{} {}".format(months[date[5:7]], date[8:])
    population = (
        global_pop if country == "Global" else pypopulation.get_population(iso_code)
    )
    vaccinated = (
        str(round(new_df["daily_vaccinations"].sum(axis=0) / population * 100, 1)) + "%"
    )
    threshold = "70%"
    today = "{:,}".format(
        int(float(new_df.iloc[[-1]]["daily_vaccinations"].to_string(index=False)))
    )
    sparkline = sparkline_fig(new_df)
    pred = pred_full_vacc_fig(new_df, population)
    return page, update_date, vaccinated, threshold, today, sparkline, pred, 0, country


@app.callback(
    Output(component_id="percent-countries", component_property="figure"),
    Input(component_id="country-rankings", component_property="value"),
)
def switch_ranking_graph(tab):
    cur_df = pd.read_csv("./data/_raw_data.csv")
    percent = percent_rankings(cur_df)
    total = total_rankings(cur_df)
    return percent if tab == "percent" else total


@app.callback(
    Output(component_id="update-date-header", component_property="children"),
    Input(component_id="update-date-info", component_property="n_clicks"),
)
def show_info(n_clicks):
    if n_clicks and n_clicks % 2:
        return "Data is delayed by a couple days."
    else:
        return "Latest Update"


@app.callback(
    Output(component_id="vaccinated-header", component_property="children"),
    Input(component_id="vaccinated-info", component_property="n_clicks"),
)
def show_info(n_clicks):
    if n_clicks and n_clicks % 2:
        return "Percentage of total population vaccinated."
    else:
        return "Vaccinated"


@app.callback(
    Output(component_id="threshold-header", component_property="children"),
    Input(component_id="threshold-info", component_property="n_clicks"),
)
def show_info(n_clicks):
    if n_clicks and n_clicks % 2:
        return "Rough estimate of number of people needed to be vaccinated."
    else:
        return "Herd Immunity Threshold"


@app.callback(
    Output(component_id="today-header", component_property="children"),
    Input(component_id="today-info", component_property="n_clicks"),
)
def show_info(n_clicks):
    if n_clicks and n_clicks % 2:
        return "Rough estimate of number of people needed to be vaccinated."
    else:
        return "Vaccinated Today"


if __name__ == "__main__":
    app.run_server(debug=True)