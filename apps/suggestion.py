from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app import app
import json

heat_df = pd.read_csv("data/heat.csv")
app_df = pd.read_csv("data/AppUsageStatEntity-5572736000.csv")
app_df["time"] = pd.to_datetime(app_df["timestamp"], unit="ms")
app_df = app_df.loc[:, ["time", "name", "startTime", "endTime", "totalTimeForeground"]]
app_df.sort_values(by="time", ascending=True)


def ampm(x):
    if x < 12:
        res = f"{x}AM"
    elif x < 24 and x > 12:
        y = x - 12
        res = f"{y}PM"
    elif x == 12:
        res = "12PM"
    else:
        res = "0AM"
    return res


def cutname(y):
    if len(y) < 11:
        return y
    else:
        return y.split()[-1]


fig1 = go.Figure(
    data=go.Heatmap(
        x=heat_df.hour + 1,
        y=heat_df.location,
        z=heat_df.rate,
        hovertemplate="%{y}<br>" + "%{z:d}%<extra></extra>",
        colorscale="Purp",
    )
)
fig1.update_layout(title="Focus time rate = Focus time/Total time spent", title_x=0.5)
fig1.update_xaxes(dtick=2, title_text="time(h)")
fig1.update_yaxes(title_text="place")

fig2 = go.Figure(
    data=go.Pie(labels=["AppName"], values=[100], marker=dict(colors=["lightgray"]))
)
fig2.update_layout(legend=dict(orientation="h", xanchor="center", x=0.5))
layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("Focus Time Rate"),
                                    html.P(
                                        [
                                            "Summary of Focus Time Rate for selected date range.",
                                            html.Br(),
                                            "Put the cursor on each slot to check app usage percentage.",
                                        ]
                                    ),
                                ],
                                style={"marginTop": "10%"},
                            ),
                            dcc.Graph(id="heatmap", figure=fig1),
                        ]
                    )
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("App usage"),
                                    html.Div(
                                        [html.P(["Location", html.Br(), "Time"])],
                                        id="output",
                                    ),
                                ],
                                style={"marginTop": "10%"},
                            ),
                            html.Div(dcc.Graph(id="appPie", figure=fig2)),
                        ],
                        className="text-center",
                    )
                ),
            ]
        )
    ],
    class_name="h-100",
)


@app.callback(
    Output("output", "children"),
    [Input("heatmap", "hoverData"), Input("heatmap", "clickData")],
)
def show_data(hoverData, clickData):
    if hoverData is not None:
        locationName = hoverData["points"][0]["y"]
        timeMid = hoverData["points"][0]["x"]
        timeStart = ampm(timeMid - 1)
        timeEnd = ampm(timeMid + 1)
        return [html.P([f"{locationName}", html.Br(), f"{timeStart} - {timeEnd}"])]
    else:
        return [html.P(["Location", html.Br(), "Time"])]


@app.callback(Output("appPie", "figure"), Input("heatmap", "hoverData"))
def update_pie(hoverData):
    if hoverData is not None:
        locationName = hoverData["points"][0]["y"]
        timeMid = hoverData["points"][0]["x"]
        timeStart = timeMid - 1
        timeEnd = timeMid + 1
        pie_df = app_df.loc[
            (app_df["time"].dt.hour >= timeStart) & (app_df["time"].dt.hour < timeEnd)
        ]
        pie_df = pie_df.loc[:, ["name", "totalTimeForeground"]]
        aggrByApp = pie_df.groupby(["name"]).max() - pie_df.groupby("name").min()
        aggrByApp = aggrByApp.sort_values(by=["totalTimeForeground"], ascending=False)
        aggrByApp.reset_index(level=["name"], inplace=True)
        top5app = aggrByApp.loc[:4, :]
        top5app["name"] = top5app["name"].apply(lambda x: cutname(x))
        etc = aggrByApp.loc[5:, :]
        top5app = top5app.append(
            pd.DataFrame(
                [["etc", sum(etc.totalTimeForeground)]],
                columns=["name", "totalTimeForeground"],
                index=[5],
            )
        )
        top5app = top5app.loc[top5app["totalTimeForeground"] != 0]
        fig3 = go.Figure(
            data=[
                go.Pie(
                    labels=top5app.name,
                    values=top5app.totalTimeForeground,
                    textinfo="percent",
                    insidetextorientation="radial",
                )
            ]
        )
        # px.pie(top5app, values='totalTimeForeground', names='name', insidetextorientation='radial')
        fig3.update_layout(legend=dict(orientation="h", xanchor="center", x=0.5))
        return fig3
    else:
        return fig2
