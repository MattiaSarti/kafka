"""
Periodic (random) stock price update events publication.
"""


from os import environ
from time import sleep

from confluent_kafka import Producer


BROKER_HOST = environ['BROKER_HOST']
BROKER_PORT = environ['BROKER_PORT']
TOPIC_ID = environ['TOPIC_ID']
TOPIC_PARTITION_ID = int(environ['TOPIC_PARTITION_ID'])

EVENT_PUBLISHING_TIMEOUT_IN_S = 120


def event_publication_acknowledgment(err, msg) -> None:
    """
    Print either the successfully published event ot the event failed to be
    delivered together with its error.
    """
    print(
        f"Event failed to be delivered: {str(msg)}\n\tError: {str(err)}"
        if err is not None else f"Event published: {str(msg)}"
    )


def periodically_publish_events_of_random_stock_price_changes() -> None:
    """
    Periodically publish random changes in the stock price to the message
    broker.
    """
    events_producer = Producer(
        {'bootstrap.servers': f"{BROKER_HOST}:{BROKER_PORT}"}
    )
    while True:
        sleep(10)

        events_producer.produce(
            on_delivery=event_publication_acknowledgment,
            topic=TOPIC_ID,
            partition=TOPIC_PARTITION_ID,
            key='mattia',  # TODO
            value='is amazing'  # TODO
        )
        events_producer.flush(timeout=EVENT_PUBLISHING_TIMEOUT_IN_S)


if __name__ == '__main__':
    periodically_publish_events_of_random_stock_price_changes()
