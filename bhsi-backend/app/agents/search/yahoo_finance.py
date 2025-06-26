import yfinance as yf
from datetime import datetime, timedelta

def get_stock_info(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)

    # -- Current Summary Info --
    info = stock.info
    print(f"\n📊 Raw Info for {ticker_symbol}:\n{info}\n")

    print(f"\n📈 Stock Info for {ticker_symbol.upper()}:")
    print(f"Name: {info.get('shortName')}")
    print(f"Price: {info.get('regularMarketPrice')} {info.get('currency')}")
    print(f"Market Cap: {info.get('marketCap')}")
    print(f"52 Week High: {info.get('fiftyTwoWeekHigh')}")
    print(f"52 Week Low: {info.get('fiftyTwoWeekLow')}")
    print(f"Dividend Yield: {info.get('dividendYield')}")
    print(f"Forward PE: {info.get('forwardPE')}")
    print(f"Website: {info.get('website')}")

    # -- Share Price Drop Analysis --
    today = datetime.today().date()
    last_week = today - timedelta(days=7)
    hist = stock.history(start=str(last_week), end=str(today))

    if not hist.empty:
        latest_close = hist['Close'][-1]
        week_ago_close = hist['Close'][0]
        drop_pct = ((week_ago_close - latest_close) / week_ago_close) * 100
        print(f"\n📉 Share Price (7-day): {week_ago_close:.2f} → {latest_close:.2f} ({drop_pct:.2f}%)")
        if drop_pct > 5:
            print("⚠️ Significant drop in share price this week!")
    else:
        print("\n⚠️ No historical price data available.")

    # -- Revenue Trend Analysis --
    try:
        income_stmt = stock.financials
        if not income_stmt.empty:
            revenue = income_stmt.loc["Total Revenue"]
            if len(revenue) >= 2:
                rev_latest = revenue[0]
                rev_prev = revenue[1]
                rev_change = ((rev_latest - rev_prev) / rev_prev) * 100
                print(f"\n💰 Revenue Change YoY: {rev_prev:.0f} → {rev_latest:.0f} ({rev_change:.2f}%)")
                if rev_change < -10:
                    print("⚠️ Potential revenue decline year-over-year.")
        else:
            print("\n⚠️ Revenue data unavailable.")
    except Exception as e:
        print(f"\n⚠️ Error retrieving revenue data: {e}")

if __name__ == "__main__":
    get_stock_info("SAN")  # Santander on NYSE#this is the ticker symbol for Santander -> so we might need to have the input from front end come here 
