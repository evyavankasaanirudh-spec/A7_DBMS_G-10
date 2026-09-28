from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .fraud_detection import calculate_fraud_risk
from .mongo_database import get_mongo_database


app = FastAPI(
    title="Insurance Fraud Detection Microservice",
    description="Fraud Risk Analysis using Rule-Based Detection and MongoDB",
    version="1.0.0"
)


class FraudAnalysisRequest(BaseModel):
    claim_id: int
    customer_id: int
    claim_amount: float
    previous_claims: int = 0
    days_after_policy_start: int = 0


@app.get("/")
def root():
    return {
        "service": "Fraud Service",
        "status": "running"
    }


@app.post("/analyze")
def analyze_fraud(request: FraudAnalysisRequest):

    result = calculate_fraud_risk(
        claim_amount=request.claim_amount,
        previous_claims=request.previous_claims,
        days_after_policy_start=request.days_after_policy_start
    )

    client, database = get_mongo_database()

    if client is None or database is None:
        raise HTTPException(
            status_code=500,
            detail="MongoDB connection failed"
        )

    try:
        collection = database["fraud_analysis"]

        document = {
            "claim_id": request.claim_id,
            "customer_id": request.customer_id,
            "claim_amount": request.claim_amount,
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "reasons": result["reasons"],
            "analysis_type": "rule_based"
        }

        existing_record = collection.find_one(
            {"claim_id": request.claim_id}
        )

        if existing_record:
            collection.update_one(
                {"claim_id": request.claim_id},
                {"$set": document}
            )
        else:
            collection.insert_one(document)

        return {
            "message": "Fraud analysis completed",
            "claim_id": request.claim_id,
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "reasons": result["reasons"]
        }

    finally:
        client.close()


@app.get("/fraud-analysis/{claim_id}")
def get_fraud_analysis(claim_id: int):

    client, database = get_mongo_database()

    if client is None or database is None:
        raise HTTPException(
            status_code=500,
            detail="MongoDB connection failed"
        )

    try:
        collection = database["fraud_analysis"]

        result = collection.find_one(
            {"claim_id": claim_id},
            {"_id": 0}
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Fraud analysis not found"
            )

        return result

    finally:
        client.close()