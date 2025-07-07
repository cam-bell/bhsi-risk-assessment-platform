from typing import List, Dict

def assess_risk(data: dict, news: List[Dict]) -> Dict[str, str]:
    """
    Aggregate financial data and news sentiment to produce a risk score.
    Rules:
    - If totalRevenue trend is declining OR negative cashflow = Orange
    - If debtToEquity > 2.5 = Red
    - If 1+ Red news headline = Red
    - Else = Green
    """
    # Check for Red news
    if any(item.get("sentiment") == "Red" for item in news):
        return {"riskLevel": "Red"}

    # Check debtToEquity
    debt_to_equity = data.get("debtToEquity")
    if debt_to_equity is not None:
        try:
            if float(debt_to_equity) > 2.5:
                return {"riskLevel": "Red"}
        except Exception:
            pass

    # Check totalRevenue trend (declining)
    revenue_trend_declining = False
    total_revenue = data.get("financials", {}).get("Total Revenue")
    if total_revenue and isinstance(total_revenue, dict):
        # Sort by period (column), check if latest < previous
        values = list(total_revenue.values())
        if len(values) >= 2 and values[0] < values[1]:
            revenue_trend_declining = True

    # Check negative cashflow
    cashflow = data.get("cashflow", {})
    net_cash = None
    if isinstance(cashflow, dict):
        # Try to find a net cashflow field
        for key in ["Total Cash From Operating Activities", "Change In Cash"]:
            v = cashflow.get(key)
            if v is not None:
                if isinstance(v, dict):
                    v = list(v.values())[0] if v else None
                net_cash = v
                break
    negative_cashflow = net_cash is not None and net_cash < 0

    if revenue_trend_declining or negative_cashflow:
        return {"riskLevel": "Orange"}

    return {"riskLevel": "Green"} 