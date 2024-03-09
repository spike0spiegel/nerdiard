import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)


df = pd.read_csv("merged.csv")

print(df[:5])
#----------------------------------------------
app.layout = html.Div([
    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id='slct_year',
                 options=[
                    {'label': '2015', 'value': 2015},
                    {'label': '2016', 'value': 2016},
                    {'label': '2015', 'value': 2017},
                    {'label': '2015', 'value': 2018}],
                 multi=False,
                 value=2015,
                 style={'width': '40%'}),

    html.Div(id='output_container',children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={})

])
#------------------------------
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen by user was: {}".format(option_slctd)

    dff = df.copy()
    dff = dff[dff['Year'] == option_slctd]
    dff = dff[dff['Affected by'] == 'Varroasfsf']

    #plotly express
#------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)