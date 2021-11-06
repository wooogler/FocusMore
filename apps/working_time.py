from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from app import app
import pandas as pd
import plotly.express as px
import json


def generate_item(title, children="children"):
    return html.Div([html.H4(title), children], style={"height": "100%"})


df_act = pd.read_csv(
    "data/PhysicalActivityTransitionEntity-5572736000.csv", index_col="timestamp"
)
df_act["timestamp"] = pd.to_datetime(df_act.index, unit="ms")
df_act.set_index("timestamp", drop=True, inplace=True)

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
                dbc.Col(generate_item(title="Daily time spent at Our Lab"), width=6),
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


@app.callback(
    Output("entire-chart", "figure"), Input("map-interactions", "selectedData")
)
def display_selected_data(selectedData):
    if selectedData is None:
        return
    timestamp_list = list(
        map(lambda point: int(point["hovertext"]), selectedData.get("points"))
    )
    timestamp_range = list(
        map(
            lambda stamp: [
                min(stamp),
                max(stamp),
            ],
            grouper(timestamp_list, 1000 * 60 * 60 * 10),
        )
    )
    # print(len(timestamp_range), timestamp_range)
    still_time = 0
    total_time = 0
    df_act_list = []
    for range in timestamp_range:
        # print(pd.to_datetime(range[0], unit="ms"), pd.to_datetime(range[1], unit="ms"))
        total_time = total_time + range[1] - range[0]
        # print(total_time)
        df_act_list.append(
            df_act.loc[
                pd.to_datetime(range[0], unit="ms") : pd.to_datetime(
                    range[1], unit="ms"
                )
            ]
        )
    # 여기 나중에 해결하기
    print(df_act_list)

    for df_act_item in df_act_list:
        for idx, item in df_act_item.iterrows():
            if item["transitionType"] == "ENTER_STILL":
                enter_still_timestamp = int(idx)
            elif item["transitionType"] == "EXIT_STILL":
                exit_still_timestamp = int(idx)
                still_time = still_time + (exit_still_timestamp - enter_still_timestamp)
    print(timestamp_range)
    print(still_time / (1000 * 60 * 60))
    print(total_time / (1000 * 60 * 60))
    return ""
