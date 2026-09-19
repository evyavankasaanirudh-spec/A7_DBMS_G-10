from datetime import datetime

from backend.database import get_postgres_connection
from backend.mongo_database import get_mongo_database
from backend.services.fraud_detection import calculate_fraud_risk


def process_claim(claim_id):
    # -----------------------------
    # 1. Fetch claim from PostgreSQL
    # -----------------------------
    postgres_connection = get_postgres_connection()
    postgres_cursor = postgres_connection.cursor()

    query = """
        SELECT
            c.claim_id,
            c.customer_id,
            c.policy_id,
            c.claim_amount,
            c.claim_date,
            c.description,
            c.status,
            cu.customer_id AS customer_id,
            p.policy_type,
            p.coverage_amount
        FROM claims c
        JOIN customers cu
            ON c.customer_id = cu.customer_id
        JOIN policies p
            ON c.policy_id = p.policy_id
        WHERE c.claim_id = %s;
    """

    postgres_cursor.execute(query, (claim_id,))
    claim = postgres_cursor.fetchone()

    if claim is None:
        print("Claim not found.")
        postgres_cursor.close()
        postgres_connection.close()
        return

    (
        claim_id,
        customer_id,
        policy_id,
        claim_amount,
        claim_date,
        description,
        status,
        customer_name,
        policy_type,
        coverage_amount
    ) = claim

    print("\n========== CLAIM DETAILS ==========")
    print("Claim ID:", claim_id)
    print("Customer:", customer_name)
    print("Policy Type:", policy_type)
    print("Claim Amount:", claim_amount)
    print("Coverage Amount:", coverage_amount)
    print("Description:", description)

    # -----------------------------
    # 2. Calculate fraud risk
    # -----------------------------
    risk_result = calculate_fraud_risk(
        float(claim_amount),
        0,
        0
    )

    risk_score = risk_result["risk_score"]
    risk_level = risk_result["risk_level"]
    reasons = risk_result["reasons"]

    print("\n========== FRAUD ANALYSIS ==========")
    print("Risk Score:", risk_score)
    print("Risk Level:", risk_level)

    print("Reasons:")
    for reason in reasons:
        print("-", reason)

    # -----------------------------
    # 3. Update claim status
    # -----------------------------
    if risk_level == "High":
        new_status = "Under Review"
    else:
        new_status = "Processed"

    update_query = """
        UPDATE claims
        SET status = %s
        WHERE claim_id = %s;
    """

    postgres_cursor.execute(update_query, (new_status, claim_id))
    postgres_connection.commit()

    # -----------------------------
    # 4. Store analysis in MongoDB
    # -----------------------------
    mongo_client, mongo_database = get_mongo_database()
    fraud_collection = mongo_database["fraud_analysis"]

    fraud_document = {
        "claim_id": claim_id,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "policy_id": policy_id,
        "policy_type": policy_type,
        "claim_amount": float(claim_amount),
        "coverage_amount": float(coverage_amount),
        "description": description,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "claim_status": new_status,
        "analyzed_at": datetime.now()
    }

    insert_result = fraud_collection.insert_one(fraud_document)

    print("\n========== STORAGE DETAILS ==========")
    print("MongoDB Document ID:", insert_result.inserted_id)
    print("Updated PostgreSQL Status:", new_status)
    print("Fraud analysis saved successfully in MongoDB.")

    # -----------------------------
    # 5. Close connections
    # -----------------------------
    postgres_cursor.close()
    postgres_connection.close()
    mongo_client.close()

    return {
        "claim_id": claim_id,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "claim_amount": float(claim_amount),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "claim_status": new_status,
        "message": "Claim processed and fraud analysis saved successfully"
    }

    print("\nClaim processing completed successfully.")


if __name__ == "__main__":
    claim_id_input = int(input("Enter Claim ID to process: "))
    process_claim(claim_id_input)