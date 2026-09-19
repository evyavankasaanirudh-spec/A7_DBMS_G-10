from database import get_postgres_connection


def fetch_all_claims():
    connection = get_postgres_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        query = """
        SELECT
            c.claim_id,
            cu.full_name,
            p.policy_type,
            c.claim_amount,
            c.claim_type,
            c.claim_date,
            c.status
        FROM claims c
        JOIN customers cu
            ON c.customer_id = cu.customer_id
        JOIN policies p
            ON c.policy_id = p.policy_id
        ORDER BY c.claim_id;
        """

        cursor.execute(query)

        claims = cursor.fetchall()

        print("\nInsurance Claims")
        print("=" * 90)

        for claim in claims:
            print(f"Claim ID       : {claim[0]}")
            print(f"Customer Name  : {claim[1]}")
            print(f"Policy Type    : {claim[2]}")
            print(f"Claim Amount   : ₹{claim[3]}")
            print(f"Claim Type     : {claim[4]}")
            print(f"Claim Date     : {claim[5]}")
            print(f"Status         : {claim[6]}")
            print("-" * 90)

        print(f"Total claims fetched: {len(claims)}")

        cursor.close()

    except Exception as error:
        print("Error while fetching claims:", error)

    finally:
        connection.close()
        print("PostgreSQL connection closed.")


if __name__ == "__main__":
    fetch_all_claims()