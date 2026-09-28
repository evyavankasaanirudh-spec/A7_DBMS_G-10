from kafka import KafkaConsumer
import json


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "claim-notifications"


def start_consumer():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="insurance-notification-group",
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        )
    )

    print("Notification Service: Kafka consumer started!")
    print(f"Listening to topic: {KAFKA_TOPIC}")

    for message in consumer:
        event = message.value

        print("\n--- Notification Event Received ---")
        print(f"Event: {event}")
        print("------------------------------------")