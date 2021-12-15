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
import numpy as np
import time

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
    dfs = (pd.read_csv(f) for f in files)
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values(["timestamp"])
    return df


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


def get_hour(ts):
    return (pd.to_datetime(ts, unit="ms").hour) // 2 * 2 + 1


fig1 = go.Figure()

fig2 = go.Figure(
    data=go.Pie(labels=["No Data"], values=[100], marker=dict(colors=["lightgray"]))
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
                                            "Click each colored slot to check app usage percentage.",
                                        ]
                                    ),
                                    html.P(
                                        [], id='direction'
                                    )
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
    Output("direction", "children"),
    Input("places","data")
)
def give_direction(places):
    chd=[html.B(["Please select your working spaces ", html.A(["here"], href="/working_time")])]
    if places is None:
        return chd
    if len(places)<=1:
        return chd
@app.callback(
    [Output("appPie", "figure"), Output("heatmap", "figure")],
    Input("heatmap", "clickData"),
    Input("user-dropdown", "value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("places", "data"),
    Input("place-areas", "data"),
)
def update_pie(clickData, user_name, start_date, end_date, place_names, place_areas):
    ##overall data##
    # in response to username change
    app_files = glob.glob(
        os.path.join(os.getcwd(), "user_data", user_name, "AppUsageStatEntity-*.csv")
    )
    loc_files = glob.glob(
        os.path.join(os.getcwd(), "user_data", user_name, "LocationEntity-*.csv")
    )
    phy_files = glob.glob(
        os.path.join(
            os.getcwd(), "user_data", user_name, "PhysicalActivityEventEntity-*.csv"
        )
    )
    dev_files = glob.glob(
        os.path.join(os.getcwd(), "user_data", user_name, "DeviceEventEntity-*.csv")
    )
    app_df = files_to_df(app_files)
    app_df["time"] = pd.to_datetime(app_df["timestamp"], unit="ms")
    app_df = extract_df(app_df, start_date, end_date)
    loc_df = files_to_df(loc_files)
    loc_df["time"] = pd.to_datetime(loc_df["timestamp"], unit="ms")
    loc_df = extract_df(loc_df, start_date, end_date)
    phy_df = files_to_df(phy_files)
    phy_df["time"] = pd.to_datetime(phy_df["timestamp"], unit="ms")
    phy_df = extract_df(phy_df, start_date, end_date)
    phy_df = phy_df.sort_values(["confidence"]).drop_duplicates(
        ["timestamp"], keep="last"
    )
    phy_df = phy_df.sort_values(["timestamp"]).reset_index(drop=True)
    dev_df = files_to_df(dev_files)
    dev_df["time"] = pd.to_datetime(phy_df["timestamp"], unit="ms")
    dev_df=extract_df(phy_df, start_date, end_date)
    dev_df=dev_df.drop_duplicates(["timestamp","type"], keep="first")
    dev_df=dev_df.loc[dev_df["type"].isin(["SCREEN_ON", "SCREEN_OFF"])]
    dev_df=dev_df.sort_values(["timestamp"]).reset_index(drop=True)
    
    hours=list(range(1,24,2))
    zeros=[0]*12
    place_on=[]
    phy_df["isStill"]=phy_df["type"].apply(lambda t: t=="STILL")
    dev_df["isOn"]=dev_df["type"].apply(lambda t: t=="SCREEN_ON")
    
    heatFig=go.Figure()
    zip_dfs=[]
    if len(place_names)<=1:
        heatFig.update_layout(title="Please select working places in [Working Time] page.")
    loc_time=dict()
    
    for place in [name for name in place_names if name is not None]:
        pts=place_areas[place]["points"]
        if len(pts)==0:
            continue
        timestamp_list=list(
            map(lambda pt: int(time.mktime(datetime.strptime(pt["hovertext"][:19], '%Y-%m-%dT%H:%M:%S').timetuple())*1000), pts)
        )
        timestamp_ranges = list(
            map(
                lambda stamp: [min(stamp), max(stamp)],
                grouper(timestamp_list, 1000 * 60 * 60 * 4),
            )
        )
        loc_time[place]=timestamp_ranges
        still_time_ranges=[]
        hour_placeTime=dict(zip(hours, zeros))
        hour_stillTime=dict(zip(hours, zeros))
        for r in timestamp_ranges:
            phy_df_place = phy_df.loc[phy_df["timestamp"].between(r[0], r[1])]
            r_start_h=get_hour(r[0])
            r_end_h=get_hour(r[1])
            if (r_start_h==r_end_h):
                hour_placeTime[r_start_h] += r[1] - r[0]
            else:
                hdelta=r_end_h-r_start_h
                st=pd.to_datetime(r[0], unit='ms')
                et=pd.to_datetime(r[1], unit='ms')
                sh=st.hour
                sm=st.minute
                eh=et.hour
                em=et.minute
                m1=((r_start_h+2-sh)*60-sm)*1000*60
                m2=((r_end_h-eh)*60-em)*1000*60
                hour_placeTime[r_start_h]+=m1
                hour_placeTime[r_end_h]+=m2
                if hdelta>2:
                    for i in range(2,hdelta,2):
                        hour_placeTime[r_start_h+i]+=1000*60*2
                elif hdelta<0:
                    hdelta=r_end_h+24-r_start_h
                    if hdelta>2:
                        for i in range(2,hdelta,2):
                            hour_placeTime[(r_start_h+i)%24]+=1000*60*2
                    
            still_start=-1
            for index, row in phy_df_place.iterrows():
                prev = phy_df.loc[index - 1].isStill
                curr = row["isStill"]
                if (not prev) and curr:
                    still_start = row["timestamp"]
                elif prev and (not curr):
                    still_end = row["timestamp"]
                    if still_start != -1:
                        still_time_ranges.append([still_start, still_end])
                        still_start_hour=get_hour(still_start)
                        still_end_hour=get_hour(still_end)
                        
                        if still_start_hour==still_end_hour:
                            hour_stillTime[still_start_hour] += still_end-still_start
                        else:
                            hdelta=still_end_hour-still_start_hour
                            st=pd.to_datetime(still_start,unit='ms')
                            et=pd.to_datetime(still_end, unit='ms')
                            sh=st.hour
                            sm=st.minute
                            eh=et.hour
                            em=et.minute
                            m1=((still_start_hour+2-sh)*60-sm)*1000*60
                            m2=((still_end_hour-eh)*60+em)*1000*60
                            hour_stillTime[still_start_hour]+=m1
                            hour_stillTime[still_end_hour]+=m2
                            if hdelta>2:
                                for i in range(2,hdelta+2,2):
                                    hour_stillTime[still_start_hour+i]+=1000*60*2
                            # elif hdelta<0:
                        still_start=-1
        hour_onTime = dict(zip(hours, zeros))
        for r in still_time_ranges:
            dev_df_still = dev_df.loc[dev_df["timestamp"].between(r[0], r[1])]
            on_start = -1
            for index, row in dev_df_still.iterrows():
                prev = dev_df.loc[index - 1].isOn
                curr = row["isOn"]
            if (not prev) and curr:
                on_start = row["timestamp"]
            elif prev and (not curr):
                on_end = row["timestamp"]
                if on_start != -1:
                    on_start_hour = get_hour(on_start)
                    on_end_hour = get_hour(on_end)
                    if on_start_hour == on_end_hour:
                        hour_onTime[on_start_hour] += on_end - on_start
                    else:
                        hdelta=on_end_hour-on_start_hour
                        st=pd.to_datetime(on_start,unit='ms')
                        et=pd.to_datetime(on_end, unit='ms')
                        sh=st.hour
                        sm=st.minute
                        eh=et.hour
                        em=et.minute
                        m1=((on_start_hour+2-sh)*60-sm)*1000*60
                        m2=((eh-on_end_hour)*60+em)*1000*60
                        hour_onTime[on_start_hour]+=m1
                        hour_onTime[on_end_hour]+=m2
                        
                        if hdelta>2:
                            for i in range(2,hdelta,2):
                                hour_onTime[on_start_hour+i]+=1000*60*2
                        #elif hdelta<0:
                    on_start=-1
        place_on.append(hour_onTime)
        place_rate=[]
        for k in list(hour_placeTime.keys()):
            if hour_placeTime[k]!=0:
                rate=(hour_stillTime[k]-hour_onTime[k])/hour_placeTime[k]*100
                place_rate.append(rate%100)
            else:
                place_rate.append(None)
        place12=[place]*12
        zip_df=pd.DataFrame(list(zip(hours, place12, place_rate)), columns=['time','place','rate'])
        zip_dfs.append(zip_df)
    heat_df = pd.concat(zip_dfs, ignore_index=True)
    heatFig = go.Figure(
        data=go.Heatmap(
            x=heat_df.time,
            y=heat_df.place,
            z=heat_df.rate,
            hovertemplate="%{y}<br>" + "%{z:d}%<extra></extra>",
            colorscale="Purp",
            zmin=0,
            zmax=100,
        )
    )
    heatFig.update_layout(
        title="Focus time rate = Focus time/Total time spent", title_x=0.5
    )
    heatFig.update_xaxes(dtick=2, title_text="time(h)")
    heatFig.update_yaxes(title_text="place")
    app_df = app_df.loc[:, ["time", "timestamp", "name", "totalTimeForeground"]]
    app_byname = app_df.groupby(["name"])

    if clickData is not None:  # in response to heatmap click
        
        locationName = clickData["points"][0]["y"]
        timeMid = clickData["points"][0]["x"]
        timeStart = timeMid - 1
        timeEnd = timeMid + 1
        app_df = app_df.loc[
            (app_df["time"].dt.hour >= timeStart) & (app_df["time"].dt.hour < timeEnd)
        ]
        if app_df.size==0 or clickData["points"][0]["z"] is None:
            pieFig=fig2
        else:
            df_start_date = min(app_df["time"]).date()
            df_end_date = max(app_df["time"]).date()
            day_length = (df_end_date - df_start_date).days + 1
            day_delta = pd.to_timedelta(np.arange(day_length), unit="d")
            dates = np.repeat(np.array([df_start_date]), day_length)
            dates += day_delta
            dates=dates.tolist()
            dates = list(map(lambda x: pd.to_datetime(x), dates))
            app_time = []
            loc_timerange=loc_time[locationName]
            for t in loc_timerange:
                tmin=t[0]
                tmax=t[1]
                tmin_dt=pd.to_datetime(tmin, unit='ms')
                tmax_dt=pd.to_datetime(tmax, unit='ms')
                if (tmin_dt.hour>timeEnd or tmax_dt.hour<timeStart):
                    continue
                time_app = app_df.loc[
                    (app_df["time"] >= tmin_dt) & (app_df["time"]<=tmax_dt)
                ]
                time_byApp = (
                    time_app.groupby(["name"]).max() - time_app.groupby(["name"]).min()
                )    
                time_byApp.reset_index(level=["name"], inplace=True)
                for index, row in time_byApp.iterrows():
                    name=row["name"]
                    totalTimeForeground = row["totalTimeForeground"]
                    app_time.append([name, totalTimeForeground])
            # for d in dates:
            #     date_app = app_df.loc[
            #         (app_df["time"] >= d) & (app_df["time"] < d + timedelta(days=1))
            #     ]
            #     date_byApp = (
            #         date_app.groupby(["name"]).max() - date_app.groupby(["name"]).min()
            #     )
            #     date_byApp.reset_index(level=["name"], inplace=True)
            #     for index, row in date_byApp.iterrows():
            #         name = row["name"]
            #         totalTimeForeground = row["totalTimeForeground"]
            #         app_time.append([name, totalTimeForeground])
            
            pie_df = pd.DataFrame(app_time, columns=["name", "totalTimeForeground"])

            aggrByApp = pie_df.groupby(["name"]).sum()
            print(aggrByApp.size)
            print(aggrByApp.head())
            if (aggrByApp.size > 0):
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
                top5app["totalMin"] = top5app["totalTimeForeground"] / 60000
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
                            sort=False,
                        )
                    ]
                )
                
                fig3.update_layout(legend=dict(orientation="h", xanchor="center", x=0.5))
                pieFig = fig3
                if top5app.size==0:
                    pieFig=fig2
            else:
                pieFig = fig2
    else:
        pieFig = fig2

    return [pieFig, heatFig]
