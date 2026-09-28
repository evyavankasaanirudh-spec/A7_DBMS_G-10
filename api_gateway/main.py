from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

from .auth import get_current_user, require_roles



app = FastAPI(
    title="Insurance Claim Fraud Platform API Gateway",
    description="Central API Gateway for Insurance Microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# MICROservice URLs
# --------------------------------------------------

AUTH_SERVICE = "http://127.0.0.1:8001"
CLAIM_SERVICE = "http://127.0.0.1:8002"
FRAUD_SERVICE = "http://127.0.0.1:8003"
NOTIFICATION_SERVICE = "http://127.0.0.1:8004"
RAG_SERVICE = "http://127.0.0.1:8005"


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


class ClaimRequest(BaseModel):
    customer_id: int
    policy_id: int
    claim_amount: float
    claim_type: str
    claim_date: str
    description: str | None = None


class FraudRequest(BaseModel):
    claim_id: int
    customer_id: int
    claim_amount: float
    previous_claims: int
    days_after_policy_start: int


class RAGDocumentRequest(BaseModel):
    document_id: int
    text: str
    document_type: str
    source: str


class RAGSearchRequest(BaseModel):
    query: str
    limit: int = 3


# --------------------------------------------------
# API GATEWAY ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "API Gateway",
        "status": "running",
        "services": {
            "auth": AUTH_SERVICE,
            "claim": CLAIM_SERVICE,
            "fraud": FRAUD_SERVICE,
            "notification": NOTIFICATION_SERVICE,
            "rag": RAG_SERVICE
        }
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# ==================================================
# AUTH SERVICE
# ==================================================

@app.post("/auth/login")
async def login(request: LoginRequest):

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE}/login",
            json=request.model_dump()
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


# ==================================================
# CLAIM SERVICE
# ==================================================

@app.post("/claims")
async def create_claim(
    request: ClaimRequest,
    current_user=Depends(get_current_user)
):
    # Admin and Claim Officer can create claims for any customer.
    if current_user["role"] in ["Admin", "Claim Officer"]:
        customer_id = request.customer_id

    # Customer can create a claim only for their own customer ID.
    elif current_user["role"] == "Customer":
        if current_user["customer_id"] is None:
            raise HTTPException(
                status_code=403,
                detail="Customer account is not linked to a customer record"
            )

        if request.customer_id != current_user["customer_id"]:
            raise HTTPException(
                status_code=403,
                detail="Customers can create claims only for their own account"
            )

        customer_id = current_user["customer_id"]

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to create claims"
        )

    claim_data = request.model_dump()
    claim_data["customer_id"] = customer_id

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CLAIM_SERVICE}/claims",
            json=claim_data
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


@app.get("/claims")
async def get_claims(current_user=Depends(get_current_user)):

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CLAIM_SERVICE}/claims"
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    claims = response.json()

    # Admin and Claim Officer can view all claims.
    if current_user["role"] in ["Admin", "Claim Officer"]:
        return claims

    # Customer can view only their own claims.
    if current_user["role"] == "Customer":
        customer_id = current_user["customer_id"]

        if customer_id is None:
            raise HTTPException(
                status_code=403,
                detail="Customer account is not linked to a customer record"
            )

        return [
            claim
            for claim in claims
            if claim.get("customer_id") == customer_id
        ]

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to view claims"
    )


# ==================================================
# FRAUD SERVICE
# ==================================================

@app.post("/fraud/analyze")
async def analyze_fraud(
    request: FraudRequest,
    current_user=Depends(
        require_roles("Admin", "Claim Officer")
    )
):

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FRAUD_SERVICE}/analyze",
            json=request.model_dump()
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


@app.get("/fraud/{claim_id}")
async def get_fraud_analysis(
    claim_id: int,
    current_user=Depends(get_current_user)
):

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FRAUD_SERVICE}/fraud-analysis/{claim_id}"
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


# ==================================================
# RAG SERVICE
# ==================================================

@app.post("/rag/documents")
async def add_rag_document(
    request: RAGDocumentRequest,
    current_user=Depends(
        require_roles("Admin")
    )
):

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAG_SERVICE}/documents",
            json=request.model_dump()
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


@app.post("/rag/search")
async def search_rag(
    request: RAGSearchRequest,
    current_user=Depends(get_current_user)
):

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RAG_SERVICE}/search",
            json=request.model_dump()
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()