import dash_core_components as dcc
import dash_html_components as html


class Navbar:
    def __init__(self, data):
        self.data = data

    def navbar(self):
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
                    options=self.data.dropdown_options,
                    value="Global,",
                    placeholder="Select Country",
                ),
            ],
        )