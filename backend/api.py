from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.database import get_postgres_connection
from backend.mongo_database import get_mongo_database
from backend.process_claim import process_claim
from backend.auth import (
    verify_password,
    create_access_token,
    decode_access_token
)


# ============================================================
# APPLICATION SETUP
# ============================================================

app = FastAPI(
    title="Insurance Claim Fraud Detection API",
    description="REST API for processing insurance claims and storing fraud analysis",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# FRONTEND
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


if not FRONTEND_DIR.exists():
    raise RuntimeError(
        f"Frontend directory not found: {FRONTEND_DIR}"
    )


app.mount(
    "/frontend",
    StaticFiles(
        directory=str(FRONTEND_DIR),
        html=True
    ),
    name="frontend"
)


# ============================================================
# JWT SECURITY
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# ============================================================
# AUTHENTICATION
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = decode_access_token(token)

        user_id = payload.get("sub")
        username = payload.get("username")
        role = payload.get("role")


        if not user_id or not username or not role:

            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )


        return {
            "user_id": int(user_id),
            "username": username,
            "role": role
        }


    except HTTPException:
        raise


    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


def require_roles(*allowed_roles):

    def role_checker(
        current_user=Depends(get_current_user)
    ):

        if current_user["role"] not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )

        return current_user


    return role_checker


# ============================================================
# CLAIM MODEL
# ============================================================

class ClaimRequest(BaseModel):

    policy_id: int = Field(gt=0)

    claim_type: str = Field(
        min_length=2,
        max_length=100
    )

    claim_amount: float = Field(gt=0)

    claim_date: date

    description: str = Field(
        min_length=5,
        max_length=500
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Insurance Claim Fraud Detection API is running",
        "version": "1.0"
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    connection = None
    cursor = None


    try:

        connection = get_postgres_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT
                user_id,
                username,
                password_hash,
                role,
                customer_id
            FROM users
            WHERE username = %s;
            """,
            (form_data.username,)
        )


        user = cursor.fetchone()


        if not user:

            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )


        (
            user_id,
            username,
            password_hash,
            role,
            customer_id
        ) = user


        if not verify_password(
            form_data.password,
            password_hash
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )


        access_token = create_access_token(
            {
                "sub": str(user_id),
                "username": username,
                "role": role
            }
        )


        # IMPORTANT:
        # Return both top-level values and user object.
        # This makes the API easy to use from Swagger
        # and from the frontend.

        return {

            "message": "Login successful",

            "access_token": access_token,

            "token_type": "bearer",

            "username": username,

            "role": role,

            "customer_id": customer_id,

            "user": {

                "user_id": user_id,

                "username": username,

                "role": role,

                "customer_id": customer_id

            }

        }


    except HTTPException:
        raise


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# PROCESS CLAIM
# ADMIN + CLAIM OFFICER
# ============================================================

@app.get("/process/{claim_id}")
def process_claim_endpoint(
    claim_id: int,
    current_user=Depends(
        require_roles(
            "Admin",
            "Claim Officer"
        )
    )
):

    try:

        result = process_claim(claim_id)

        return result


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# CREATE CLAIM
# CUSTOMER ONLY
# ============================================================

@app.post("/claims")
def create_claim(
    claim: ClaimRequest,
    current_user=Depends(get_current_user)
):

    connection = None
    cursor = None


    try:

        connection = get_postgres_connection()

        cursor = connection.cursor()


        if current_user["role"] != "Customer":

            raise HTTPException(
                status_code=403,
                detail="Only customers can submit claims"
            )


        cursor.execute(
            """
            SELECT customer_id
            FROM users
            WHERE user_id = %s;
            """,
            (current_user["user_id"],)
        )


        user_record = cursor.fetchone()


        if not user_record or user_record[0] is None:

            raise HTTPException(
                status_code=400,
                detail="Customer account is not linked to a customer"
            )


        customer_id = user_record[0]


        cursor.execute(
            """
            INSERT INTO claims
            (
                customer_id,
                policy_id,
                claim_type,
                claim_amount,
                claim_date,
                description,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'Pending'
            )
            RETURNING claim_id;
            """,
            (
                customer_id,
                claim.policy_id,
                claim.claim_type,
                claim.claim_amount,
                claim.claim_date,
                claim.description
            )
        )


        claim_id = cursor.fetchone()[0]

        connection.commit()


        return {

            "message":
                "Claim submitted successfully",

            "claim_id":
                claim_id,

            "customer_id":
                customer_id,

            "status":
                "Pending"

        }


    except HTTPException:
        raise


    except Exception as error:

        if connection:
            connection.rollback()


        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# CUSTOMER CLAIMS
# ============================================================

@app.get("/my-claims")
def get_my_claims(
    current_user=Depends(
        require_roles("Customer")
    )
):

    connection = None
    cursor = None


    try:

        connection = get_postgres_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT customer_id
            FROM users
            WHERE user_id = %s;
            """,
            (current_user["user_id"],)
        )


        user_record = cursor.fetchone()


        if not user_record or user_record[0] is None:

            raise HTTPException(
                status_code=400,
                detail="Customer account is not linked to a customer"
            )


        customer_id = user_record[0]


        cursor.execute(
            """
            SELECT
                claim_id,
                customer_id,
                policy_id,
                claim_type,
                claim_amount,
                claim_date,
                description,
                status
            FROM claims
            WHERE customer_id = %s
            ORDER BY claim_id DESC;
            """,
            (customer_id,)
        )


        rows = cursor.fetchall()


        claims = []


        for row in rows:

            claims.append(
                {
                    "claim_id": row[0],
                    "customer_id": row[1],
                    "policy_id": row[2],
                    "claim_type": row[3],
                    "claim_amount": float(row[4]),
                    "claim_date": str(row[5]),
                    "description": row[6],
                    "status": row[7]
                }
            )


        return {

            "customer_id":
                customer_id,

            "claims":
                claims

        }


    except HTTPException:
        raise


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# ALL CLAIMS
# ADMIN + CLAIM OFFICER
# ============================================================

@app.get("/claims")
def get_claims(
    current_user=Depends(
        require_roles(
            "Admin",
            "Claim Officer"
        )
    )
):

    connection = None
    cursor = None


    try:

        connection = get_postgres_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT
                claim_id,
                customer_id,
                policy_id,
                claim_type,
                claim_amount,
                claim_date,
                description,
                status
            FROM claims
            ORDER BY claim_id;
            """
        )


        rows = cursor.fetchall()


        claims = []


        for row in rows:

            claims.append(
                {
                    "claim_id": row[0],
                    "customer_id": row[1],
                    "policy_id": row[2],
                    "claim_type": row[3],
                    "claim_amount": float(row[4]),
                    "claim_date": str(row[5]),
                    "description": row[6],
                    "status": row[7]
                }
            )


        return {
            "claims": claims
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# FRAUD ANALYSIS
# ADMIN + CLAIM OFFICER
# ============================================================

@app.get("/fraud-analysis")
def get_fraud_analysis(
    current_user=Depends(
        require_roles(
            "Admin",
            "Claim Officer"
        )
    )
):
    try:
        mongo_result = get_mongo_database()

        # Handle either:
        # 1. database object
        # 2. tuple returned by Mongo helper
        if isinstance(mongo_result, tuple):
            database = mongo_result[-1]
        else:
            database = mongo_result

        collection = database["fraud_analysis"]

        records = list(
            collection.find(
                {},
                {
                    "_id": 0
                }
            )
        )

        return {
            "fraud_analysis": records,
            "records": records,
            "count": len(records)
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

# ============================================================
# FILTER FRAUD ANALYSIS
# ============================================================

@app.get("/fraud-analysis/filter")
def filter_fraud_analysis(
    risk_level: str = Query(...),

    current_user=Depends(
        require_roles(
            "Admin",
            "Claim Officer"
        )
    )
):
    allowed_levels = [
        "High",
        "Medium",
        "Low"
    ]

    if risk_level not in allowed_levels:
        raise HTTPException(
            status_code=400,
            detail="Risk level must be High, Medium, or Low"
        )

    try:
        mongo_result = get_mongo_database()

        if isinstance(mongo_result, tuple):
            database = mongo_result[-1]
        else:
            database = mongo_result

        collection = database["fraud_analysis"]

        records = list(
            collection.find(
                {
                    "risk_level": risk_level
                },
                {
                    "_id": 0
                }
            )
        )

        return {
            "risk_level": risk_level,
            "count": len(records),
            "fraud_analysis": records,
            "records": records
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# DASHBOARD SUMMARY
# ADMIN + CLAIM OFFICER
# ============================================================

@app.get("/dashboard-summary")
def dashboard_summary(
    current_user=Depends(
        require_roles(
            "Admin",
            "Claim Officer"
        )
    )
):
    connection = None
    cursor = None

    try:
        connection = get_postgres_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_claims,

                COUNT(*) FILTER (
                    WHERE LOWER(status) = 'pending'
                ) AS pending_claims,

                COUNT(*) FILTER (
                    WHERE LOWER(status) = 'processed'
                ) AS processed_claims,

                COUNT(*) FILTER (
                    WHERE LOWER(status) = 'under review'
                ) AS under_review_claims

            FROM claims;
            """
        )

        result = cursor.fetchone()

        total_claims = result[0]
        pending_claims = result[1]
        processed_claims = result[2]
        under_review_claims = result[3]

        # MongoDB
        mongo_result = get_mongo_database()

        if isinstance(mongo_result, tuple):
            database = mongo_result[-1]
        else:
            database = mongo_result

        collection = database["fraud_analysis"]

        total_fraud_records = collection.count_documents({})

        high_risk = collection.count_documents(
            {
                "risk_level": "High"
            }
        )

        medium_risk = collection.count_documents(
            {
                "risk_level": "Medium"
            }
        )

        low_risk = collection.count_documents(
            {
                "risk_level": "Low"
            }
        )

        return {
            "claims": {
                # Original names
                "total_claims": total_claims,
                "pending_claims": pending_claims,
                "processed_claims": processed_claims,
                "under_review_claims": under_review_claims,

                # Frontend-friendly aliases
                "total": total_claims,
                "pending": pending_claims,
                "processed": processed_claims,
                "under_review": under_review_claims
            },

            "fraud_analysis": {
                "total_records": total_fraud_records,
                "high_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk
            },

            # Frontend-friendly fraud object
            "fraud": {
                "total": total_fraud_records,
                "high": high_risk,
                "medium": medium_risk,
                "low": low_risk
            }
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()