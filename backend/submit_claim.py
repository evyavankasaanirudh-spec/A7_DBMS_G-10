from database import get_postgres_connection


def submit_claim(
    customer_id,
    policy_id,
    claim_amount,
    claim_type,
    claim_date,
    description
):
    # Basic input validation
    if claim_amount <= 0:
        print("Claim amount must be greater than zero.")
        return

    if not claim_type.strip():
        print("Claim type cannot be empty.")
        return

    if not description.strip():
        print("Claim description cannot be empty.")
        return

    connection = get_postgres_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO claims
        (
            customer_id,
            policy_id,
            claim_amount,
            claim_type,
            claim_date,
            description
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING claim_id;
        """

        values = (
            customer_id,
            policy_id,
            claim_amount,
            claim_type,
            claim_date,
            description
        )

        cursor.execute(query, values)

        new_claim_id = cursor.fetchone()[0]

        connection.commit()

        print("\nClaim submitted successfully!")
        print("-" * 40)
        print(f"Claim ID      : {new_claim_id}")
        print(f"Customer ID   : {customer_id}")
        print(f"Policy ID     : {policy_id}")
        print(f"Claim Amount  : ₹{claim_amount}")
        print(f"Claim Type    : {claim_type}")
        print(f"Claim Date    : {claim_date}")
        print("Status        : Pending")

        cursor.close()

    except Exception as error:
        connection.rollback()
        print("Claim submission failed!")
        print("Error:", error)

    finally:
        connection.close()
        print("PostgreSQL connection closed.")


if __name__ == "__main__":
    submit_claim(
        customer_id=1,
        policy_id=1,
        claim_amount=45000,
        claim_type="Vehicle Repair",
        claim_date="2026-09-15",
        description="Repair expenses after a minor vehicle accident"
    )