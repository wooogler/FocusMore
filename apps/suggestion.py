from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app import app
heat_df=pd.read_csv('data/heat.csv')
print(heat_df)
fig=go.Figure(data=go.Heatmap(x=heat_df.hour+1,
                              y=heat_df.location,
                              z=heat_df.rate,
                              colorscale='sunset'))
layout = dbc.Container([
    dbc.Row(html.Div(), class_name='h-15'),
    dbc.Row(
        [
            dbc.Col(html.Div([
                html.H2("Focus Time Rate"),
                html.P(["Summary of Focus Time Rate for selected date range.", html.Br(),
                        "Put the cursor on each slot to check app usage percentage."]),
                dcc.Graph(figure=fig)
            ])),
            dbc.Col(html.Div([
                html.H2("App usage"), "pie chart"
            ]))
        ], class_name='h-70'
    ),
    dbc.Row(html.Div(), class_name='h-15')
], class_name="h-100")