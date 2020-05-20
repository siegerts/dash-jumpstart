# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import numpy as np
import pandas as pd
import datetime as dt

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

parser = lambda date: pd.datetime.strptime(date, "%Y-%m-%d")

# Fetch prices from local CSV using pandas
prices = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "prices.csv"),
    # index_col=0,
    parse_dates=True,
    date_parser=parser,
)


app.layout = html.Div(
    children=[
        html.H1(children="Stock Tracker"),
        html.Div(
            children="""
        Dash: A web application framework for Python.
    """
        ),
        html.Label("Stock Symbol"),
        dcc.Dropdown(
            id="stock-ticker-select",
            options=[
                {"label": ticker, "value": ticker}
                for ticker in prices["ticker"].unique()
            ],
            multi=True,
            value=[prices["ticker"].unique()[0]],
        ),
        dcc.RadioItems(
            id="stock-ticker-price",
            options=[
                {"label": "Open", "value": "open"},
                {"label": "High", "value": "high"},
                {"label": "Low", "value": "low"},
                {"label": "Close", "value": "close"},
            ],
            value="close",
        ),
        # newdf = df.loc[(df.origin != "JFK")
        # multi filter?
        # for label in labels, type == line, name = ticker
        # x and y data points
        dcc.Graph(id="stock-price-graph",),
        # dcc.Graph(id="stock-volume-graph",),
    ]
)


@app.callback(
    Output("stock-price-graph", "figure"),
    [Input("stock-ticker-select", "value"), Input("stock-ticker-price", "value")],
)
def update__price_figure(select_tickers, price):
    # x == date
    # y == value
    return {
        "data": [
            {
                "x": [date for date in prices.loc[(prices.ticker == stock)]["date"]],
                "y": [price for price in prices.loc[(prices.ticker == stock)][price]],
                "type": "scatter",
                "mode": "lines",
                "name": f"{stock}",
                "line": {"shape": "spline", "smoothing": "5"},
            }
            for stock in select_tickers
        ],
        "layout": {"title": f"Stock Price ({(' & ').join(select_tickers)})"},
    }


if __name__ == "__main__":
    app.run_server(debug=True)
