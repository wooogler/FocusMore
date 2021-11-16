import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(id='app-layout', style={"height": "100vh"})
server = app.server
