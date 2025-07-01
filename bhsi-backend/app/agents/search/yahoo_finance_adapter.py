import json
from typing import Dict, Any

def yahoo_finance_data_to_rawdoc(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Yahoo Finance financial data dict to a dict suitable for RawDoc insertion.
    """
    payload_bytes = json.dumps(financial_data, sort_keys=True).encode("utf-8")
    meta = {
        "company_name": financial_data.get("company_name"),
        "ticker": financial_data.get("ticker"),
        "risk_level": financial_data.get("risk_level"),
        "risk_score": financial_data.get("risk_score"),
        "market_cap": financial_data.get("market_cap"),
        "current_price": financial_data.get("current_price"),
        "currency": financial_data.get("currency"),
    }
    return {
        "source": "YahooFinance",
        "payload": payload_bytes,
        "meta": meta
    } 