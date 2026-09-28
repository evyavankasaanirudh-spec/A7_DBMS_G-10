from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .database import get_db_connection
from .auth import verify_password, create_access_token


app = FastAPI(
    title="Insurance Auth Microservice",
    description="JWT Authentication and Role-Based Access Service",
    version="1.0.0"
)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def root():
    return {
        "service": "Auth Service",
        "status": "running"
    }


@app.post("/login")
def login(request: LoginRequest):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT user_id, username, password_hash, role, customer_id
        FROM users
        WHERE username = %s
        """,
        (request.username,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    user_id, username, password_hash, role, customer_id = user

    if not verify_password(request.password, password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token_data = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "customer_id": customer_id
    }

    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user_id,
            "username": username,
            "role": role,
            "customer_id": customer_id
        }
    }