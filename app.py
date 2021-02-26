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

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
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
            html.H4(className="header", children="Global Covid Vaccination Progress"),
            dcc.Dropdown(
                className="dropdown",
                id="region",
                options=dropdown_options,
                value="Global,",
            ),
        ],
    )


def percent_coutries():
    cur_df = pd.read_csv("./data/_raw_data.csv")
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
                (
                    row["country"],
                    int(row["daily_vaccinations"] / population * 100),
                ),
            )
    percentage.sort(key=lambda x: x[1])
    top_countries = percentage[-10:]
    flipped = list(zip(*top_countries))
    fig = go.Figure(go.Bar(x=flipped[1], y=flipped[0], orientation="h"))
    fig.update_layout(
        title="Vaccination Progress Ranking",
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
    return html.Div(
        className="percent-countries-container",
        children=[
            dcc.Graph(
                className="percent-countries-graph card",
                id="percent-countries",
                figure=fig,
            )
        ],
    )


def vacc_velocity():
    return html.Div()


def top_stat(stat, heading, class_id):
    return html.Div(
        className="top-stats card",
        children=[
            html.H2(className="stat", id=class_id, children=stat),
            html.H6(className="header", children=heading),
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
            dcc.Graph(id="sparkline", figure=fig),
            html.H6(className="header", children="Daily Vaccinations Past 7 Days"),
        ],
    )


def top_stats():
    return html.Div(
        className="top-stats-container",
        children=[
            top_stat("", "Latest Update", "update_date"),
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
        children=[percent_coutries(), right()],
    )


def countrypage(country):
    return html.Div(className="country-page", children=[vacc_velocity(), right()])


def dashboard():
    return html.Div(className="dashboard", id="dashboard", children=[homepage()])


app.layout = html.Div(children=[navbar(), dashboard()])


@app.callback(
    Output(component_id="dashboard", component_property="children"),
    Output(component_id="update_date", component_property="children"),
    Output(component_id="vaccinated", component_property="children"),
    Output(component_id="threshold", component_property="children"),
    Output(component_id="today", component_property="children"),
    Output(component_id="sparkline", component_property="figure"),
    Output(component_id="pred-full-vacc", component_property="figure"),
    Input(component_id="region", component_property="value"),
)
def change_page(dropdown_value):
    country, iso_code = dropdown_value.split(",")
    new_df = pd.read_csv(f"./data/{country}_vaccinations.csv")
    page = homepage() if country == "Global" else countrypage(country)
    date = new_df.iloc[[-1]]["date"].to_string(index=False)
    update_date = "{} {}".format(months[date[5:7]], date[8:])
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
    return page, update_date, vaccinated, threshold, today, sparkline, pred


if __name__ == "__main__":
    app.run_server(debug=True)