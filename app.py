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


def percent_vacc():
    labels = ["Vaccinated", "Not Vaccinated"]
    values = [100, 200]
    fig_colors = [colors["primary"], colors["white"]]
    marker = go.pie.Marker(colors=fig_colors)
    fig = go.Figure(
        data=[go.Pie(labels=labels, values=values, hole=0.3, marker=marker)]
    )
    return html.Div(
        className="percent-vacc card",
        children=[
            html.H5(children="Percentage of Population Vaccinated"),
            dcc.Graph(id="percent-vaccinated", figure=fig),
            html.H6(children="Ranking"),
            html.Ol(
                className="ranking",
                children=[
                    html.Li(children="Canada"),
                    html.Li(children="Japan"),
                    html.Li(children="USA"),
                ],
            ),
        ],
    )


def daily_vacc():
    return html.Div(
        className="daily-vacc card", children=[html.H5(children="Daily Vaccinations")]
    )


def pred_full_vacc():
    return html.Div(
        className="pred-full-vacc card",
        children=[html.H5(children="Predicted Fully Vaccinated Date")],
    )


def homepage():
    return html.Div(
        className="country-page",
        children=[percent_vacc(), daily_vacc(), pred_full_vacc()],
    )


def dashboard(country):
    return html.Div(className="dashboard", children=[homepage()])


app.layout = html.Div(children=[navbar(), dashboard("global")])

if __name__ == "__main__":
    app.run_server(debug=True)