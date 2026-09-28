class Claim:
    def __init__(
        self,
        claim_id,
        customer_id,
        policy_id,
        claim_amount,
        claim_type,
        claim_date,
        description,
        status
    ):
        self.claim_id = claim_id
        self.customer_id = customer_id
        self.policy_id = policy_id
        self.claim_amount = claim_amount
        self.claim_type = claim_type
        self.claim_date = claim_date
        self.description = description
        self.status = status