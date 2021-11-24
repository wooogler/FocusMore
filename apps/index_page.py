from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from app import app
from datetime import datetime, timedelta, date
import glob
import os
import pandas as pd

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H2(["Welcome to ", html.B("Focusmore")]),
                                html.P(
                                    [
                                        "FocusMore is an application that tracks users' focus time and tells how smartphone interferes with working.",
                                        html.Br(),
                                        "This application",
                                    ]
                                ),
                                html.Ol(
                                    [
                                        html.Li("helps you choose where you worked,"),
                                        html.Li(
                                            "shows how much you focused or couldn't focus during your working hours in each place,"
                                        ),
                                        html.Li("shows what apps you used most,"),
                                        html.Li(
                                            "suggest the best working condition and let you know what apps to use less."
                                        ),
                                    ]
                                ),
                            ], style={"marginTop": "10%"}
                        )
                    ],
                    width=8,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Table(
                                    [
                                        html.Tr(
                                            [
                                                html.Td(
                                                    "■",
                                                    style={
                                                        "color": "lightgray",
                                                        "width": "25px",
                                                    },
                                                ),
                                                html.Td(
                                                    html.B("Leisure Time"),
                                                    style={"width": "125px"},
                                                ),
                                                html.Td(
                                                    "The time when you are moving in the working place"
                                                ),
                                            ]
                                        ),
                                        html.Tr(
                                            [
                                                html.Td(
                                                    "■",
                                                    style={
                                                        "color": "red",
                                                        "width": "25px",
                                                    },
                                                ),
                                                html.Td(
                                                    html.B("Wasting Time"),
                                                    style={"width": "125px"},
                                                ),
                                                html.Td(
                                                    "The time when you are sitting on the chair and using your smartphone"
                                                ),
                                            ]
                                        ),
                                        html.Tr(
                                            [
                                                html.Td(
                                                    "■",
                                                    style={
                                                        "color": "blue",
                                                        "width": "25px",
                                                    },
                                                ),
                                                html.Td(
                                                    html.B("Focus Time"),
                                                    style={"width": "125px"},
                                                ),
                                                html.Td(
                                                    "The time when you are sitting on the chair in the working space"
                                                ),
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        )
                    ],
                    width=8,
                )
            ]
        ),
    ]
)


@app.callback(
    [
        Output("date-picker-range", "min_date_allowed"),
        Output("date-picker-range", "max_date_allowed"),
        Output("date-picker-range", "start_date"),
        Output("date-picker-range", "end_date"),
    ],
    Input("user-dropdown", "value"),
)
def update_date_range(user_name):
    dev_files = glob.glob(
        os.path.join(os.getcwd(), "user_data", user_name, "DeviceEventEntity-*.csv")
    )
    df_loc_files = (pd.read_csv(f) for f in dev_files)
    df_loc = pd.concat(df_loc_files, ignore_index=True)
    df_loc = df_loc.sort_values(["timestamp"])
    min_date = date.fromtimestamp(min(df_loc["timestamp"]) / 1000).isoformat()
    max_date = (
        date.fromtimestamp(max(df_loc["timestamp"]) / 1000) + timedelta(days=1)
    ).isoformat()

    return [min_date, max_date, min_date, max_date]



