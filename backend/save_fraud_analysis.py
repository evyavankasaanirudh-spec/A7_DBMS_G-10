from datetime import datetime

from mongo_database import get_mongo_database


def save_fraud_analysis(
    claim_id,
    customer_id,
    claim_amount,
    risk_score,
    risk_level,
    reasons
):
    client, database = get_mongo_database()

    if client is None:
        return

    try:
        collection = database["fraud_analysis"]

        fraud_document = {
            "claim_id": claim_id,
            "customer_id": customer_id,
            "claim_amount": claim_amount,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "reasons": reasons,
            "analysis_type": "Rule-Based Fraud Detection",
            "created_at": datetime.now()
        }

        # Check whether this claim already has a fraud analysis
        existing_record = collection.find_one(
            {
                "claim_id": claim_id
            }
        )

        if existing_record:

            # Update the existing analysis instead of
            # creating another duplicate document
            collection.update_one(
                {
                    "_id": existing_record["_id"]
                },
                {
                    "$set": {
                        "customer_id": customer_id,
                        "claim_amount": claim_amount,
                        "risk_score": risk_score,
                        "risk_level": risk_level,
                        "reasons": reasons,
                        "analysis_type": "Rule-Based Fraud Detection",
                        "updated_at": datetime.now()
                    }
                }
            )

            print("\nFraud analysis updated successfully!")
            print("Claim ID:", claim_id)
            print("Risk Score:", risk_score)
            print("Risk Level:", risk_level)

        else:

            # No existing record → create a new one
            result = collection.insert_one(fraud_document)

            print("\nFraud analysis saved successfully!")
            print("MongoDB document ID:", result.inserted_id)
            print("Claim ID:", claim_id)
            print("Risk Score:", risk_score)
            print("Risk Level:", risk_level)

    except Exception as error:
        print("Failed to save fraud analysis!")
        print("Error:", error)

    finally:
        client.close()
        print("MongoDB connection closed.")


if __name__ == "__main__":
    save_fraud_analysis(
        claim_id=1,
        customer_id=1,
        claim_amount=85000,
        risk_score=90,
        risk_level="High",
        reasons=[
            "High claim amount",
            "Multiple previous claims",
            "Claim submitted shortly after policy activation"
        ]
    )