def calculate_fraud_risk(
    claim_amount,
    previous_claims,
    days_after_policy_start
):
    risk_score = 0
    reasons = []

    # Rule 1: High claim amount
    if claim_amount > 75000:
        risk_score += 35
        reasons.append("High claim amount")

    # Rule 2: Multiple previous claims
    if previous_claims >= 3:
        risk_score += 25
        reasons.append("Multiple previous claims")

    # Rule 3: Claim submitted soon after policy activation
    if days_after_policy_start <= 7:
        risk_score += 30
        reasons.append(
            "Claim submitted shortly after policy activation"
        )

    # Rule 4: Very high claim amount
    if claim_amount > 150000:
        risk_score += 10
        reasons.append("Very high claim amount")

    # Keep score within 100
    if risk_score > 100:
        risk_score = 100

    # Determine risk level
    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if not reasons:
        reasons.append("No major fraud indicators detected")

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons
    }


if __name__ == "__main__":
    print("Insurance Claim Fraud Detection")
    print("=" * 45)

    result = calculate_fraud_risk(
        claim_amount=85000,
        previous_claims=4,
        days_after_policy_start=3
    )

    print(f"Fraud Risk Score : {result['risk_score']}/100")
    print(f"Risk Level       : {result['risk_level']}")
    print("Reasons:")

    for reason in result["reasons"]:
        print(f"- {reason}")