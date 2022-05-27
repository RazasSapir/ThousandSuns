import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output

from UI.UI_params import *
from UI.components.navbar import get_nav_bar
from UI.pages import find_optimum_page, annual_simulation_page, simulation_params_page

app = Dash(external_stylesheets=[dbc.themes.JOURNAL], suppress_callback_exceptions=True, assets_folder=ASSETS_FOLDER)

app.layout = html.Div([
    get_nav_bar(app),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', style={"padding": "1rem"})
])


# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == YEARLY_SIMULATION_PAGE:
        return annual_simulation_page.get_layout()
    elif pathname == FIND_OPTIMUM_PAGE:
        return find_optimum_page.get_layout()
    elif pathname == SIMULATION_PARAMS_PAGE:
        return simulation_params_page.get_layout()
    else:
        return '404'
    # You could also return a 404 "URL not found" page here


def main():
    app.run_server(host="0.0.0.0", debug=True)
