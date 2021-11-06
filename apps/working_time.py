from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from app import app


def generate_item(title, children='children'):
    return html.Div(
        [html.H4(title),
         children]
    )


layout = dbc.Container([
    dbc.Row([dbc.Col(generate_item(title='Working places on a map')),
            dbc.Col(generate_item(title='My working places'))], class_name='h-50'),
    dbc.Row([dbc.Col(generate_item(title='Entire time spent at Out Lab')),
            dbc.Col(generate_item(title='Daily time spent at Out Lab'))], class_name='h-50')
], class_name='h-100')
