import psycopg2


def get_postgres_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="insurance_db",
            user="postgres",
            password="eve0928"
        )

        print("PostgreSQL connection successful!")
        return connection

    except Exception as error:
        print("PostgreSQL connection failed!")
        print("Error:", error)
        return None


if __name__ == "__main__":
    connection = get_postgres_connection()

    if connection:
        connection.close()
        print("PostgreSQL connection closed.")