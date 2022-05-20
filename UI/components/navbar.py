import dash_bootstrap_components as dbc
from dash import html

from UI.UI_params import *


def get_nav_bar(app):
    return dbc.Navbar(
        [
            dbc.NavbarBrand("Thousand Suns", className="ms-2"),
            dbc.NavLink("Annual Simulation", href=YEARLY_SIMULATION_PAGE),
            dbc.NavLink("Finding Optimum", href=FIND_OPTIMUM_PAGE),
            dbc.NavLink("Simulation Params", href=SIMULATION_PARAMS_PAGE),
            dbc.Row([
                dbc.Col(html.Img(src=app.get_asset_url(MADOR_LOGO), height="50px"), style={"padding-left": "1rem"}),
                dbc.Col(html.Img(src=app.get_asset_url(TALPIOT_LOGO), height="50px"), style={"padding-left": "1rem"}),
            ],
                className="g-0 ms-auto flex-nowrap mt-3 mt-md-0", )
        ],
        color="dark",
        dark=True,
    )
