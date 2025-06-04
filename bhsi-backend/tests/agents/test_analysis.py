import pytest
from typing import Dict, List
from app.agents.analysis.gemini_agent import GeminiAgent
from app.agents.analysis.processor import DataProcessor
from app.agents.analysis.orchestrator import AnalysisOrchestrator


@pytest.fixture
def gemini_agent():
    return GeminiAgent()


@pytest.fixture
def data_processor():
    return DataProcessor()


@pytest.fixture
def analysis_orchestrator():
    return AnalysisOrchestrator()


def test_gemini_agent_initialization(gemini_agent):
    assert gemini_agent.api_key is not None
    assert gemini_agent.model is not None
    assert "turnover" in gemini_agent.risk_criteria
    assert "shareholding" in gemini_agent.risk_criteria
    assert "bankruptcy" in gemini_agent.risk_criteria
    assert "legal" in gemini_agent.risk_criteria
    assert "corruption" in gemini_agent.risk_criteria


def test_data_processor_initialization(data_processor):
    assert "turnover" in data_processor.keywords
    assert "shareholding" in data_processor.keywords
    assert "bankruptcy" in data_processor.keywords
    assert "legal" in data_processor.keywords
    assert "corruption" in data_processor.keywords


@pytest.mark.asyncio
async def test_gemini_agent_analyze_text(gemini_agent):
    text = "Company shows strong financial performance with consistent growth"
    result = await gemini_agent.analyze_text(text, "turnover")
    assert result in ["green", "orange", "red"]


def test_data_processor_classify_results(data_processor):
    test_results = {
        "GoogleSearchAgent": [
            {
                "title": "Company Reports Strong Growth",
                "snippet": "The company shows positive revenue trends",
                "source": "news.com"
            }
        ]
    }
    classified = data_processor._classify_results(test_results)
    assert "turnover" in classified
    assert len(classified["turnover"]) > 0


@pytest.mark.asyncio
async def test_analysis_orchestrator(analysis_orchestrator):
    test_results = {
        "GoogleSearchAgent": [
            {
                "title": "Company Reports Strong Growth",
                "snippet": "The company shows positive revenue trends",
                "source": "news.com"
            }
        ],
        "BingSearchAgent": [
            {
                "title": "Company Maintains Stable Ownership",
                "snippet": "No major changes in shareholding structure",
                "source": "business.com"
            }
        ]
    }
    
    analysis = await analysis_orchestrator.analyze_company(test_results)
    assert "risk_scores" in analysis
    assert "processed_results" in analysis
    assert "analysis_summary" in analysis
    
    formatted = analysis_orchestrator.format_for_database(analysis)
    assert "turnover" in formatted
    assert "shareholding" in formatted
    assert "bankruptcy" in formatted
    assert "legal" in formatted
    assert "corruption" in formatted
    assert "overall" in formatted 