"""
TODO
https://developer.confluent.io/quickstart/kafka-docker/
https://docs.confluent.io/kafka-clients/python/current/overview.html#ak-consumer
https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-producer
https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/
"""


from collections import deque
from logging import INFO, getLogger, info
from os import environ
from typing import List

from confluent_kafka import (
    Consumer,
    KafkaError,
    KafkaException,
    TopicPartition
)
from dash import Dash, Input, Output
from dash.dcc import Graph
from dash.html import Button, Div, H1
from plotly.express import line


BROKER_HOST = environ['BROKER_HOST']
BROKER_PORT = environ['BROKER_PORT']
CONSUMER_GROUP_ID = environ['CONSUMER_GROUP_ID']
EVENTS_KEY = environ['EVENTS_KEY']
TOPIC_ID = environ['TOPIC_ID']

FIGURE_LAYOUT = {
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'xaxis_title': "Time",
    'yaxis_title': "Stock Price"
}
GRID_STYLE = {
    'gridcolor': '#d3d3d3',
    'griddash': 'dash',
    'gridwidth': 0.5,
    'showgrid': True
}
MAIN_COLOR = '#33ceff'
N_LATEST_PRICES_MAKING_CHART_HISTORY = 6
REFRESH_BUTTON_COMPONENT_ID = 'refresh-button'
STOCK_CHART_COMPONENT_ID = 'stock-price-chart'
TEXT_STYLE = {
    'font-family': 'Times New Roman',
    'font-style': 'italic',
    'text-align': 'center'
}


def acknowledge_commit(
        error: KafkaError,
        partitions: List[TopicPartition]
) -> None:
    """
    Check whether the offset was correctly committed after the message
    consumption.
    """
    if error is not None:
        info(
            msg=(
                "Partition offset(s) failed to be committed!"
                f"\n\tDetails: {str(error)}"
            )
        )
    else:
        info(
            msg=(
                "Partition offset(s) committed ✓"
                f"\n\tDetails: {str(partitions)}"
            )
        )


getLogger().setLevel(INFO)


latest_prices = deque([], maxlen=N_LATEST_PRICES_MAKING_CHART_HISTORY)
latest_timestamps = deque([], maxlen=N_LATEST_PRICES_MAKING_CHART_HISTORY)

events_consumer = Consumer(
    {
        'bootstrap.servers': f"{BROKER_HOST}:{BROKER_PORT}",
        'group.id': CONSUMER_GROUP_ID,
        'enable.partition.eof': True,  # NOTE: so as not to wait for timeouts
        'on_commit': acknowledge_commit
    }
)

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
    global events_consumer, latest_prices, latest_timestamps

    try:
        events_consumer.subscribe(topics=[TOPIC_ID])

        while True:
            message = events_consumer.poll(timeout=0.01)  # [seconds]

            if message is None:
                break

            error = message.error()
            if error is not None:
                # if the end of the associated partition is reached:
                if error.code() == KafkaError._PARTITION_EOF:
                    break
                else:
                    raise KafkaException(error)

            timestamp, price = map(float, message.value().split('|'))
            latest_prices.append(price)
            latest_timestamps.append(timestamp)

            events_consumer.commit(asynchronous=True)

    except Exception as exception:
        events_consumer.close()
        raise exception

    figure = line(x=latest_timestamps, y=latest_prices)

    figure.update_layout(**FIGURE_LAYOUT)
    figure.update_traces(line_color=MAIN_COLOR)
    figure.update_xaxes(**GRID_STYLE)
    figure.update_yaxes(**GRID_STYLE)

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
