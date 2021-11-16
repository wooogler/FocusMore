import dash
import dash_bootstrap_components as dbc
const PORT = proceess.env.PORT || '8080'

app.set("port", PORT)
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
