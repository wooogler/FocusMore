from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from app import app
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="selectDay",
                            value="Day",
                            placeholder="Select Day",
                            searchable=False,
                            clearable=False,
                            style={"width": "200px", "float": "right"},
                        ),
                        html.H2("Focus Time Rate per hour per day"),
                        html.P(
                            [
                                "The focus time rate means the ratio of focus to the whole",
                                html.Br(),
                                "This graph shows the ratio of focus time per 2 hours per day. You can see when you focus more or less on this graph.",
                            ]
                        ),
                        dcc.Graph(id="FocusBar"),
                    ]
                ),
            ],
            class_name="h-35",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("Distracting Apps"),
                                    html.P(
                                        [
                                            "The top 5 apps that are used most frequently ",
                                            html.Br(),
                                            "when you have ",
                                            html.I("Low Focus Time Rate"),
                                        ]
                                    ),
                                ],
                                style={
                                    "borderColor": "#d62728",
                                    "border": " solid 0.2em",
                                    "borderRadius": "10px",
                                },
                            ),
                            dcc.Graph(id="appPie1", style={"maxWidth": "50vw"}),
                        ]
                    )
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("Not Disturbing Apps"),
                                    html.P(
                                        [
                                            "The top 5 apps that are used most frequently ",
                                            html.Br(),
                                            "when you have ",
                                            html.I("High Focus Time Rate"),
                                        ]
                                    ),
                                ],
                                style={
                                    "borderColor": "#2ca02c",
                                    "border": " solid 0.2em",
                                    "borderRadius": "10px",
                                },
                            ),
                            dcc.Graph(id="appPie2", style={"maxWidth": "50vw"}),
                        ]
                    )
                ),
            ],
            class_name="h-35",
            style={"textAlign": "center"},
        ),
    ],
    class_name="h-100",
)


@app.callback(
    Output("selectDay", "options"),
    [Input("date-picker-range", "start_date"), Input("date-picker-range", "end_date")],
)
def update_dropdown(start_date, end_date):
    return [
        {"label": i, "value": i}
        for i in pd.date_range(start_date, end_date, freq="D").format(
            formatter=lambda x: x.strftime("%Y-%m-%d")
        )
    ]


@app.callback(
    [
        Output("FocusBar", "figure"),
        Output("appPie1", "figure"),
        Output("appPie2", "figure"),
    ],
    [
        Input("user-dropdown", "value"),
        Input("date-picker-range", "start_date"),
        Input("selectDay", "value"),
    ],
)
def update_graphs(user_name, start_date, selectedDay):
    usrDir = os.path.join(os.getcwd(), "user_data", user_name)
    file_list = os.listdir(usrDir)

    ## ---- Still Time ---- ##
    actDf = []
    for filename in file_list:
        if filename.startswith("PhysicalActivityEventEntity"):
            df = pd.read_csv(os.path.join(usrDir, filename))
            df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
            actDf.append(df)
    actDf = pd.concat(actDf)
    actDf = actDf.sort_values(["timestamp"])

    idx = (
        actDf.groupby(["timestamp"])["confidence"].transform(max) == actDf["confidence"]
    )
    actDf = actDf[idx].sort_values(["timestamp"]).reset_index(drop=True)

    actDf["label"] = np.where(actDf["type"] == "STILL", 1, 0)
    actDf["hour"] = actDf["time"].dt.hour
    if selectedDay == "Day":
        actDf_byDay = actDf.loc[actDf["time"].dt.date.astype(str) == start_date]
    else:
        actDf_byDay = actDf.loc[actDf["time"].dt.date.astype(str) == selectedDay]

    actDf_byDay = actDf_byDay.reset_index(drop=True)
    actDf_byDay["hour"] = actDf_byDay["hour"].map(lambda x: (x // 2) * 2 + 2)

    still_start = actDf_byDay.timestamp.min()
    still_end = actDf_byDay.timestamp.min()
    still_times = {}
    still_inters = []

    for i, r in actDf_byDay.iterrows():

        if i == 0:
            if r["label"] == 0:
                continue
            else:
                still_start = r.timestamp
        else:
            if (r["hour"] > actDf_byDay.loc[i - 1]["hour"] and r["label"] == 1) or (
                actDf_byDay.loc[i - 1]["label"] == 0 and r["label"] == 1
            ):
                still_start = r.timestamp

            elif i == actDf_byDay.index.max():
                still_end = r.timestamp
                if r["hour"] in still_times:
                    still_times[r["hour"]].append(still_end - still_start)
                else:
                    still_times[r["hour"]] = [still_end - still_start]
                still_inters.append([still_start, still_end])
                break

            elif (r["hour"] < actDf_byDay.loc[i + 1]["hour"]) or (
                actDf_byDay.loc[i - 1]["label"] == 1 and r["label"] == 0
            ):
                still_end = r.timestamp

                if r["hour"] in still_times:
                    still_times[r["hour"]].append(still_end - still_start)
                else:
                    still_times[r["hour"]] = [still_end - still_start]
                still_inters.append([still_start, still_end])

    total_still = {}
    for key in still_times.keys():
        total_still[key] = sum(item for item in still_times[key])

    hourly_still = {}
    for key in total_still.keys():
        hourly_still[key] = total_still[key] / (1000 * 60)

    ## ---- ScreenOn Time ---- ##
    screenDf = []

    for filename in file_list:
        if filename.startswith("DeviceEventEntity"):
            df = pd.read_csv(os.path.join(usrDir, filename))
            df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
            screenDf.append(df)
    screenDf = pd.concat(screenDf)
    screenDf = screenDf.drop_duplicates(["timestamp", "type"], keep="first")
    screenDf = screenDf.loc[screenDf["type"].isin(["SCREEN_ON", "SCREEN_OFF"])]
    screenDf = screenDf.sort_values(["timestamp"])

    screenDf["hour"] = screenDf["time"].dt.hour
    if selectedDay == "Day":
        screenDf_byDay = screenDf.loc[
            screenDf["time"].dt.date.astype(str) == start_date
        ]
    else:
        screenDf_byDay = screenDf.loc[
            screenDf["time"].dt.date.astype(str) == selectedDay
        ]
    screenDf_byDay = screenDf_byDay.reset_index(drop=True)
    screenDf_byDay["hour"] = screenDf_byDay["hour"].map(lambda x: (x // 2) * 2 + 2)

    screenDf_byDay_still = []
    screen_times = {}
    screen_inters = []

    for s, t in still_inters:
        screenDf_byDay_interv = screenDf_byDay.loc[
            lambda x: x["timestamp"].between(s, t), :
        ]
        screenDf_byDay_interv = screenDf_byDay_interv.sort_values(
            "timestamp"
        ).reset_index(drop=True)

        on_start = screenDf_byDay_interv.timestamp.min()
        on_end = screenDf_byDay_interv.timestamp.min()

        for i, r in screenDf_byDay_interv.iterrows():
            if i == screenDf_byDay_interv.index.min() and r["type"] == "SCREEN_OFF":
                on_start = s
            elif i == screenDf_byDay_interv.index.max() and r["type"] == "SCREEN_ON":
                on_end = t
                if r["hour"] in screen_times:
                    screen_times[r["hour"]].append(on_end - on_start)
                else:
                    screen_times[r["hour"]] = [on_end - on_start]
                screen_inters.append([on_start, on_end])
                break

            else:
                if r["type"] == "SCREEN_ON":
                    on_start = r.timestamp
                else:
                    on_end = r.timestamp
                    if r["hour"] in screen_times:
                        screen_times[r["hour"]].append(on_end - on_start)
                    else:
                        screen_times[r["hour"]] = [on_end - on_start]
                    screen_inters.append([on_start, on_end])

        screenDf_byDay_still.append(screenDf_byDay_interv)

    screenDf_byDay_still = pd.concat(screenDf_byDay_still)
    screenDf_byDay_still = screenDf_byDay_still.sort_values("timestamp").reset_index(
        drop=True
    )

    total_on = {}
    for key in screen_times.keys():
        total_on[key] = sum(item for item in screen_times[key])

    hourly_on = {}
    for key in total_on.keys():
        hourly_on[key] = total_on[key] / (1000 * 60)

    ## ---- Focus time ratio ---- ##
    time_slots = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
    for t in time_slots:
        if t not in hourly_on.keys():
            hourly_on[t] = 0
            hourly_still[t] = 1

    focus_ratio = {}
    for key in hourly_still.keys():
        focus_ratio[key] = (hourly_on[key] / hourly_still[key]) * 100

    ratio_df = pd.DataFrame(
        {"timeslot": list(focus_ratio.keys()), "ratio": list(focus_ratio.values())}
    )

    meanVal = ratio_df["ratio"].mean()
    ratio_df["label"] = ratio_df["ratio"].apply(
        lambda x: "High" if x > meanVal else "Low"
    )
    ratio_df = ratio_df.sort_values("timeslot")

    ratio_df_high = ratio_df.loc[ratio_df["label"] == "High"]
    ratio_df_low = ratio_df.loc[ratio_df["label"] == "Low"]

    ## ---- App usage ---- ##
    appDf = []

    for filename in file_list:
        if filename.startswith("AppUsageStatEntity"):
            df = pd.read_csv(os.path.join(usrDir, filename))
            df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
            appDf.append(df)
    appDf = pd.concat(appDf)
    appDf = appDf.sort_values(["timestamp"])
    appDf = appDf.loc[:, ["time", "timestamp", "name", "totalTimeForeground"]]

    appDf["hour"] = appDf["time"].dt.hour
    if selectedDay == "Day":
        appDf_byDay = appDf.loc[appDf["time"].dt.date.astype(str) == start_date]
    else:
        appDf_byDay = appDf.loc[appDf["time"].dt.date.astype(str) == selectedDay]
    appDf_byDay = appDf_byDay.dropna()
    appDf_byDay = appDf_byDay.reset_index(drop=True)
    appDf_byDay["hour"] = appDf_byDay["hour"].map(lambda x: (x // 2) * 2 + 2)

    appDf_byDay_high = appDf_byDay.loc[
        appDf_byDay["hour"].isin(ratio_df_high["timeslot"])
    ]
    appDf_byDay_low = appDf_byDay.loc[
        appDf_byDay["hour"].isin(ratio_df_low["timeslot"])
    ]

    ## Not disturbing
    appDf_byDay_high = appDf_byDay_high.loc[:, ["name", "totalTimeForeground"]]
    highApps = appDf_byDay_high.groupby("name").sum().reset_index()
    highApps = highApps.sort_values("totalTimeForeground", ascending=False)
    highTop5 = highApps.iloc[:5]
    highEtc = highApps.iloc[5:]["totalTimeForeground"].sum()
    highTop5 = pd.concat(
        [
            highTop5,
            pd.DataFrame([["etc", highEtc]], columns=["name", "totalTimeForeground"]),
        ]
    )
    highTop5 = highTop5.reset_index(drop=True)
    highTop5["totalTime(m)"] = highTop5["totalTimeForeground"] / (1000 * 60)

    ## Distracting
    appDf_byDay_low = appDf_byDay_low.loc[:, ["name", "totalTimeForeground"]]
    lowApps = appDf_byDay_low.groupby("name").sum().reset_index()
    lowApps = lowApps.sort_values("totalTimeForeground", ascending=False)
    lowTop5 = lowApps.iloc[:5]
    lowEtc = highApps.iloc[5:]["totalTimeForeground"].sum()
    lowTop5 = pd.concat(
        [
            lowTop5,
            pd.DataFrame([["etc", lowEtc]], columns=["name", "totalTimeForeground"]),
        ]
    )
    lowTop5 = lowTop5.reset_index(drop=True)
    lowTop5["totalTime(m)"] = lowTop5["totalTimeForeground"] / (1000 * 60)
    ## ---- VISUALIZATION ---- ##

    colors = {"High": "#2ca02c", "Low": "#d62728"}
    labels = {"High": "High Focus Rate", "Low": "Low Focus Rate"}

    fig = go.Figure()

    for label, label_df in ratio_df.groupby("label"):

        fig.add_trace(
            go.Bar(
                x=label_df.timeslot,
                y=label_df.ratio,
                name=labels[label],
                marker={"color": colors[label]},
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[ratio_df.timeslot.min() - 1, ratio_df.timeslot.max() + 1],
            y=[meanVal, meanVal],
            name="Mean",
            mode="lines+text",
            # text="Mean",
            showlegend=False,
            marker={"color": "darkgray"},
        )
    )
    fig.layout.plot_bgcolor = "#fff"
    fig.layout.paper_bgcolor = "#fff"

    fig.update_layout(
        xaxis_title="Every two hour (2H)",
        yaxis_title="Focus Time Rate (%)",
    )
    fig.update_layout(yaxis_range=[0, 100])

    fig1 = go.Figure()
    fig1.add_trace(
        go.Pie(
            labels=lowTop5["name"],
            values=lowTop5["totalTime(m)"],
            textinfo="percent",
            hoverinfo="label",
            direction="clockwise",
            sort=False,
        )
    )

    fig2 = go.Figure()
    fig2.add_trace(
        go.Pie(
            labels=highTop5["name"],
            values=highTop5["totalTime(m)"],
            textinfo="percent",
            hoverinfo="label",
            direction="clockwise",
            sort=False,
        )
    )

    return [fig, fig1, fig2]
