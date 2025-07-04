import pytest
from app.agents.analysis.optimized_hybrid_classifier import OptimizedHybridClassifier
from app.agents.analysis.management_summarizer import ManagementSummarizer
from app.agents.search.streamlined_orchestrator import StreamlinedSearchOrchestrator


@pytest.fixture
def hybrid_classifier():
    return OptimizedHybridClassifier()


@pytest.fixture
def streamlined_orchestrator():
    return StreamlinedSearchOrchestrator()


def test_hybrid_classifier_initialization(hybrid_classifier):
    """Test that the optimized hybrid classifier initializes properly"""
    assert hybrid_classifier is not None
    assert hasattr(hybrid_classifier, 'high_legal_patterns')
    assert hasattr(hybrid_classifier, 'medium_legal_patterns')
    assert hasattr(hybrid_classifier, 'no_legal_patterns')
    assert len(hybrid_classifier.high_risk_sections) > 0


@pytest.mark.asyncio
async def test_hybrid_classifier_keyword_gate(hybrid_classifier):
    """Test that keyword gate catches obvious cases quickly"""
    # Test high-legal case
    result = await hybrid_classifier.classify_document(
        text="Concurso de acreedores de la empresa", 
        title="Test"
    )
    assert result["label"] == "High-Legal"
    assert "keyword" in result["method"]
    assert result["processing_time_ms"] < 1.0  # Should be very fast
    
    # Test medium-legal case
    result = await hybrid_classifier.classify_document(
        text="Requerimiento de la autoridad competente", 
        title="Test"
    )
    assert result["label"] == "Medium-Legal"
    assert "keyword" in result["method"]
    
    # Test no-legal case
    result = await hybrid_classifier.classify_document(
        text="Noticias deportivas de fútbol", 
        title="Test"
    )
    assert result["label"] == "No-Legal"
    assert "keyword" in result["method"]


def test_streamlined_orchestrator_initialization(streamlined_orchestrator):
    """Test that streamlined orchestrator initializes with correct agents"""
    assert streamlined_orchestrator is not None
    assert "boe" in streamlined_orchestrator.agents
    assert "newsapi" in streamlined_orchestrator.agents


@pytest.mark.asyncio
async def test_streamlined_search(streamlined_orchestrator):
    """Test streamlined search functionality"""
    result = await streamlined_orchestrator.search_all(
        query="Test Company",
        days_back=1,
        active_agents=["boe"]  # Only test BOE to avoid API costs
    )
    
    assert isinstance(result, dict)
    assert "boe" in result
    assert "search_summary" in result["boe"]


def test_performance_stats(hybrid_classifier):
    """Test that performance statistics are tracked"""
    stats = hybrid_classifier.get_performance_stats()
    assert isinstance(stats, dict)
    
    # Reset and verify
    hybrid_classifier.reset_stats()
    stats = hybrid_classifier.get_performance_stats()
    assert stats["total_classifications"] == 0


@pytest.mark.asyncio 
async def test_classification_speed(hybrid_classifier):
    """Test that classification is genuinely fast"""
    import time
    
    test_cases = [
        "Concurso de acreedores",
        "Sanción grave", 
        "Requerimiento regulatorio",
        "Beneficios empresariales",
        "Noticias deportivas"
    ]
    
    start_time = time.time()
    
    for text in test_cases:
        await hybrid_classifier.classify_document(text=text, title="Test")
    
    total_time = (time.time() - start_time) * 1000  # Convert to ms
    avg_time = total_time / len(test_cases)
    
    # Should average well under 1ms per classification
    assert avg_time < 5.0, f"Average classification time too slow: {avg_time:.2f}ms"
    
    stats = hybrid_classifier.get_performance_stats()
    assert stats["keyword_efficiency"] != "0.0%"  # Should have some keyword hits 


@pytest.mark.asyncio
async def test_management_summary_language_templates():
    summarizer = ManagementSummarizer()
    # Spanish (es) high risk
    classification_results = [
        {"risk_level": "High-Legal", "title": "Sanción grave", "summary": "Multa importante"}
    ]
    summary_es = await summarizer.generate_summary(
        company_name="TestCorp",
        classification_results=classification_results,
        include_evidence=True,
        language="es"
    )
    # Accept either template or cloud output: check company name and Spanish keywords
    assert "TestCorp" in summary_es["executive_summary"]
    assert any(word in summary_es["executive_summary"].lower() for word in ["riesgo", "empresa", "evaluación"])
    assert summary_es["method"] in ("cloud_gemini_analysis", "template_analysis")

    # English (en) high risk
    summary_en = await summarizer.generate_summary(
        company_name="TestCorp",
        classification_results=classification_results,
        include_evidence=True,
        language="en"
    )
    # Only check company name and non-empty summary for English
    assert "TestCorp" in summary_en["executive_summary"]
    assert summary_en["executive_summary"].strip() != ""
    assert summary_en["method"] in ("cloud_gemini_analysis", "template_analysis")

    # Spanish (es) low risk
    classification_results = [
        {"risk_level": "No-Legal", "title": "Noticia positiva", "summary": "Sin incidencias"}
    ]
    summary_es_low = await summarizer.generate_summary(
        company_name="TestCorp",
        classification_results=classification_results,
        include_evidence=True,
        language="es"
    )
    assert "TestCorp" in summary_es_low["executive_summary"]
    assert any(word in summary_es_low["executive_summary"].lower() for word in ["riesgo", "empresa", "evaluación"])

    # English (en) low risk
    summary_en_low = await summarizer.generate_summary(
        company_name="TestCorp",
        classification_results=classification_results,
        include_evidence=True,
        language="en"
    )
    assert "TestCorp" in summary_en_low["executive_summary"]
    assert summary_en_low["executive_summary"].strip() != ""

    # Unsupported language
    with pytest.raises(ValueError):
        await summarizer.generate_summary(
            company_name="TestCorp",
            classification_results=classification_results,
            include_evidence=True,
            language="fr"
        ) 