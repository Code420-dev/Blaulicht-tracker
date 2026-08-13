def assess_incident(title, category, hours_old):
    """
    Evaluates road hazard severity and combines it with recency.
    """
    lower_title = title.lower()
    
    # 1. Hazard Severity
    if any(word in lower_title for word in ['sperrung', 'gesperrt', 'vollsperrung', 'unfall', 'kollision']):
        safety_status = "🔴 Red Zone — Active Road Blockade / Avoid Route"
        base_hazard = 3
    elif any(word in lower_title for word in ['brand', 'feuer', 'polizeieinsatz', 'sek', 'evakuierung', 'stau']):
        safety_status = "🟡 Yellow Zone — Emergency Deployment Nearby"
        base_hazard = 2
    else:
        safety_status = "🟢 Green Zone — Informational Report"
        base_hazard = 1

    # 2. Calculate Combined Score (Freshness + Severity)
    # Incidents happening right now (< 6h old) with high risk score get top priority
    recency_bonus = max(0, (24 - hours_old) / 6)
    total_score = base_hazard + recency_bonus

    return safety_status, total_score