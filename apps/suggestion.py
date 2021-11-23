from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import timedelta, date, datetime
import plotly.express as px
import plotly.graph_objects as go
from app import app
import json
import os
import glob

heat_df = pd.read_csv("data/heat.csv")
app_df = pd.read_csv("data/AppUsageStatEntity-5572736000.csv")
app_df["time"] = pd.to_datetime(app_df["timestamp"], unit="ms")
app_df = app_df.loc[:, ["time", "name", "startTime", "endTime", "totalTimeForeground"]]
app_df.sort_values(by="time", ascending=True)

def extract_df(df, start_date, end_date):
    if start_date is not None:
        start_date_timestamp = datetime.fromisoformat(start_date).timestamp() * 1000
        df = df.loc[start_date_timestamp <= df["timestamp"]]
    if end_date is not None:
        end_date_timestamp = (
            datetime.fromisoformat(end_date) + timedelta(days=1)
        ).timestamp() * 1000
        df = df.loc[df["timestamp"] < end_date_timestamp]
    return df

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

def files_to_df(files):
    dfs=(pd.read_csv(f) for f in files)
    df=pd.concat(df_loc_files, ignore_index=True)
    df=df.sort_values(["timestamp"])
    return df

def range_data(d, start_date, end_date):
    return d.loc[(d["time"]>=start_date)&(d["time"]<end_date+timedelta(days=1))]


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

# @app.callback(
#     [
#         Output("date-picker-range", "min_date_allowed"),
#         Output("date-picker-range", "max_date_allowed"),
#         Output("appPie", "selectedData"),
#         Output("heatmap", "selectedData")
#     ],
#     Input("user-dropdown", "value"),
#     Input("date-picker-range", "start_date"),
#     Input("date-picker-range", "end_date"),
# )
# def update_data(user_name, start_date, end_date):
#     app_files=glob.glob(
#         os.path.join(os.getcwd(), "user_data", user_name, "AppUsageStatEntity-*.csv")
#     )
#     loc_files=glob.glob(
#         os.path.join(os.getcwd(), "user_data", user_name, "LocationEntity-*.csv")
#     )
#     phy_files=glob.glob(
#         os.path.join(os.getcwd(), "user_data", user_name, "PhysicalActivityEventEntity-*.csv")
#     )
#     app_df=files_to_df(app_files)
#     app_df["time"] = pd.to_datetime(app_df["timestamp"], unit="ms")
#     app_df=range_data(app_df)
#     loc_df=files_to_df(loc_files)
#     loc_df["time"] = pd.to_datetime(loc_df["timestamp"], unit="ms")
#     loc_df=range_data(loc_df)
#     phy_df=files_to_df(app_files)
#     phy_df["time"] = pd.to_datetime(phy_df["timestamp"], unit="ms")
#     phy_df=range_data(phy_df)
#     app_df=app_df.loc[:,["timestamp", "name", "startTime", "endTime","totalTimeForeground"]]
#     min_date = date.fromtimestamp(min(df_loc["timestamp"]) / 1000).isoformat()
#     max_date = (
#         date.fromtimestamp(max(df_loc["timestamp"]) / 1000) + timedelta(days=1)
#     ).isoformat()
#     return([min_date, max_date, app_df, [loc_df, phy_df]])
    

@app.callback(
    Output("output", "children"),
    Input("heatmap", "clickData"),
)
def show_data(clickData):
    if clickData is not None:
        locationName = clickData["points"][0]["y"]
        timeMid = clickData["points"][0]["x"]
        timeStart = ampm(timeMid - 1)
        timeEnd = ampm(timeMid + 1)
        return [html.P([f"{locationName}", html.Br(), f"{timeStart} - {timeEnd}"])]
    else:
        return [html.P(["Location", html.Br(), "Time"])]


@app.callback(
              Output("appPie", "figure"),
              Input("heatmap", "clickData"), 
              Input("user-dropdown", "value"),
              Input("date-picker-range", "start_date"),
              Input("date-picker-range", "end_date"),
)
def update_pie(clickData, user_name,start_date, end_date):
    # in response to username change
    app_files = glob.glob(
            os.path.join(os.getcwd(), "user_data", user_name, "AppUsageStatEntity-*.csv")
    )
    df_app_files = (pd.read_csv(f) for f in app_files)
    app_df = pd.concat(df_app_files, ignore_index=True)
    app_df = app_df.sort_values(["timestamp"], ascending=True)
    app_df["time"] = pd.to_datetime(app_df["timestamp"], unit="ms")
    app_df=extract_df(app_df, start_date, end_date)
    app_df = app_df.loc[:, ["time", "name", "startTime", "endTime", "totalTimeForeground"]]
    app_byname=app_df.groupby(["name"])
    
    if clickData is not None: # in response to heatmap click

        locationName = clickData["points"][0]["y"]
        timeMid = clickData["points"][0]["x"]
        timeStart = timeMid - 1
        timeEnd = timeMid + 1
        pie_df = app_df.loc[
            (app_df["time"].dt.hour >= timeStart) & (app_df["time"].dt.hour < timeEnd)
        ]
        
        # day_delta = pd.to_timedelta(np.arange(end_date-start_date), unit='d')
        
        
        
        
        pie_df = pie_df.loc[:, ["name", "totalTimeForeground"]]
        aggrByApp = pie_df.groupby(["name"]).max() - pie_df.groupby("name").min()
        aggrByApp = aggrByApp.sort_values(by=["totalTimeForeground"], ascending=False)
        aggrByApp.reset_index(level=["name"], inplace=True)
        top5app = aggrByApp.loc[:4, :]
        top5app.loc["name"] = top5app["name"].apply(lambda x: cutname(x))
        etc = aggrByApp.loc[5:, :]
        top5app = top5app.append(
            pd.DataFrame(
                [["etc", sum(etc.totalTimeForeground)]],
                columns=["name", "totalTimeForeground"],
                index=[5],
            )
        )
        top5app["totalMin"]=top5app["totalTimeForeground"]/60000
        top5app = top5app.loc[top5app["totalTimeForeground"] != 0]
        fig3 = go.Figure(
            data=[
                go.Pie(
                    labels=top5app.name,
                    values=top5app.totalMin,
                    textinfo="percent",
                    hoverinfo="label+value",
                    insidetextorientation="radial",
                    direction="clockwise",
                    sort=False
                )
            ]
        )
        # px.pie(top5app, values='totalTimeForeground', names='name', insidetextorientation='radial')
        fig3.update_layout(legend=dict(orientation="h", xanchor="center", x=0.5))
        pieFig=fig3
    else:
        pieFig=fig2
    return pieFig
