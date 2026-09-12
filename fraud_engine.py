def calculate_fraud_risk(
    amount,
    transaction_count=1,
    international=False,
    unusual_hour=False,
    new_device=False
):
    score = 0
    reasons = []

    if amount >= 100000:
        score += 40
        reasons.append("Very high transaction amount")
    elif amount >= 50000:
        score += 25
        reasons.append("High transaction amount")
    elif amount >= 10000:
        score += 10
        reasons.append("Moderately high transaction amount")

    if transaction_count >= 10:
        score += 25
        reasons.append("High number of recent transactions")
    elif transaction_count >= 5:
        score += 15
        reasons.append("Multiple recent transactions")

    if international:
        score += 15
        reasons.append("International transaction")

    if unusual_hour:
        score += 10
        reasons.append("Transaction made during unusual hours")

    if new_device:
        score += 15
        reasons.append("Transaction from a new device")

    score = min(score, 100)

    if score >= 60:
        risk_level = "High"
    elif score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if not reasons:
        reasons.append("No major risk indicators detected")

    return {
        "score": score,
        "risk_level": risk_level,
        "reasons": reasons
    }