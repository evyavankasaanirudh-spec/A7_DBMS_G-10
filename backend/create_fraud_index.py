from mongo_database import get_mongo_database


client, database = get_mongo_database()

try:
    collection = database["fraud_analysis"]

    print("\nChecking fraud-analysis records...")

    pipeline = [
        {
            "$sort": {
                "created_at": -1,
                "_id": -1
            }
        },
        {
            "$group": {
                "_id": "$claim_id",
                "keep_id": {"$first": "$_id"},
                "all_ids": {"$push": "$_id"},
                "count": {"$sum": 1}
            }
        }
    ]

    total_deleted = 0

    for group in collection.aggregate(pipeline):

        claim_id = group["_id"]
        keep_id = group["keep_id"]
        all_ids = group["all_ids"]
        count = group["count"]

        if count > 1:

            delete_ids = [
                doc_id
                for doc_id in all_ids
                if doc_id != keep_id
            ]

            result = collection.delete_many(
                {
                    "_id": {
                        "$in": delete_ids
                    }
                }
            )

            total_deleted += result.deleted_count

            print(
                f"Claim {claim_id}: "
                f"found {count} records, "
                f"kept latest record, "
                f"deleted {result.deleted_count} duplicate(s)"
            )

    print("\nDuplicate cleanup completed.")
    print("Total duplicate records deleted:", total_deleted)

    # Now create the unique index
    collection.create_index(
        [("claim_id", 1)],
        unique=True,
        name="unique_claim_id"
    )

    print("\nUnique index created successfully!")
    print("Only one fraud-analysis record is now allowed per claim.")

    print(
        "\nRemaining fraud-analysis records:",
        collection.count_documents({})
    )

finally:
    client.close()
    print("MongoDB connection closed.")