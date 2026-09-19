from database import get_postgres_connection
from services.fraud_detection import calculate_fraud_risk


def analyze_claim(claim_id):
    connection = get_postgres_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        # Fetch claim, customer, policy, and previous claim count
        query = """
        SELECT
            c.claim_id,
            c.customer_id,
            cu.full_name,
            c.policy_id,
            p.policy_type,
            c.claim_amount,
            c.claim_type,
            c.claim_date,
            p.policy_start_date,
            COUNT(previous_claims.claim_id) AS previous_claims
        FROM claims c
        JOIN customers cu
            ON c.customer_id = cu.customer_id
        JOIN policies p
            ON c.policy_id = p.policy_id
        LEFT JOIN claims previous_claims
            ON previous_claims.customer_id = c.customer_id
            AND previous_claims.claim_id <> c.claim_id
        WHERE c.claim_id = %s
        GROUP BY
            c.claim_id,
            c.customer_id,
            cu.full_name,
            c.policy_id,
            p.policy_type,
            c.claim_amount,
            c.claim_type,
            c.claim_date,
            p.policy_start_date;
        """

        cursor.execute(query, (claim_id,))
        claim = cursor.fetchone()

        if claim is None:
            print(f"No claim found with ID {claim_id}")
            return

        (
            claim_id,
            customer_id,
            customer_name,
            policy_id,
            policy_type,
            claim_amount,
            claim_type,
            claim_date,
            policy_start_date,
            previous_claims
        ) = claim

        # Calculate number of days after policy activation
        days_after_policy_start = (
            claim_date - policy_start_date
        ).days

        # Run fraud detection
        result = calculate_fraud_risk(
            claim_amount=float(claim_amount),
            previous_claims=previous_claims,
            days_after_policy_start=days_after_policy_start
        )

        print("\nInsurance Claim Fraud Analysis")
        print("=" * 50)
        print(f"Claim ID                : {claim_id}")
        print(f"Customer Name           : {customer_name}")
        print(f"Customer ID             : {customer_id}")
        print(f"Policy ID               : {policy_id}")
        print(f"Policy Type             : {policy_type}")
        print(f"Claim Amount            : ₹{claim_amount}")
        print(f"Claim Type              : {claim_type}")
        print(f"Claim Date              : {claim_date}")
        print(f"Policy Start Date       : {policy_start_date}")
        print(f"Days After Policy Start : {days_after_policy_start}")
        print(f"Previous Claims         : {previous_claims}")
        print("-" * 50)
        print(f"Fraud Risk Score        : {result['risk_score']}/100")
        print(f"Risk Level              : {result['risk_level']}")
        print("Fraud Indicators:")

        for reason in result["reasons"]:
            print(f"- {reason}")

        cursor.close()

    except Exception as error:
        print("Claim analysis failed!")
        print("Error:", error)

    finally:
        connection.close()
        print("PostgreSQL connection closed.")


if __name__ == "__main__":
    analyze_claim(claim_id=999)