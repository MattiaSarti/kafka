<h1 align="center">Kafka for an Event-driven Microservice Architecture</h1>

<p align="center">
    Kafka for an Event-driven Microservice Architecture
</p>


```bash
kafka-topics --bootstrap-server broker:${BROKER_PORT} --topic ${TOPIC_ID} --create
echo "Topic '${TOPIC_ID}' created:"
kafka-topics --bootstrap-server broker:${BROKER_PORT} --topic ${TOPIC_ID} --describe
```

Simplifications:
- no fault tolerance (single broker, producer and consumer instances, simplified producer and consumer)
- consumer cannot scale (no coordination in distributed application), Kafka Streams API not employed
