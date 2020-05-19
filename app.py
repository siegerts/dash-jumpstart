# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import numpy as np
import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Fetch prices from local CSV using pandas
prices = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "prices.csv"),
    index_col=0,
    parse_dates=True,
)

prices = pd.read_csv(os.path.join("prices.csv"), index_col=0, parse_dates=True,)


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
        # newdf = df.loc[(df.origin != "JFK")
        # multi filter?
        # for label in labels, type == line, name = ticker
        # x and y data points
        dcc.Graph(id="stock-price-graph",),
    ]
)


@app.callback(
    Output("stock-price-graph", "figure"), [Input("stock-ticker-select", "value")]
)
def update_figure(select_tickers):
    print(select_tickers)
    return {
        "data": [
            {"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "SF"},
            {"x": [1, 2, 3], "y": [2, 4, 5], "type": "bar", "name": "Montréal",},
        ],
        "layout": {"title": f"Stock Price ({(' & ').join(select_tickers)})"},
    }


if __name__ == "__main__":
    app.run_server(debug=True)
