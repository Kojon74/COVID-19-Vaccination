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

global_df = pd.read_csv("./data/_raw_data.csv")
df = pd.read_csv("./data/Global_vaccinations.csv")

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)


def navbar():
    dropdown_options = [
        {"label": country, "value": country} for country in set(global_df["country"])
    ]
    dropdown_options.sort(key=lambda x: x["label"])
    global_option = {"label": "Global", "value": "Global"}
    dropdown_options.insert(0, global_option)
    return html.Div(
        className="nav",
        children=[
            html.H4(className="header", children="Global Covid Vaccination Progress"),
            dcc.Dropdown(
                className="dropdown",
                id="region",
                options=dropdown_options,
                value="Global",
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
        # print(row["iso_code"])
        if row["iso_code"] != "":
            population = pypopulation.get_population(row["iso_code"])
        # print(population)
        if population:
            print(population)
            percentage.append(
                np.asarray(
                    [
                        row["country"],
                        row["daily_vaccinations"] / population,
                    ]
                )
            )
        else:
            # pass
            print(row["country"])
    # print(percentage)
    percentage = np.asarray(percentage)
    percentage[percentage[:, 1].argsort()]
    top_countries = percentage
    print(top_countries)
    fig = go.Figure(
        go.Bar(x=top_countries[:, 1], y=top_countries[:, 0], orientation="h")
    )
    fig.update_layout(
        title="Vaccination Progress Ranking",
        margin=dict(t=30, l=10, b=5, r=10),
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
        className="top-stat-container",
        children=[
            html.Div(
                className="top-stats card",
                children=[
                    html.H2(className="stat", id=class_id, children=stat),
                    html.H6(className="header", children=heading),
                ],
            ),
        ],
    )


def top_stat_graph(cur_df):
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
    return html.Div(
        className="top-stats card",
        children=[
            dcc.Graph(figure=fig),
            html.H6(className="header", children="Past 7 Days"),
        ],
    )


def top_stats():
    return html.Div(
        className="top-stats-container",
        children=[
            top_stat("Feb. 15", "Latest Update", "update_date"),
            top_stat("33%", "Vaccinated", "vaccinated"),
            top_stat("60%", "Vaccination Intent", "threshold"),
            top_stat("1000", "Vaccinnated Today", "today"),
            html.Div(
                className="top-stat-container",
                id="sparkline",
                children=[
                    top_stat_graph(df),
                ],
            ),
        ],
    )


def pred_full_vacc(cur_df):
    daily_vaccinated = cur_df["daily_vaccinations"].values
    dates = cur_df["date"].values
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=daily_vaccinated))
    fig.update_layout(
        title="Predicted Fully Vaccinated Date",
        xaxis_title="Date",
        yaxis_title="Number of Vaccinations/Covid-19 Cases",
    )
    return html.Div(
        children=[
            dcc.Graph(
                className="pred-full-vacc-graph card", id="pred-full-vacc", figure=fig
            ),
        ],
    )


def right():
    return html.Div(
        className="right",
        children=[
            top_stats(),
            html.Div(
                className="pred-full-vacc-container",
                id="pred",
                children=[pred_full_vacc(df)],
            ),
        ],
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
    Output(component_id="sparkline", component_property="children"),
    Output(component_id="pred", component_property="children"),
    Input(component_id="region", component_property="value"),
)
def change_page(country):
    new_df = pd.read_csv(f"./data/{country}_vaccinations.csv")
    page = homepage() if country == "Global" else countrypage(country)
    update_date = new_df.iloc[[-1]]["date"].to_string(index=False)[5:]
    vaccinated = 33
    threshold = 70
    today = float(new_df.iloc[[-1]]["daily_vaccinations"].to_string(index=False))
    sparkline = top_stat_graph(new_df)
    pred = pred_full_vacc(new_df)
    return page, update_date, vaccinated, threshold, today, sparkline, pred


if __name__ == "__main__":
    app.run_server(debug=True)