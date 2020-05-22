# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import numpy as np
import pandas as pd
from datetime import datetime as dt
import json

MIN_DATE = pd.Timestamp(2010, 1, 4, 0).date()
MAX_DATE = pd.Timestamp(2018, 11, 7, 0).date()


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

parser = lambda date: pd.datetime.strptime(date, "%Y-%m-%d")

# Fetch prices from local CSV using pandas
prices = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "prices.csv"),
    # index_col=0,
    parse_dates=True,
    date_parser=parser,
)
prices["date"] = pd.to_datetime(prices["date"], format="%Y-%m-%d")


app.layout = html.Div(
    [
        dbc.Navbar(
            children=[
                dbc.Row(
                    [dbc.Col(dbc.NavbarBrand("Stock Tracker", className="ml-2")),],
                    align="center",
                    no_gutters=True,
                ),
            ],
            sticky="top",
        ),
        dbc.Container(
            [
                html.Div(
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.FormGroup(
                                                [
                                                    dbc.Label("Choose a Stock Symbol"),
                                                    dcc.Dropdown(
                                                        id="stock-ticker-select",
                                                        options=[
                                                            {
                                                                "label": ticker,
                                                                "value": ticker,
                                                            }
                                                            for ticker in prices[
                                                                "ticker"
                                                            ].unique()
                                                        ],
                                                        multi=True,
                                                        value=[
                                                            prices["ticker"].unique()[0]
                                                        ],
                                                    ),
                                                ]
                                            ),
                                            dbc.FormGroup(
                                                [
                                                    dbc.Label("Price"),
                                                    dbc.Col(
                                                        dbc.RadioItems(
                                                            id="stock-ticker-price",
                                                            options=[
                                                                {
                                                                    "label": "Open",
                                                                    "value": "open",
                                                                },
                                                                {
                                                                    "label": "High",
                                                                    "value": "high",
                                                                },
                                                                {
                                                                    "label": "Low",
                                                                    "value": "low",
                                                                },
                                                                {
                                                                    "label": "Close",
                                                                    "value": "close",
                                                                },
                                                            ],
                                                            value="close",
                                                        ),
                                                        width=10,
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    dcc.Markdown(
                                                        """
                                Choose the lasso or rectangle tool in the graph's menu
                                bar and then select points in the graph.
                            
                            """
                                                    ),
                                                    html.Pre(id="selected-data"),
                                                ],
                                            ),
                                        ],
                                        body=True,
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        dcc.Graph(id="stock-price-graph", animate=True),
                                        dcc.Graph(
                                            id="stock-volume-graph", animate=True,
                                        ),
                                    ],
                                    md=8,
                                ),
                            ],
                        ),
                    ],
                    className="m-4",
                ),
            ],
            fluid=True,
        ),
    ]
)


def filter_data_by_date(df, ticker, start_date, end_date):
    if start_date is None:
        start_date = MIN_DATE

    if end_date is None:
        end_date = MAX_DATE

    filtered = df[
        (df["ticker"] == ticker) & (df["date"] >= start_date) & (df["date"] <= end_date)
    ]
    return filtered


@app.callback(
    Output("stock-price-graph", "figure"),
    [Input("stock-ticker-select", "value"), Input("stock-ticker-price", "value"),],
)
def update_price_figure(selected_tickers, price):
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
            }
            for stock in selected_tickers
        ],
        "layout": {
            "title": f"Stock Price - {price} ({(' & ').join(selected_tickers)})",
        },
    }


@app.callback(
    Output("stock-volume-graph", "figure"),
    [
        Input("stock-ticker-select", "value"),
        Input("stock-price-graph", "relayoutData"),
    ],
)
def update_volume_figure(selected_tickers, relayoutData):

    # x == date
    # y == value
    data = []
    from_date = None
    to_date = None

    if relayoutData:
        from_date = relayoutData.get("xaxis.range[0]", None)
        to_date = relayoutData.get("xaxis.range[1]", None)

        if from_date and to_date:
            from_date = pd.Timestamp(from_date)
            to_date = pd.Timestamp(to_date)

            for stock in selected_tickers:
                filtered = filter_data_by_date(prices, stock, from_date, to_date)
                data.append(
                    {
                        "x": filtered["date"],
                        "y": filtered["volume"],
                        "type": "bar",
                        "name": f"{stock}",
                    }
                )

            xaxis = {
                "title": "Trading Volume by Date",
                "autorange": True,
                "range": [from_date, to_date],
            }

            return {
                "data": data,
                "layout": {
                    "title": f"Trading Volume ({(' & ').join(selected_tickers)})",
                    "xaxis": xaxis,
                    "yaxis": {"autorange": True},
                },
            }

        else:
            data = [
                {
                    "x": [item for item in prices[(prices.ticker == stock)]["date"]],
                    "y": [item for item in prices[(prices.ticker == stock)]["volume"]],
                    "type": "bar",
                    "name": f"{stock}",
                }
                for stock in selected_tickers
            ]

            xaxis = {
                "title": "Trading Volume by Date",
                "autorange": True,
                "range": [MIN_DATE, MAX_DATE],
            }

            return {
                "data": data,
                "layout": {
                    "title": f"Trading Volume ({(' & ').join(selected_tickers)})",
                    "xaxis": xaxis,
                    "yaxis": {"autorange": True},
                },
            }

    return {
        "data": data,
        "layout": {
            "title": f"Trading Volume ({(' & ').join(selected_tickers)})",
            "yaxis": {"autorange": True},
        },
    }


if __name__ == "__main__":
    app.run_server(debug=True)
