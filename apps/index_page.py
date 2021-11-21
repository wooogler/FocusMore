from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from app import app
layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.Div(html.B("Select Username"), style={"background-color":"mediumpurple", "color":"white"}), width="auto"),
                dbc.Col(html.Div(html.B("Selct Date Range"), style={"background-color":"mediumpurple", "color":"white"}), width={"size":"auto", "offset":1})
            ],
            justify="end"
        ),
        dbc.Row(
            [
                dbc.Col([
                    html.Div([
                        html.H2(["Welcome to ",html.B("Focusmore")]),
                        html.P(["FocusMore is an application that tracks users' focus time and tells how smartphone interferes with working.",html.Br(),"This application"]),
                        html.Ol([html.Li("helps you choose where you worked,"),
                                 html.Li("shows how much you focused or couldn't focus during your working hours in each place,"),
                                 html.Li("shows what apps you used most,"),
                                 html.Li("suggest the best working condition and let you know what apps to use less.")]
                                )
                    ])
                ], width=8)
            ]
        ),
        dbc.Row(
            [
                dbc.Col([
                    html.Div([
                        html.Table([
                            html.Tr([html.Td("■", style={'color':'lightgray', 'width':'25px'}),
                                     html.Td(html.B("Leisure Time"), style={'width':'125px'}),
                                     html.Td("The time when you are moving in the working place")]),
                            html.Tr([html.Td("■", style={'color':'red', 'width':'25px'}),
                                     html.Td(html.B("Wasting Time"), style={'width':'125px'}),
                                     html.Td("The time when you are sitting on the chair and using your smartphone")]),
                            html.Tr([html.Td("■", style={'color':'blue', 'width':'25px'}),
                                     html.Td(html.B("Focus Time"), style={'width':'125px'}),
                                     html.Td("The time when you are sitting on the chair in the working space")])
                        ])
                    ])
                ], width=8)
            ]
        )
    ]
)