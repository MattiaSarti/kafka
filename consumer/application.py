"""
TODO
https://developer.confluent.io/quickstart/kafka-docker/
https://docs.confluent.io/kafka-clients/python/current/overview.html#ak-consumer
https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-producer
"""


from os import environ

from confluent_kafka import Consumer
from dash import Dash, Input, Output
from dash.dcc import Graph
from dash.html import Button, Div, H1
from plotly.express import line


CONSUMER_GROUP_ID = environ['CONSUMER_GROUP_ID']
EVENTS_KEY = environ['EVENTS_KEY']

GRID_STYLE = {
    'gridcolor': '#d3d3d3',
    'griddash': 'dash',
    'gridwidth': 0.5,
    'showgrid': True
}
MAIN_COLOR = '#33ceff'
REFRESH_BUTTON_COMPONENT_ID = 'refresh-button'
STOCK_CHART_COMPONENT_ID = 'stock-price-chart'
TEXT_STYLE = {
    'font-family': 'Times New Roman',
    'font-style': 'italic',
    'text-align': 'center'
}

X = [1.2, 1.9, 2.8, 3.5, 4.4, 5.9, 6.1, 7.2, 8.0, 9.6, 10.1]
Y = [5.3, 6.8, 2.3, 7.4, 8.6, 1.6, 9.5, 10.4, 12.6, 11.3, 13.4]


app = Dash(name=__name__)


app.layout = Div(
    children=[
        H1(
            "Live Stock Price Chart",
            style={
                'font-size': '35px',
                'font-weight': 'normal',
                'margin-top': '40px'
            }
        ),
        Button(
            "Refresh",
            id=REFRESH_BUTTON_COMPONENT_ID,
            style={
                'border-color': MAIN_COLOR,
                'background-color': 'white',
                'font-size': '25px',
                'margin-top': '20px',
                'padding':'15px 30px 15px 30px',
                **TEXT_STYLE
            }
        ),
        Graph(
            id=STOCK_CHART_COMPONENT_ID,
            config={
                'displayModeBar': False,
                'displaylogo': False
            }
        ),
    ],
    style={
        **TEXT_STYLE
    }
)


@app.callback(
    Output(
        component_id=STOCK_CHART_COMPONENT_ID,
        component_property='figure'
    ),
    Input(
        component_id=REFRESH_BUTTON_COMPONENT_ID,
        component_property='n_clicks'
    )
)
def update_and_display_stock_price_chart(*args, **kwargs):
    """
    Update the stock price chart figure with the latest events' data, if any.
    """
    X.append(X[-1] + 1)
    Y.append(Y[-1] + 1)

    figure = line(x=X, y=Y)
    figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Stock Price",
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)'
    )
    figure.update_traces(
        line_color=MAIN_COLOR
    )
    figure.update_xaxes(**GRID_STYLE)
    figure.update_yaxes(**GRID_STYLE)

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
