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

@pytest.mark.asyncio
def test_hybrid_classifier_batch_flow(hybrid_classifier, monkeypatch):
    """Test batch/cached hybrid classifier logic with a mix of cases."""
    import asyncio
    # Patch cloud_classifier to count LLM calls
    llm_call_count = {"count": 0}
    async def fake_batch_llm(docs):
        llm_call_count["count"] += 1
        # Return dummy LLM results
        return [
            {"label": "legal", "confidence": 0.91, "reason": "Ambiguous legal text", "method": "cloud_gemini_analysis"}
            for _ in docs
        ]
    # Patch _get_cloud_classifier to return a mock with classify_documents_batch
    class FakeCloud:
        def get_cache_key(self, doc):
            # Simple hash for testing
            return f"fake_key_{hash(str(doc))}"
        
        async def classify_documents_batch(self, docs):
            return await fake_batch_llm(docs)
    monkeypatch.setattr(hybrid_classifier, "_get_cloud_classifier", lambda: FakeCloud())

    docs = [
        {"text": "Concurso de acreedores", "title": "Test"},  # Obvious keyword
        {"text": "El consejo discutió una sentencia relevante pero no concluyente.", "title": "Test"},  # Ambiguous, contains 'sentencia', should trigger LLM
        {"text": "Noticias deportivas", "title": "Test"},    # No-Legal
    ]
    # Fallback Hierarchy (see image):
    # 1. Cloud Gemini (default for ambiguous)
    # 2. Local LLaMA (if Gemini fails)
    # 3. Keyword Regex (if both fail or match high-confidence regex)
    # 4. No-Legal default (avoid if possible)

    # First call: should trigger LLM for ambiguous only
    results = asyncio.run(hybrid_classifier.classify_documents_batch(docs))
    print("Cache after first call:", getattr(getattr(hybrid_classifier._get_cloud_classifier(), 'classifier', None), 'classification_cache', None))
    assert len(results) == 3
    assert results[0]["final_label"] == "High-Legal" or results[0]["keyword_label"] == "High-Legal"
    assert results[1]["final_label"] == "legal" and results[1]["source_used"] == "llm"
    assert results[2]["final_label"] == "No-Legal" or results[2]["keyword_label"] == "No-Legal"
    # All fields present
    for res in results:
        assert "final_label" in res and "final_score" in res and "source_used" in res
    # Second call: should use cache, no extra LLM calls
    print("Cache before second call:", getattr(getattr(hybrid_classifier._get_cloud_classifier(), 'classifier', None), 'classification_cache', None))
    results2 = asyncio.run(hybrid_classifier.classify_documents_batch(docs))
    print("Cache after second call:", getattr(getattr(hybrid_classifier._get_cloud_classifier(), 'classifier', None), 'classification_cache', None))
    assert llm_call_count["count"] == 1  # Only first call triggers LLM 