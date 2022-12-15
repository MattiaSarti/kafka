"""
Periodic (random) stock price update events publication.
"""


from logging import INFO, getLogger, info
from os import environ
from time import sleep

from confluent_kafka import Message, Producer


BROKER_HOST = environ['BROKER_HOST']
BROKER_PORT = environ['BROKER_PORT']
EVENTS_KEY = environ['EVENTS_KEY']
TOPIC_ID = environ['TOPIC_ID']

EVENT_PUBLISHING_TIMEOUT_IN_S = 120
INFORMATIVE_MESSAGE_METHODS = [
    'headers',
    'key',
    'latency',
    'offset',
    'partition',
    'timestamp',
    'topic',
    'value'
]


getLogger().setLevel(INFO)


def event_publication_acknowledgment(err, msg) -> None:
    """
    Print either the successfully published event ot the event failed to be
    delivered together with its error.
    """
    info(
        (
            "Event failed to be delivered!" +
            f"\n\tEvent details: {stringify_message(msg)}" +
            f"\n\tError: {str(err)}"
        ) if err is not None else (
            "Event published ✓" +
            f"\n\tEvent details: {stringify_message(msg)}"
        )
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
            # partition=...,
            # NOTE: no need to specify a unique partition as, anyway, events
            # with same key are guaranteed to be assigned to the same
            # partition; thus, any partition is fine as long as the key is
            # kept constant
            key=EVENTS_KEY,
            value='is amazing'  # TODO
        )
        events_producer.flush(timeout=EVENT_PUBLISHING_TIMEOUT_IN_S)


def stringify_message(message: Message) -> str:
    """
    Turn the given client message into a well-formatted and informative
    string.
    """
    message_as_string = []
    for method_name in INFORMATIVE_MESSAGE_METHODS:
        method = getattr(message, method_name)
        message_as_string.append(
            method_name + ': ' + str(method())
        )
    return ' | '.join(message_as_string)


if __name__ == '__main__':
    periodically_publish_events_of_random_stock_price_changes()
