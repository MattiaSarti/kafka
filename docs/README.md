<h1 align="center">Kafka for an Event-driven Microservice Architecture</h1>

<p align="center">
    Kafka for an Event-driven Microservice-based Project to Produce (Synthetic) Stock Price Changes as Events and to Consume Such Messages in a Web Application for Rendering a Real-Time Stock Price History Chart
</p>


## The Project in a Picture:
![...loading...](./media/project-in-a-picture.png)

## A Video-Example:
TODO

## How to Build and Run the Project:
After installing Docker and Docker Compose, execute, in the root project directory:
```bash
docker compose up --build --detach
```
(Docker Version: 20.10.18 | Docker Compose Version: v2.12.2)

## Simplifications:
- no fault tolerance (single broker, producer and consumer instances, simplified producer and consumer)
- consumer cannot scale (no coordination in distributed application), Kafka Streams API not employed
