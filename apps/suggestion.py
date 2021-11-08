from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app import app
import json
heat_df=pd.read_csv('data/heat.csv')
def ampm(x):
    if x<12:
        res=f'{x}AM'
    else:
        res=f'{x}PM'
    return res
fig1=go.Figure(data=go.Heatmap(x=heat_df.hour+1,
                              y=heat_df.location,
                              z=heat_df.rate,
                              colorscale='Purp'))
fig2=go.Figure(data=go.Pie(labels=['KakaoTalk','Instagram','Chrome','Slack','YouTube'], values=[25,56,32,67,32]))
layout = dbc.Container([
    dbc.Row(html.Div(), class_name='h-15'),
    dbc.Row(
        [
            dbc.Col(html.Div([
                html.H2("Focus Time Rate"),
                html.P(["Summary of Focus Time Rate for selected date range.", html.Br(),
                        "Put the cursor on each slot to check app usage percentage."]),
                dcc.Graph(id='heatmap', figure=fig1)
            ])),
            dbc.Col(html.Div([
                html.H2("App usage"),
                html.Div(id='output'),
                dcc.Graph(id='appPie', figure=fig2)
            ], className='text-center'),
                )
        ], class_name='h-70'
    ),
    dbc.Row(html.Div(), class_name='h-15')
], class_name="h-100")

@app.callback(
    Output('output', 'children'),
    [Input('heatmap', 'hoverData'), Input('heatmap','clickData')])
def show_data(hoverData, clickData):
    if (hoverData is not None):
        locationName=hoverData['points'][0]['y']
        timeMid=hoverData['points'][0]['x']
        timeStart=ampm(timeMid-1)
        timeEnd=ampm(timeMid+1)
        return [
            f'{locationName}, {timeStart} - {timeEnd}'
        ]
    else:
        return []