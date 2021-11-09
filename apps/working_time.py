from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from app import app
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import random


def generate_item(title, children="children"):
    return html.Div([html.H4(title), children], style={"height": "100%"})


df_act = pd.read_csv("data/PhysicalActivityTransitionEntity-5572736000.csv")
df_dev = pd.read_csv("data/DeviceEventEntity-5572736000.csv")

# map
df_loc = pd.read_csv("data/LocationEntity-5572736000.csv", index_col="timestamp")

fig_loc = px.scatter_mapbox(
    df_loc,
    lat="latitude",
    lon="longitude",
    hover_name=df_loc.index,
    zoom=13,
)
fig_loc.update_layout(mapbox_style="open-street-map")
fig_loc.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}, dragmode="select", hovermode=False
)
fig_loc.update_traces(unselected={"marker": {"opacity": 0.2}})

# table
table_header = [html.Thead(html.Tr([html.Th("Place Name"), html.Th("Actions")]))]

places = [{"name": "place 1"}]


def get_row(place):
    return html.Tr([html.Td(place["name"]), html.Td("actions")])


def get_table_body(places):
    return [html.Tbody(list(map(get_row, places)))]


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    generate_item(
                        title="Working places on a map",
                        children=dcc.Graph(
                            id="map-interactions",
                            figure=fig_loc,
                            style={"height": "calc(100% - 44px)"},
                        ),
                    ),
                    width=6,
                ),
                dbc.Col(
                    generate_item(
                        title="My working places",
                        children=dbc.Table(
                            table_header + get_table_body(places), bordered=True
                        ),
                    ),
                    width=6,
                ),
            ],
            class_name="h-50",
        ),
        dbc.Row(
            [
                dbc.Col(
                    generate_item(
                        title="Entire time spent at Our Lab",
                        children=dcc.Graph(id="entire-chart"),
                    ),
                    width=6,
                ),
                dbc.Col(
                    generate_item(
                        title="Daily time spent at Our Lab",
                        children=dcc.Graph(id="daily-chart"),
                    ),
                    width=6,
                ),
            ],
            class_name="h-50",
        ),
    ],
    class_name="h-100",
)


def grouper(list_, threshold):
    list_.sort()
    prev = None
    group = []
    for item in list_:
        if not prev or item - prev <= threshold:
            group.append(item)
        else:
            yield group
            group = [item]
        prev = item
    if group:
        yield group


def get_still_time(df):
    still_time = 0
    if not isinstance(df, pd.DataFrame):
        return still_time
    df = df.drop_duplicates(["timestamp", "transitionType"], keep="first")
    df = df.loc[df["transitionType"].isin(["ENTER_STILL", "EXIT_STILL"])]
    for idx, row in df.iterrows():
        if row["transitionType"] == "ENTER_STILL":
            enter_still_time = row["timestamp"]
        elif row["transitionType"] == "EXIT_STILL":
            exit_still_time = row["timestamp"]
            if enter_still_time in locals():
                still_time = still_time + exit_still_time - enter_still_time

    return still_time


def get_screen_time(df):
    screen_time = 0
    if not isinstance(df, pd.DataFrame):
        return screen_time
    df = df.drop_duplicates(["timestamp", "type"], keep="first")
    df = df.loc[df["type"].isin(["SCREEN_ON", "SCREEN_OFF"])]
    for idx, row in df.iterrows():
        if row["type"] == "SCREEN_ON":
            screen_on_time = row["timestamp"]
        elif row["type"] == "SCREEN_OFF":
            screen_off_time = row["timestamp"]
            if screen_on_time in locals():
                screen_time = screen_time + screen_off_time - screen_on_time

    return screen_time


@app.callback(
    Output("entire-chart", "figure"), Input("map-interactions", "selectedData")
)
def update_entire_chart(selectedData):
    # if selectedData is None:
    #     return
    # timestamp_list = list(
    #     map(lambda point: int(point["hovertext"]), selectedData.get("points"))
    # )
    # timestamp_range = list(
    #     map(
    #         lambda stamp: [
    #             min(stamp),
    #             max(stamp),
    #         ],
    #         grouper(timestamp_list, 1000 * 60 * 60 * 10),
    #     )
    # )
    # # print(len(timestamp_range), timestamp_range)
    # total_still_time = 0
    # total_screen_time = 0
    # total_time = 0
    # for range in timestamp_range:
    #     total_time = total_time + range[1] - range[0]
    #     df_act_place = df_act[df_act["timestamp"].between(range[0], range[1])]
    #     df_dev_place = df_dev[df_dev["timestamp"].between(range[0], range[1])]
    #     total_still_time = total_still_time + get_still_time(df_act_place)
    #     total_screen_time = total_screen_time + get_screen_time(df_dev_place)
    # # 여기 나중에 해결하기
    # print(total_time / (1000 * 60 * 60))
    # print(total_still_time / (1000 * 60 * 60))
    # print(total_screen_time / (1000 * 60 * 60))
    # focus_time = total_still_time - total_screen_time
    # leisure_time = total_time - total_still_time
    # wasting_time = total_screen_time
    df_entire = pd.DataFrame(
        pd.Series(
            {
                "Focus Time": 24.2,
                "Wasting Time": 4.2,
                "Leisure Time": 6.5,
            }
        ),
        columns=["time"],
    )
    fig = go.Figure(
        data=[go.Pie(labels=df_entire.index, values=df_entire["time"], sort=False)]
    )
    fig.update_traces(
        marker=dict(colors=["#0D6EFD", "#DC3545", "#ADB5BD"]),
        textinfo="percent+label",
        showlegend=False,
    )
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 100},
    )
    # pie 차트 안 나옴
    return fig


@app.callback(
    Output("daily-chart", "figure"), Input("map-interactions", "selectedData")
)
def update_daily_chart(selectedData):
    # if selectedData is None:
    #     return
    # timestamp_list = list(
    #     map(lambda point: int(point["hovertext"]), selectedData.get("points"))
    # )
    # timestamp_range = list(
    #     map(
    #         lambda stamp: [
    #             pd.to_datetime(min(stamp), unit="ms"),
    #             pd.to_datetime(max(stamp), unit="ms"),
    #         ],
    #         grouper(timestamp_list, 1000 * 60 * 60 * 10),
    #     )
    # )
    # print(timestamp_range)
    datetime_range = pd.date_range(start="2021-4-5", end="2021-4-10")
    df_daily = pd.DataFrame(
        {
            "day": datetime_range,
            "Working Time": np.random.uniform(5, 10, size=(len(datetime_range),)),
            "Wasting Time": np.random.uniform(0, 2, size=(len(datetime_range),)),
            "Leisure Time": np.random.uniform(1, 4, size=(len(datetime_range),)),
        }
    )
    fig = go.Figure()
    df_total_time = (
        df_daily["Working Time"] + df_daily["Wasting Time"] + df_daily["Leisure Time"]
    )
    df_working_ratio = df_daily["Working Time"] / df_total_time * 100
    fig.add_trace(
        go.Bar(
            x=df_daily["day"],
            y=df_daily["Working Time"],
            name="Working Time",
            textfont={"size": 11},
            text=df_daily["Working Time"].round(1).astype(str)
            + "h<br>("
            + df_working_ratio.round(1).astype(str)
            + "%)",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_daily["day"],
            y=df_daily["Wasting Time"],
            name="Wasting Time",
            marker_color="#DC3545",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_daily["day"],
            y=df_daily["Leisure Time"],
            name="Leisure Time",
            marker_color="#ADB5BD",
            text=df_total_time.round(1).astype(str) + "h",
            textposition="outside",
        )
    )
    fig.update_layout(barmode="stack", margin={"r": 0, "t": 0, "l": 0, "b": 100})

    return fig
