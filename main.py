import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from datetime import datetime as dt
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# model
from model import prediction
from sklearn.svm import SVR

app = dash.Dash(__name__, external_stylesheets=['assets/styles.css'])
server = app.server

# Define the layout components

# Navigation component
item1 = html.Div(
    [
        html.P("-Welcome to the Stock Predictor with Dash -", className="start"),
        html.Div([
            # stock code input
            dcc.Input(id='stock-code', type='text', placeholder='Enter stock name', className="input-field"),
            html.Button('Submit', id='submit-button', className="button")
        ], className="stock-input"),

        html.Div([
            # Date range picker input
            dcc.DatePickerRange(
                id='date-range', start_date=dt(2024, 1, 1).date(), end_date=dt.now().date(), className='date-input'
            )
        ], className="date-picker"),

        html.Div([
            # Stock price button
            html.Button('Get Stock Price', id='stock-price-button', className="button"),

            # Number of days of forecast input
            dcc.Input(id='forecast-days', type='number', placeholder='Enter number of days', className="input-field"),

            # Forecast button
            html.Button('Get Forecast', id='forecast-button', className="button")
        ], className="selectors"),

    ],
    className="nav"
)

# Content component
item2 = html.Div(
    [
        html.Div(
            [
                html.Img(id='logo', className='logo'),
                html.H1(id='company-name', className='company-name')
            ],
            className="header"),
        html.Div(id="description", className="description"),
        html.Div([], id="graphs-content", className="graphs"),
        html.Div([], id="forecast-content", className="forecast")
    ],
    className="content"
)

# Set the layout
app.layout = html.Div(className='container', children=[item1, item2])

# Callbacks

# Callback to update the data based on the submitted stock code
@app.callback(
    [
        Output("description", "children"),
        Output("logo", "src"),
        Output("company-name", "children"),
        Output("stock-price-button", "n_clicks"),
        Output("forecast-button", "n_clicks")
    ],
    [Input("submit-button", "n_clicks")],
    [State("stock-code", "value")]
)
def update_data(n, val):
    if n is None:
        return None, None, None, None, None
    else:
        if val is None:
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            inf = ticker.info
            if 'logo_url' not in inf:
                return None, None, None, None, None
            else:
                name = inf['longName']
                logo_url = inf['logo_url']
                description = inf['longBusinessSummary']
                return description, logo_url, name, None, None


# Callback for displaying stock price graphs
@app.callback(
    [Output("graphs-content", "children")],
    [
        Input("stock-price-button", "n_clicks"),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date')
    ],
    [State("stock-code", "value")]
)
def stock_price(n, start_date, end_date, val):
    if n is None:
        return [""]
    if val is None:
        raise PreventUpdate
    else:
        if start_date is not None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = px.line(df, x="Date", y=["Close", "Open"], title="Closing and Opening Price vs Date")
    return [dcc.Graph(figure=fig)]

# Callback for displaying forecast
@app.callback(
    [Output("forecast-content", "children")],
    [Input("forecast-button", "n_clicks")],
    [State("forecast-days", "value"),
     State("stock-code", "value")]
)
def forecast(n, n_days, val):
    if n is None:
        return [""]
    if val is None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)
