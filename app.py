import dash
import dash_bootstrap_components as dbc
from dash import html

app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout=html.Div(["home"])
server = app.server
