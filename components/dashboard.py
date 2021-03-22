import dash_html_components as html

from .country_rankings import CountryRankings
from .top_stats import TopStats
from .vaccination_progress import VaccinationProgress


class Dashboard:
    def __init__(self, data):
        self.data = data

    def right(self):
        """
        Returns layout for right hand side component.
        """
        top_stats = TopStats(self.data).top_stats()
        vaccination_progress = VaccinationProgress(self.data).vaccination_progress()
        return html.Div(
            className="right",
            children=[top_stats, vaccination_progress],
        )

    def homepage(self):
        """
        Returns layout for homepage.
        """
        country_rankings = CountryRankings(self.data).country_rankings()
        return html.Div(
            className="country-page",
            children=[country_rankings, self.right()],
        )

    def countrypage(self, country):
        """
        Returns layout for specific coutry's page.
        """
        return html.Div(className="country-page", children=[self.right()])

    def dashboard(self):
        """
        Returns top-level layout
        """
        return html.Div(
            className="dashboard", id="dashboard", children=[self.homepage()]
        )
