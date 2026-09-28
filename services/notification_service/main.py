from fastapi import FastAPI
import threading

from .kafka_consumer import start_consumer


app = FastAPI(
    title="Insurance Notification Microservice",
    description="Kafka-based Notification Service",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "service": "Notification Service",
        "status": "running",
        "kafka_topic": "claim-notifications"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "kafka": "connected"
    }


@app.on_event("startup")
def start_kafka_consumer():
    consumer_thread = threading.Thread(
        target=start_consumer,
        daemon=True
    )

    consumer_thread.start()