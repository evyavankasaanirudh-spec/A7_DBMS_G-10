import psycopg2


def get_db_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="insurance_db",
            user="postgres",
            password="eve0928"
        )

        print("Claim Service: PostgreSQL connection successful!")
        return connection

    except Exception as error:
        print("Claim Service: PostgreSQL connection failed!")
        print("Error:", error)
        return None