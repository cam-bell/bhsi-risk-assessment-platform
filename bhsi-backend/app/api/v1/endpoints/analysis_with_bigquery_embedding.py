"""
Enhanced Analysis Endpoint with BigQuery Vector Integration
🎯 Implements: Analysis → Keyword Gate → Embedding Service → BigQuery Vectors
🔗 Connects all components for complete vector pipeline
📊 Stores vectors in bhsi_dataset.vectors table
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import json
import uuid
from datetime import datetime, date

from app.dependencies.auth import get_current_user
from app.services.vector_search.bigquery_vector_store import BigQueryVectorStore

router = APIRouter()

class EnhancedAnalysisRequest(BaseModel):
    company_name: str
    days_back: int = 7
    include_boe: bool = True
    include_news: bool = True
    include_rss: bool = False
    force_refresh: bool = False
    # Vector pipeline options
    enable_embedding: bool = True
    risk_threshold: str = "medium"  # minimum risk level to embed
    max_documents_to_embed: int = 20

class AnalysisWithEmbeddingService:
    """
    Enhanced analysis service that integrates vector embedding
    """
    
    def __init__(self):
        self.embedding_service_url = "https://embedder-service-185303190462.europe-west1.run.app"
        self.base_url = "http://localhost:8000"
        self.vector_store = BigQueryVectorStore()
    
    async def embed_text(self, text: str) -> Optional[List[float]]:
        """Call embedding service to embed text"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.embedding_service_url}/embed",
                    json={"text": text}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("embedding")
                else:
                    print(f"❌ Embedding service error: {response.status_code}")
                    return None
        except Exception as e:
            print(f"❌ Embedding failed: {e}")
            return None
    
    def applies_keyword_gate(self, document: Dict[str, Any], threshold: str = "medium") -> bool:
        """Check if document passes keyword gate based on risk level"""
        risk_level = document.get("risk_level", "").lower()
        
        # Define risk hierarchy
        risk_hierarchy = {
            "low": 1,
            "medium": 2, 
            "high": 3,
            "legal": 4,
            "financial": 4,
            "regulatory": 4
        }
        
        threshold_level = risk_hierarchy.get(threshold.lower(), 2)
        
        # Check if any risk keywords indicate high risk
        for risk_keyword, level in risk_hierarchy.items():
            if risk_keyword in risk_level and level >= threshold_level:
                return True
        
        # Also check for specific D&O risk keywords
        do_keywords = [
            "director", "consejero", "administrador", "governance", 
            "corporate", "board", "junta", "responsabilidad",
            "legal", "regulatory", "compliance", "audit"
        ]
        
        text_content = f"{document.get('title', '')} {document.get('summary', '')}".lower()
        return any(keyword in text_content for keyword in do_keywords)
    
    async def process_company_with_embedding_pipeline(
        self, 
        request: EnhancedAnalysisRequest,
        auth_token: str
    ) -> Dict[str, Any]:
        """
        Complete analysis with embedding pipeline
        Flow: Analysis → Keyword Gate → Embedding → BigQuery Storage
        """
        
        print(f"\n🏭 ENHANCED ANALYSIS WITH BIGQUERY PIPELINE: {request.company_name}")
        print("="*80)
        
        # Step 1: Run standard company analysis
        print("1. 🔍 Running company analysis...")
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        search_data = {
            "company_name": request.company_name,
            "days_back": request.days_back,
            "include_boe": request.include_boe,
            "include_news": request.include_news,
            "include_rss": request.include_rss,
            "force_refresh": request.force_refresh
        }
        
        async with httpx.AsyncClient(timeout=90) as client:
            search_response = await client.post(
                f"{self.base_url}/api/v1/streamlined/search",
                json=search_data,
                headers=headers
            )
        
        if search_response.status_code != 200:
            raise HTTPException(
                status_code=search_response.status_code,
                detail=f"Analysis failed: {search_response.text}"
            )
        
        search_results = search_response.json()
        all_documents = search_results.get("results", [])
        
        print(f"   📄 Found {len(all_documents)} documents")
        
        # Step 2: Apply keyword gate filter
        print("2. 🚪 Applying keyword gate filter...")
        
        filtered_docs = []
        if request.enable_embedding:
            for doc in all_documents:
                if self.applies_keyword_gate(doc, request.risk_threshold):
                    filtered_docs.append(doc)
        
        print(f"   ✅ {len(filtered_docs)} documents passed keyword gate")
        
        # Step 3: Embed documents and store in BigQuery
        embedded_count = 0
        embedding_errors = []
        
        if request.enable_embedding and filtered_docs:
            print("3. 🤖 Embedding documents and storing in BigQuery...")
            
            # Limit documents to embed
            docs_to_embed = filtered_docs[:request.max_documents_to_embed]
            
            for i, doc in enumerate(docs_to_embed, 1):
                try:
                    # Prepare text content
                    text_content = doc.get("summary") or doc.get("title") or ""
                    if not text_content.strip():
                        continue
                    
                    print(f"   Processing document {i}/{len(docs_to_embed)}: {doc.get('title', 'N/A')[:50]}...")
                    
                    # Get embedding
                    vector = await self.embed_text(text_content[:2000])  # Limit text length
                    if not vector:
                        embedding_errors.append(f"Failed to embed: {doc.get('title', 'N/A')}")
                        continue
                    
                    # Prepare metadata for BigQuery
                    metadata = {
                        "company_name": request.company_name,
                        "title": doc.get("title"),
                        "text_summary": text_content[:1000],  # Truncate for storage
                        "source": doc.get("source"),
                        "risk_level": doc.get("risk_level"),
                        "publication_date": doc.get("date"),
                        "url": doc.get("url", ""),
                        "confidence": doc.get("confidence", 0),
                        "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
                    }
                    
                    # Store in BigQuery
                    event_id = await self.vector_store.add_vector(vector, metadata)
                    if event_id:
                        embedded_count += 1
                        print(f"     ✅ Stored vector: {event_id}")
                    else:
                        embedding_errors.append(f"Failed to store: {doc.get('title', 'N/A')}")
                
                except Exception as e:
                    embedding_errors.append(f"Error processing {doc.get('title', 'N/A')}: {str(e)}")
                    print(f"     ❌ Error: {e}")
        
        # Step 4: Test vector search with embedded documents
        bigquery_search_results = []
        if embedded_count > 0:
            print("4. 📊 Testing BigQuery vector search...")
            try:
                test_query_vector = await self.embed_text(f"riesgos para {request.company_name}")
                if test_query_vector:
                    bigquery_search_results = await self.vector_store.search(
                        test_query_vector, 
                        k=5, 
                        filters={"company_name": request.company_name}
                    )
                    print(f"   📚 BigQuery search found {len(bigquery_search_results)} relevant vectors")
            except Exception as e:
                print(f"   ❌ BigQuery search test failed: {e}")
        
        # Return comprehensive results
        return {
            "company_name": request.company_name,
            "analysis_timestamp": datetime.now().isoformat(),
            
            # Original analysis results
            "original_analysis": search_results,
            "total_documents_found": len(all_documents),
            
            # Vector pipeline results
            "vector_pipeline": {
                "enabled": request.enable_embedding,
                "documents_passed_keyword_gate": len(filtered_docs),
                "documents_embedded": embedded_count,
                "embedding_errors": embedding_errors,
                "risk_threshold": request.risk_threshold,
                "max_documents_limit": request.max_documents_to_embed
            },
            
            # BigQuery integration results
            "bigquery_integration": {
                "vectors_stored": embedded_count,
                "search_test_results": len(bigquery_search_results),
                "sample_search_results": bigquery_search_results[:3] if bigquery_search_results else []
            },
            
            # Summary
            "summary": {
                "success": embedded_count > 0,
                "documents_in_bigquery": embedded_count,
                "ready_for_rag": embedded_count > 0,
                "pipeline_status": "complete" if embedded_count > 0 else "partial"
            }
        }

# Initialize service
analysis_service = AnalysisWithEmbeddingService()

@router.post("/enhanced-analysis", response_model=Dict[str, Any])
async def enhanced_company_analysis(
    request: EnhancedAnalysisRequest,
    current_user = Depends(get_current_user)
):
    """
    Enhanced company analysis with BigQuery vector pipeline integration
    
    🎯 Complete Flow:
    1. Run company analysis (find documents)
    2. Apply keyword gate (filter high-risk documents) 
    3. Embed documents using cloud service
    4. Store vectors in BigQuery for persistence
    5. Test vector search functionality
    
    📊 Results include both original analysis and vector pipeline status
    """
    
    try:
        # Get auth token from user context
        auth_token = getattr(current_user, 'access_token', None)
        if not auth_token:
            # For demo purposes, create a temporary token
            auth_token = "demo_token"
        
        # Process with complete pipeline
        result = await analysis_service.process_company_with_embedding_pipeline(
            request, auth_token
        )
        
        return result
        
    except Exception as e:
        print(f"❌ Enhanced analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bigquery-vector-stats")
async def get_bigquery_vector_stats(current_user = Depends(get_current_user)):
    """
    Get comprehensive BigQuery vector store statistics
    """
    try:
        vector_store = BigQueryVectorStore()
        stats = await vector_store.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies-with-vectors")
async def get_companies_with_vectors(current_user = Depends(get_current_user)):
    """
    Get list of companies that have vectors stored in BigQuery
    """
    try:
        vector_store = BigQueryVectorStore()
        companies = await vector_store.get_companies()
        return {"companies": companies, "count": len(companies)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vectors/{company_name}")
async def delete_company_vectors(
    company_name: str,
    current_user = Depends(get_current_user)
):
    """
    Soft delete vectors for a specific company
    """
    try:
        vector_store = BigQueryVectorStore()
        success = await vector_store.delete_vectors(company_name)
        
        if success:
            return {"message": f"Vectors for {company_name} deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete vectors")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-complete-pipeline/{company_name}")
async def test_complete_pipeline(
    company_name: str,
    current_user = Depends(get_current_user)
):
    """
    Test the complete pipeline: Analysis → Embedding → BigQuery → RAG
    """
    try:
        # Run enhanced analysis
        request = EnhancedAnalysisRequest(
            company_name=company_name,
            enable_embedding=True,
            max_documents_to_embed=10
        )
        
        analysis_result = await analysis_service.process_company_with_embedding_pipeline(
            request, "demo_token"
        )
        
        # Test RAG if vectors were stored
        rag_test_success = False
        if analysis_result["vector_pipeline"]["documents_embedded"] > 0:
            try:
                # Simple RAG test
                headers = {"Content-Type": "application/json"}
                rag_data = {
                    "question": f"¿Cuáles son los riesgos más importantes para {company_name}?",
                    "max_documents": 5,
                    "company_filter": company_name,
                    "language": "es"
                }
                
                async with httpx.AsyncClient(timeout=60) as client:
                    rag_response = await client.post(
                        "http://localhost:8000/api/v1/analysis/nlp/ask",
                        json=rag_data,
                        headers=headers
                    )
                
                rag_test_success = rag_response.status_code == 200
                
            except Exception as e:
                print(f"RAG test error: {e}")
        
        return {
            "pipeline_test": analysis_result,
            "rag_test_success": rag_test_success,
            "complete_pipeline_working": (
                analysis_result["vector_pipeline"]["documents_embedded"] > 0 and 
                rag_test_success
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 