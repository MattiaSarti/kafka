"""
Live stock price chart application, consuming latest price change events.
"""


from collections import deque
from logging import INFO, getLogger, info
from os import environ
from threading import Thread
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
CONSUMER_APPLICATION_PORT = environ['CONSUMER_APPLICATION_PORT']
CONSUMER_GROUP_ID = environ['CONSUMER_GROUP_ID']
EVENTS_KEY = environ['EVENTS_KEY']
TOPIC_ID = environ['TOPIC_ID']

FIGURE_LAYOUT = {
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'xaxis_title': "Timestep",
    'yaxis_title': "Stock Price"
}
GRID_STYLE = {
    'gridcolor': '#d3d3d3',
    'griddash': 'dash',
    'gridwidth': 0.5,
    'showgrid': True
}
MAIN_COLOR = '#33ceff'
N_LATEST_PRICES_MAKING_CHART_HISTORY = 60
REFRESH_BUTTON_COMPONENT_ID = 'refresh-button'
STOCK_CHART_COMPONENT_ID = 'stock-price-chart'
TEXT_STYLE = {
    'font-family': 'Times New Roman',
    'font-style': 'italic',
    'text-align': 'center'
}


def acknowledge_commit(
        error: KafkaError,
        topic_partitions: List[TopicPartition]
) -> None:
    """
    Check whether the offset was correctly committed after the message
    consumption.
    """
    if error is not None:
        info(
            msg=f"Partition offset(s) failed to be committed: {str(error)}"
        )
    else:
        info(
            msg=(
                "Partition offset(s) committed ✓"
                "\n\tDetails:\n\t\t"
                '\n\t\t'.join(
                    [
                        (
                            f"- offset {str(topic_partition.offset)}"
                            f" in partition {str(topic_partition.partition)}"
                            f" of topic {str(topic_partition.offset)}"
                        ) for topic_partition in topic_partitions
                    ]
                )
            )
        )


def continuous_polling_over_any_latest_events():
    """
    Continuously updating the price chart data with any latest events via
    polling.
    """
    events_consumer = Consumer(
        {
            'bootstrap.servers': f"{BROKER_HOST}:{BROKER_PORT}",
            'group.id': CONSUMER_GROUP_ID,
            'enable.partition.eof': True,
            'on_commit': acknowledge_commit
        }
    )

    try:
        events_consumer.subscribe(topics=[TOPIC_ID])

        while True:
            message = events_consumer.poll(timeout=1)  # [seconds]

            if message is None:
                continue

            error = message.error()
            if error is not None:
                # if the end of the associated partition is reached:
                if error.code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(error)

            latest_prices.append(float(message.value()))
            latest_timesteps.append(float(message.offset()))

            events_consumer.commit(asynchronous=True)

    finally:
        events_consumer.close()


getLogger().setLevel(INFO)

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
                'padding': '15px 30px 15px 30px',
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
    # recreating the price chart with up-to-date data:
    figure = line(x=latest_timesteps, y=latest_prices)

    # styling the chart:
    figure.update_layout(**FIGURE_LAYOUT)
    figure.update_traces(line_color=MAIN_COLOR)
    figure.update_xaxes(**GRID_STYLE)
    figure.update_yaxes(**GRID_STYLE)

    return figure


if __name__ == '__main__':
    latest_prices = deque([], maxlen=N_LATEST_PRICES_MAKING_CHART_HISTORY)
    latest_timesteps = deque([], maxlen=N_LATEST_PRICES_MAKING_CHART_HISTORY)

    Thread(target=continuous_polling_over_any_latest_events).start()

    app.run(host='0.0.0.0', port=CONSUMER_APPLICATION_PORT, debug=False)
