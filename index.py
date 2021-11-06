import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

from app import app
from apps import app_usage, working_time, suggestion, index_page

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

NAVBAR_STYLE = {
    "margin-left": "16rem",
    "background-color": "#EBE5FC",
    "display": "flex",
}

CONTENT_STYLE = {
    "margin-left": "16rem",
    "padding": "1rem 1rem",
    "height": "calc(100vh - 56px)",
}

sidebar = html.Div(
    [
        dcc.Link(
            "FocusMore",
            href="/",
            className="h3",
            style={"text-decoration": "none", "color": "black"},
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavItem(
                    dbc.NavLink("Working Time", href="/working_time", active="exact")
                ),
                dbc.NavItem(
                    dbc.NavLink("App Usage Pattern", href="/app_usage", active="exact")
                ),
                dbc.NavItem(
                    dbc.NavLink("Suggestion", href="/suggestion", active="exact")
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

navbar2 = dbc.NavbarSimple(
    children=[
        html.P("Username:"),
        dcc.Dropdown(
            id="user-dropdown",
            options=[{"label": "P0701", "value": "P0701"}],
            value="P0701",
            searchable=False,
            clearable=False,
            style={"width": "100px"},
        ),
    ],
    id="page-title",
    brand="",
    color="primary",
    dark=True,
    style=NAVBAR_STYLE,
)


navbar = html.Div(
    [
        html.Div(className="ms-2 my-auto h4", id="page-title"),
        html.Div(
            [
                html.P("Username:", className="my-auto mx-2"),
                dcc.Dropdown(
                    id="user-dropdown",
                    options=[{"label": "P0701", "value": "P0701"}],
                    value="P0701",
                    searchable=False,
                    clearable=False,
                    style={"width": "100px"},
                ),
                html.P("Date Range:", className="my-auto mx-2"),
                dcc.DatePickerRange(id="date-picker-range"),
            ],
            className="d-flex ms-auto align-items-center",
        ),
    ],
    style=NAVBAR_STYLE,
)


content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), sidebar, navbar, content],
    style={"height": "100vh"},
)


@app.callback(
    [Output("page-title", "children"), Output("page-content", "children")],
    [Input("url", "pathname")],
)
def render_page_content(pathname):
    if pathname == "/":
        return ["Index", index_page.layout]
    elif pathname == "/working_time":
        return ["Working time", working_time.layout]
    elif pathname == "/app_usage":
        return ["App Usage", app_usage.layout]
    elif pathname == "/suggestion":
        return ["Suggestion", suggestion.layout]
    return dbc.Container(
        [
            html.H1("404: Not found", className="display-3"),
            html.Hr(className="my-2"),
            html.P(f"There is no page for pathname {pathname}"),
        ],
        fluid=True,
        className="py-3",
    )


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
