from kafka import KafkaProducer
import json


producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


def publish_claim_created(claim_id, customer_id, claim_amount):
    event = {
        "event": "CLAIM_CREATED",
        "claim_id": claim_id,
        "customer_id": customer_id,
        "claim_amount": claim_amount,
        "message": f"Claim {claim_id} created successfully"
    }

    producer.send(
        "claim-notifications",
        event
    )

    producer.flush()

    return event