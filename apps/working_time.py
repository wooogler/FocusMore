from collections import defaultdict
from datetime import datetime, timedelta, date
from dash import dcc, html, State, Output, Input, callback_context
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from app import app
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import glob


def generate_item(title, children="children", id="title"):
    return html.Div([html.H4(title, id=id), children], style={"height": "100%"})


df_act = pd.read_csv("data/PhysicalActivityTransitionEntity-5572736000.csv")
df_dev = pd.read_csv("data/DeviceEventEntity-5572736000.csv")

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
                        title="",
                        children=dcc.Graph(
                            id="location-map",
                            style={"height": "calc(100% - 44px)"},
                        ),
                    ),
                    width=6,
                ),
                dbc.Col(
                    generate_item(
                        title="My working places",
                        children=html.Div(
                            [
                                dcc.Input(id="place-name-state", type="text"),
                                html.Button(id="add-place-state", children="Add"),
                                html.Button(id="delete-place", children="Delete"),
                                dcc.RadioItems(
                                    options=[],
                                    id="place-select",
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                    },
                                    inputStyle={
                                        "marginRight": "1rem",
                                        "marginTop": "0.5rem",
                                    },
                                ),
                            ]
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
                        title="Please select your working places above",
                        children=dcc.Graph(id="entire-chart"),
                        id="entire-title",
                    ),
                    width=6,
                ),
                dbc.Col(
                    generate_item(
                        title="Please select your working places above",
                        children=dcc.Graph(id="daily-chart"),
                        id="daily-title",
                    ),
                    width=6,
                ),
            ],
            class_name="h-50",
        ),
    ],
    class_name="h-100",
)


@app.callback(
    [Output("places", "data"), Output("place-select", "options")],
    Input("add-place-state", "n_clicks"),
    Input("delete-place", "n_clicks"),
    State("place-name-state", "value"),
    Input("places", "data"),
    State("place-select", "value"),
)
def on_add_place(add_btn, delete_btn, place_name, places, selected_place):
    # if place_name == "" or place_name is None:
    #     raise PreventUpdate

    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    places = places or []

    if button_id == "add-place-state":
        if place_name not in places:
            places.append(place_name)

    elif button_id == "delete-place":
        if selected_place in places:
            places.remove(selected_place)

    options = [
        {"label": place, "value": place} for place in places if place is not None
    ]

    return [places, options]


@app.callback(
    Output("place-areas", "data"),
    Input("location-map", "selectedData"),
    State("place-select", "value"),
    Input("place-areas", "data"),
)
def update_place_areas(selectedData, selected_place, place_areas):
    place_areas = place_areas or {}
    if selected_place is not None:
        place_areas[selected_place] = selectedData
    return place_areas


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


@app.callback(
    [
        Output("location-map", "figure"),
        Output("location-map", "selectedData"),
    ],
    Input("user-dropdown", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("place-select", "value"),
    State("place-areas", "data"),
)
def update_map(user_name, start_date, end_date, selected_place, place_areas):
    loc_files = glob.glob(
        os.path.join(os.getcwd(), "user_data", user_name, "LocationEntity-*.csv")
    )
    df_loc_files = (pd.read_csv(f) for f in loc_files)
    df_loc = pd.concat(df_loc_files, ignore_index=True)
    df_loc = df_loc.sort_values(["timestamp"])
    df_loc = extract_df(df_loc, start_date, end_date)

    fig_loc = px.scatter_mapbox(
        lat=df_loc.latitude,
        lon=df_loc.longitude,
        hover_name=pd.to_datetime(df_loc.timestamp, unit="ms"),
        zoom=13,
    )
    fig_loc.update_layout(mapbox_style="open-street-map")
    fig_loc.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        dragmode="pan",
        modebar=dict(activecolor="red"),
    )
    fig_loc.update_traces(selected={"marker": {"opacity": 0.2, "color": "red"}})
    selectedData = None
    if selected_place is not None and selected_place in place_areas:
        selectedData = place_areas[selected_place]
        selectedpoints = [x["pointIndex"] for x in selectedData["points"]]
        fig_loc.update_traces(selectedpoints=selectedpoints)

    fig_loc["layout"]["uirevision"] = user_name

    return [fig_loc, selectedData]


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


def divide_time_ranges_into_date(time_ranges):
    time_ranges_dict = defaultdict(list)
    for range in time_ranges:
        time_ranges_dict[
            datetime.utcfromtimestamp(range[0] / 1000).strftime("%Y-%m-%d")
        ].append(range)
    return time_ranges_dict


def ranges_to_time(ranges):
    time = 0
    for range in ranges:
        time = time + range[1] - range[0]
    return time / (1000 * 60 * 60)


@app.callback(
    [Output("entire-title", "children"), Output("daily-title", "children")],
    Input("place-select", "value"),
)
def update_chart_title(place):
    if place is None:
        return ["", "Please select your working places above"]

    return [
        "Total time spent at {}".format(place),
        "Daily time spent at {}".format(place),
    ]


@app.callback(
    [
        Output("entire-chart", "figure"),
        Output("daily-chart", "figure"),
        Output("entire-chart", "style"),
        Output("daily-chart", "style"),
    ],
    Input("location-map", "selectedData"),
    Input("user-dropdown", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
)
def update_chart(selectedData, user_name, start_date, end_date):
    if selectedData is None:
        return [
            {},
            {},
            {"display": "none"},
            {"display": "none"},
        ]
    # timestamp_list = list(
    #     map(lambda point: int(point["hovertext"]), selectedData.get("points"))
    # )
    timestamp_list = list(
        map(
            lambda point: datetime.fromisoformat(point["hovertext"]).timestamp() * 1000,
            selectedData.get("points"),
        )
    )
    timestamp_ranges = list(
        map(
            lambda stamp: [min(stamp), max(stamp)],
            grouper(timestamp_list, 1000 * 60 * 60 * 4),
        )
    )
    act_files = glob.glob(
        os.path.join(
            os.getcwd(), "user_data", user_name, "PhysicalActivityEventEntity-*.csv"
        )
    )
    df_act_files = (pd.read_csv(f) for f in act_files)
    df_act = pd.concat(df_act_files, ignore_index=True)
    df_act = df_act.sort_values(["confidence"]).drop_duplicates(
        ["timestamp"], keep="last"
    )
    df_act = df_act.sort_values(["timestamp"]).reset_index(drop=True)
    df_act = extract_df(df_act, start_date, end_date)

    dev_files = glob.glob(
        os.path.join(os.getcwd(), "user_data", user_name, "DeviceEventEntity-*.csv")
    )
    df_dev_files = (pd.read_csv(f) for f in dev_files)
    df_dev = pd.concat(df_dev_files, ignore_index=True)
    df_dev = df_dev.drop_duplicates(["timestamp", "type"], keep="first")
    df_dev = df_dev.loc[df_dev["type"].isin(["SCREEN_ON", "SCREEN_OFF"])]
    df_dev = df_dev.sort_values(["timestamp"]).reset_index(drop=True)
    df_dev = extract_df(df_dev, start_date, end_date)

    total_still_time = 0
    total_not_still_time = 0
    still_time_ranges = []
    not_still_time_ranges = []
    for range in timestamp_ranges:
        df_act_place = df_act[df_act["timestamp"].between(range[0], range[1])]
        still_start = -1
        not_still_start = -1
        for index, row in df_act_place.iterrows():
            if df_act.loc[index - 1].type != "STILL" and row["type"] == "STILL":
                still_start = row["timestamp"]
            elif df_act.loc[index - 1].type == "STILL" and row["type"] != "STILL":
                still_end = row["timestamp"]
                if still_start != -1:
                    still_time_ranges.append([still_start, still_end])
                    total_still_time = total_still_time + still_end - still_start
                    still_start = -1

            if df_act.loc[index - 1].type == "STILL" and row["type"] != "STILL":
                not_still_start = row["timestamp"]
            elif df_act.loc[index - 1].type != "STILL" and row["type"] == "STILL":
                not_still_end = row["timestamp"]
                if not_still_start != -1:
                    not_still_time_ranges.append([not_still_start, not_still_end])
                    total_not_still_time = (
                        total_not_still_time + not_still_end - not_still_start
                    )
                    not_still_start = -1

    screen_on_time_ranges = []
    total_screen_on_time = 0
    for range in still_time_ranges:
        df_dev_still = df_dev[df_dev["timestamp"].between(range[0], range[1])]
        on_start = -1
        for index, row in df_dev_still.iterrows():
            if (
                df_dev.loc[index - 1].type == "SCREEN_OFF"
                and row["type"] == "SCREEN_ON"
            ):
                on_start = row["timestamp"]
            elif (
                df_dev.loc[index - 1].type == "SCREEN_ON"
                and row["type"] == "SCREEN_OFF"
            ):
                on_end = row["timestamp"]
                if on_start != -1:
                    screen_on_time_ranges.append([on_start, on_end])
                    total_screen_on_time = total_screen_on_time + on_end - on_start
                    on_start = -1

    focus_time = total_still_time / (1000 * 60 * 60) - total_screen_on_time / (
        1000 * 60 * 60
    )
    wasting_time = total_screen_on_time / (1000 * 60 * 60)
    leisure_time = total_not_still_time / (1000 * 60 * 60)

    df_entire = pd.DataFrame(
        pd.Series(
            {
                "Focus Time": focus_time,
                "Wasting Time": wasting_time,
                "Leisure Time": leisure_time,
            }
        ),
        columns=["time"],
    )
    fig_entire = go.Figure(
        data=[go.Pie(labels=df_entire.index, values=df_entire["time"], sort=False)]
    )
    fig_entire.update_traces(
        marker=dict(colors=["#0D6EFD", "#DC3545", "#ADB5BD"]),
        textinfo="percent+label",
        showlegend=False,
    )
    fig_entire.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 100},
    )

    still_dict = divide_time_ranges_into_date(still_time_ranges)

    not_still_dict = divide_time_ranges_into_date(not_still_time_ranges)
    screen_on_dict = divide_time_ranges_into_date(screen_on_time_ranges)

    date_range = sorted(list(still_dict.keys()))
    if len(date_range) == 0:
        return [
            {},
            {},
            {"display": "none"},
            {"display": "none"},
        ]
    datetime_range = pd.date_range(start=date_range[0], end=date_range[-1])
    df_daily = pd.DataFrame(
        {
            "day": datetime_range,
            "Working Time": [
                ranges_to_time(still_dict[date.strftime("%Y-%m-%d")])
                - ranges_to_time(screen_on_dict[date])
                for date in datetime_range
            ],
            "Wasting Time": [
                ranges_to_time(screen_on_dict[date.strftime("%Y-%m-%d")])
                for date in datetime_range
            ],
            "Leisure Time": [
                ranges_to_time(not_still_dict[date.strftime("%Y-%m-%d")])
                for date in datetime_range
            ],
        }
    )
    fig_daily = go.Figure()
    df_total_time = (
        df_daily["Working Time"] + df_daily["Wasting Time"] + df_daily["Leisure Time"]
    )
    df_working_ratio = df_daily["Working Time"] / df_total_time * 100
    fig_daily.add_trace(
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
    fig_daily.add_trace(
        go.Bar(
            x=df_daily["day"],
            y=df_daily["Wasting Time"],
            name="Wasting Time",
            marker_color="#DC3545",
        )
    )
    fig_daily.add_trace(
        go.Bar(
            x=df_daily["day"],
            y=df_daily["Leisure Time"],
            name="Leisure Time",
            marker_color="#ADB5BD",
            text=df_total_time.round(1).astype(str) + "h",
            textposition="outside",
        )
    )
    fig_daily.update_layout(barmode="stack", margin={"r": 0, "t": 0, "l": 0, "b": 100})

    return [fig_entire, fig_daily, {"display": "block"}, {"display": "block"}]
