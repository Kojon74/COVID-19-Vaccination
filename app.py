import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from components.navbar import Navbar
from components.dashboard import Dashboard
from components.callbacks import Callbacks
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

navbar = Navbar(data).navbar()
dashboard = Dashboard(data).dashboard()

app.layout = html.Div(
    children=[dcc.Location(id="url", refresh=False), navbar, dashboard]
)

callbacks = Callbacks(app, data)

if __name__ == "__main__":
    app.run_server(debug=True)