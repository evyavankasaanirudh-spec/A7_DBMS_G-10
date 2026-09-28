from fastapi import FastAPI, HTTPException

from .database import get_db_connection
from .schemas import ClaimCreate
from .kafka_producer import publish_claim_created


app = FastAPI(
    title="Insurance Claim Microservice",
    description="Claim Processing Microservice",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "service": "Claim Service",
        "status": "running"
    }


@app.post("/claims")
def create_claim(claim: ClaimCreate):

    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )

    cursor = connection.cursor()

    try:
        # Insert claim into PostgreSQL
        cursor.execute(
            """
            INSERT INTO claims
            (
                customer_id,
                policy_id,
                claim_amount,
                claim_type,
                claim_date,
                description,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING claim_id
            """,
            (
                claim.customer_id,
                claim.policy_id,
                claim.claim_amount,
                claim.claim_type,
                claim.claim_date,
                claim.description,
                "Pending"
            )
        )

        claim_id = cursor.fetchone()[0]

        # Commit claim to PostgreSQL
        connection.commit()

        # Publish claim-created event to Kafka
        try:
            kafka_event = publish_claim_created(
                claim_id=claim_id,
                customer_id=claim.customer_id,
                claim_amount=claim.claim_amount
            )

        except Exception as kafka_error:
            kafka_event = {
                "event": "CLAIM_CREATED",
                "status": "Kafka notification failed",
                "error": str(kafka_error)
            }

        return {
            "message": "Claim created successfully",
            "claim_id": claim_id,
            "status": "Pending",
            "kafka_event": kafka_event
        }

    except Exception as error:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:
        cursor.close()
        connection.close()


@app.get("/claims")
def get_claims():

    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                claim_id,
                customer_id,
                policy_id,
                claim_amount,
                claim_type,
                claim_date,
                description,
                status
            FROM claims
            ORDER BY claim_id
            """
        )

        rows = cursor.fetchall()

        claims = []

        for row in rows:
            claims.append({
                "claim_id": row[0],
                "customer_id": row[1],
                "policy_id": row[2],
                "claim_amount": float(row[3]),
                "claim_type": row[4],
                "claim_date": row[5],
                "description": row[6],
                "status": row[7]
            })

        return claims

    finally:
        cursor.close()
        connection.close()