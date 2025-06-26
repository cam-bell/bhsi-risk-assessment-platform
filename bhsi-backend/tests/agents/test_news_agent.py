import asyncio
from app.agents.search.news_agent import NewsAgencyAgent

async def main():
    agent = NewsAgencyAgent()
    # Use a generic query that will match many articles
    results = await agent.search("empresa")
    print("Total results:", results["total"])
    print("Sample result:", results["results"][:1])

if __name__ == "__main__":
    asyncio.run(main())