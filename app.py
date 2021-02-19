import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
colors = {
    "primary": "#87ceeb",
    "secondary": "#166484",
    "tertiary": "#fdfeff",
    "white": "#fff",
    "black": "#000",
}

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)


def navbar():
    return html.Div(
        className="nav",
        children=[
            html.H4(className="header", children="Global Covid Vaccination Progress"),
            dcc.Dropdown(
                className="dropdown",
                id="region",
                options=[{"label": "Global", "value": "Global"}],
                value="Global",
            ),
        ],
    )


def percent_coutries():
    countries = [
        "Canada",
        "Japan",
        "USA",
        "Italy",
        "France",
        "Germany",
        "UK",
        "China",
        "Mexico",
        "India",
    ]
    percentages = [50, 43, 40, 37, 33, 31, 29, 25, 21, 19]
    fig = go.Figure(go.Bar(x=countries, y=percentages))
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


def top_stat(stat, heading):
    return html.Div(
        className="top-stat-container",
        children=[
            html.Div(
                className="top-stats card",
                children=[
                    html.H2(className="stat", children=stat),
                    html.H6(className="header", children=heading),
                ],
            ),
        ],
    )


def top_stats():
    return html.Div(
        className="top-stats-container",
        children=[
            top_stat("Feb. 15", "Latest Update"),
            top_stat("33%", "Vaccinated"),
            top_stat("60%", "Vaccination Intent"),
            top_stat("1000", "Vaccinnated Today"),
            top_stat("33%", "Vaccinnated"),
        ],
    )


def pred_full_vacc():
    dates = ["Jan 1st", "Jan 2nd"]
    daily_vaccinated = [100, 200]
    daily_cases = [300, 200]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=daily_vaccinated))
    fig.add_trace(go.Scatter(x=dates, y=daily_cases))
    fig.update_layout(
        title="Predicted Fully Vaccinated Date",
        xaxis_title="Date",
        yaxis_title="Number of Vaccinations/Covid-19 Cases",
    )
    return html.Div(
        className="pred-full-vacc-container",
        children=[
            dcc.Graph(
                className="pred-full-vacc-graph card", id="pred-full-vacc", figure=fig
            ),
        ],
    )


def right():
    return html.Div(className="right", children=[top_stats(), pred_full_vacc()])


def homepage():
    return html.Div(
        className="country-page",
        children=[percent_coutries(), right()],
    )


def countrypage():
    return html.Div(className="country-page", children=[vacc_velocity(), right()])


def dashboard():
    return html.Div(className="dashboard", id="dashboard", children=[homepage()])


app.layout = html.Div(children=[navbar(), dashboard()])


@app.callback(
    Output(component_id="dashboard", component_property="children"),
    Input(component_id="region", component_property="value"),
)
def change_page(country):
    return homepage() if country == "global" else countrypage()


if __name__ == "__main__":
    app.run_server(debug=True)