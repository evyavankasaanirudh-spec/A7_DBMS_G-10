from pymongo import MongoClient


def get_mongo_database():
    try:
        client = MongoClient(
            "mongodb://127.0.0.1:27017/",
            serverSelectionTimeoutMS=5000
        )

        client.admin.command("ping")

        print("Fraud Service: MongoDB connection successful!")

        database = client["insurance_fraud_db"]

        return client, database

    except Exception as error:
        print("Fraud Service: MongoDB connection failed!")
        print("Error:", error)

        return None, None