from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from app import app
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

focus_df = pd.read_csv('data/FocusRate.csv')
pie1=go.Figure(data=go.Pie(labels=['Youtube','Instagram','KaKaoTalk','Netflix','Chrome','Others'], values=[30,25,17,10,4,14]))
pie2=go.Figure(data=go.Pie(labels=['Slack','Music','Notion','Message','Chrome','Others'], values=[38,29,18,9,6,10]))

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
                html.H2("Distracting Apps"),
                html.P([
                    "The top 5 apps that are used most frequently ", html.Br(),
                    "when you have ", html.I("Low Focus Time Rate")
                ]),
                dcc.Graph(id='appPie1', figure=pie1)
            ])),
        dbc.Col(
             html.Div([
                html.H2("Not Disturbing Apps"),
                html.P([
                    "The top 5 apps that are used most frequently ", html.Br(),
                    "when you have ", html.I("High Focus Time Rate")
                ]),
                dcc.Graph(id='appPie2', figure=pie2)
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
    
    bars = []
    for label, label_df in df.groupby('Label'):
        bars.append(go.Bar(x=label_df.Hour ,y=label_df.FocusRate, name=labels[label], marker={'color': colors[label]}))
    fig_bar=go.Figure(data=bars)
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig_bar