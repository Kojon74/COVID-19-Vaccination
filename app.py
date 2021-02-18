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
    fig.update_layout(title="Percentage of Population Vaccinated")
    return html.Div(
        className="percent-vacc stats-container",
        children=[
            dcc.Graph(className="card", id="percent-vaccinated", figure=fig),
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
    dates = ["Jan 1st", "Jan 2nd"]
    daily_vaccinated = [100, 200]
    fig = go.Figure(data=[go.Bar(x=dates, y=daily_vaccinated)])
    fig.update_layout(
        title="Number of Vaccinations per Day",
        xaxis_title="Date",
        yaxis_title="Number of Vaccinations",
    )
    return html.Div(
        className="daily-vacc stats-container",
        children=[
            dcc.Graph(className="card", id="daily-vaccination", figure=fig),
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
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=dates, y=daily_vaccinated))
    fig1.add_trace(go.Scatter(x=dates, y=daily_cases))
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=dates, y=daily_vaccinated))
    fig2.add_trace(go.Scatter(x=dates, y=daily_cases))
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=dates, y=daily_vaccinated))
    fig3.add_trace(go.Scatter(x=dates, y=daily_cases))
    top3_figs = [fig1, fig2, fig3]
    return html.Div(
        className="pred-full-vacc stats-container",
        children=[
            dcc.Graph(className="card", id="pred-full-vacc", figure=fig),
            html.Div(
                className="ranking-container",
                children=[
                    dcc.Graph(
                        className="ranking card", id=f"pred-full-vacc-{i+1}", figure=fig
                    )
                    for i, fig in enumerate(top3_figs)
                ],
            ),
        ],
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