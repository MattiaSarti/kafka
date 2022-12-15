"""
TODO
https://developer.confluent.io/quickstart/kafka-docker/
https://docs.confluent.io/kafka-clients/python/current/overview.html#ak-consumer
https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-producer
"""


from dash import Dash, Input, Output
from dash.dcc import Graph
from dash.html import Button, Div, H1
from plotly.express import line


REFRESH_BUTTON_COMPONENT_ID = 'refresh-button'
STOCK_CHART_COMPONENT_ID = 'stock-price-chart'

X = [1.2, 1.9, 2.8, 3.5, 4.4, 5.9, 6.1, 7.2, 8.0, 9.6, 10.1]
Y = [5.3, 6.8, 2.3, 7.4, 8.6, 1.6, 9.5, 10.4, 12.6, 11.3, 13.4]


app = Dash(name=__name__)


app.layout = Div(
    children=[
        H1("Live Stock Price Chart"),
        Graph(id=STOCK_CHART_COMPONENT_ID),
        Button("Refresh", id=REFRESH_BUTTON_COMPONENT_ID),
    ]
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
def update_and_display_time_series(*args, **kwargs):
    X.append(X[-1] + 1)
    Y.append(Y[-1] + 1)
    figure = line(
        x=X,
        y=Y
    )
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
