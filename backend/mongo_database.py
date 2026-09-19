from pymongo import MongoClient


def get_mongo_database():
    try:
        client = MongoClient(
            "mongodb://127.0.0.1:27017/",
            serverSelectionTimeoutMS=5000
        )

        # Test the MongoDB connection
        client.admin.command("ping")

        print("MongoDB connection successful!")

        database = client["insurance_fraud_db"]
        return client, database

    except Exception as error:
        print("MongoDB connection failed!")
        print("Error:", error)
        return None, None


if __name__ == "__main__":
    client, database = get_mongo_database()

    if client is not None:
        print("Database name:", database.name)
        client.close()
        print("MongoDB connection closed.")