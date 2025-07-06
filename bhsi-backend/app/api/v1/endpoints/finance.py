from fastapi import APIRouter, HTTPException, Query
from app.agents.search.streamlined_yahoo_finance_agent import StreamlinedYahooFinanceAgent

router = APIRouter()

yahoo_agent = StreamlinedYahooFinanceAgent()

@router.get("/{ticker_symbol}")
def get_financial_info(ticker_symbol: str):
    try:
        # Use the agent's search method with ticker as the query
        result = yahoo_agent.search(ticker_symbol)
        # If the agent's search is async, run it in an event loop
        if hasattr(result, '__await__'):
            import asyncio
            result = asyncio.run(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-name")
def get_financial_info_by_name(company_name: str = Query(..., description="Company name")):
    try:
        # Use the agent's search method with company name as the query
        result = yahoo_agent.search(company_name)
        if hasattr(result, '__await__'):
            import asyncio
            result = asyncio.run(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 