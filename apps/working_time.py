from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from app import app

layout = dbc.Container([
    dbc.Row([dbc.Col(html.Div('Working places on a map')),
            dbc.Col(html.Div('My working places'))]),
    dbc.Row([dbc.Col(html.Div('Entire time spent at Out Lab')),
            dbc.Col(html.Div('Daily time spent at Out Lab'))])
])
