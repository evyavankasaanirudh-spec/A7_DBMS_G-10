from pydantic import BaseModel
from datetime import date


class ClaimCreate(BaseModel):
    customer_id: int
    policy_id: int
    claim_amount: float
    claim_type: str
    claim_date: date
    description: str | None = None


class ClaimResponse(BaseModel):
    claim_id: int
    customer_id: int
    policy_id: int
    claim_amount: float
    claim_type: str
    claim_date: date
    description: str | None
    status: str | None