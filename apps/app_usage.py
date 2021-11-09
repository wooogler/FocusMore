from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from app import app
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

focus_df = pd.read_csv('data/FocusRate.csv')

app_df = pd.read_csv('data/AppPie.csv')

layout = dbc.Container([
    dbc.Row([
        html.Div([
            dcc.Dropdown(
                id="selectDay",
                options=[{
                    "label": i,
                    "value": i
                } for i in focus_df['Day'].unique()],
                value="Day",
                placeholder="Select Day",
                searchable=False,
                clearable=False,
                style={"width": "200px", "float": "right"},
            ),
            html.H2("Focus Time Rate per hour per day"),
            html.P([
                "The focus time rate means the ratio of focus to the whole", html.Br(),
                "This graph shows the ratio of focus time per 2 hours per day. You can see when you focus more or less on this graph."
            ]),
            dcc.Graph(id='FocusBar')
        ]),
    ],class_name="h-35"),
    dbc.Row([
        dbc.Col(
            html.Div([
                html.Div([html.H2("Distracting Apps"),
                html.P([
                    "The top 5 apps that are used most frequently ", html.Br(),
                    "when you have ", html.I("Low Focus Time Rate")])
                ], style={"border-color": "mediumpurple" ,"border":" solid 0.1em", "border-radius" : "10px"}),
                dcc.Graph(id='appPie1')
            ])),
        dbc.Col(
             html.Div([
                html.Div([html.H2("Not Disturbing Apps"),
                html.P([
                    "The top 5 apps that are used most frequently ", html.Br(),
                    "when you have ", html.I("High Focus Time Rate")])
                ], style={"border-color": "lightgray" ,"border":" solid 0.1em", "border-radius" : "10px"}),
                dcc.Graph(id='appPie2')
            ])),
    ], class_name = "h-35", style={"text-align": "center"})   
], class_name = "h-100")

@app.callback(
    Output('FocusBar','figure'),
    Input('selectDay','value')
)
def update_bar_graph(selectedValue):
    if selectedValue == "Day":
        df = focus_df.groupby('Hour').mean()
        
        df.reset_index(level='Hour', inplace=True)
    else:
        df = focus_df[focus_df['Day'] == selectedValue]
    meanVal = df['FocusRate'].mean()
    df['Label'] = df['FocusRate'].apply(lambda x: 'High' if x> meanVal else 'Low')  
    colors = {'High': 'lightgray', 'Low': 'mediumpurple'}
    labels = {'High': 'High Focus Rate', 'Low': 'Low Focus Rate'}
    
    fig=go.Figure()

    for label, label_df in df.groupby('Label'):

        fig.add_trace(go.Bar(
                x=label_df.Hour,
                y=label_df.FocusRate, 
                name=labels[label], 
                marker={'color': colors[label]}))

    fig.add_trace(go.Scatter(
                x= [df.Hour.min()-1, df.Hour.max()+1],
                y=[ meanVal,meanVal],
                name = 'Mean',
                mode = 'lines',
                showlegend = False,
                marker = {'color': 'darkgray'}
                ))        
    fig.layout.plot_bgcolor = '#fff'
    fig.layout.paper_bgcolor = '#fff'

    return fig

@app.callback(
    Output('appPie1','figure'),
    Input('selectDay','value')
)
def update_pie1_graph(selectedValue):
    df = app_df.loc[app_df['Label'] == 'Low']
    if selectedValue == "Day":
        df = df.groupby('AppName').mean()
        df.reset_index(level='AppName', inplace=True)
    else:
        df = df[df['Day'] == selectedValue]
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=df['AppName'], values=df['Rate']))
    
    return fig

@app.callback(
    Output('appPie2','figure'),
    Input('selectDay','value')
)
def update_pie1_graph(selectedValue):
    df = app_df.loc[app_df['Label'] == 'High']
    if selectedValue == "Day":
        df = df.groupby('AppName').mean()
        df.reset_index(level='AppName', inplace=True)
    else:
        df = df[df['Day'] == selectedValue]
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=df['AppName'], values=df['Rate']))

    return fig
