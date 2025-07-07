"""
RAG Natural Language Analysis Endpoint

🚀 NEW FEATURE: Natural Language Risk Analysis using RAG
📁 ADDITIVE: This file is completely new and separate from existing endpoints
🔄 LEVERAGES: Existing cloud services (Vector Search + Gemini) + BigQuery vectors
⚠️ REMOVABLE: Can be deleted without affecting existing functionality

Usage: POST /api/v1/analysis/nlp/ask
Example: "What are the current risks for Banco Santander?"
"""

import logging
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import httpx
import os

# 🔒 SAFE IMPORT: Only using auth from existing system
from app.dependencies.auth import get_current_active_user

# 🔗 NEW IMPORT: Use BigQuery vector store for accurate searches
from app.services.vector_search.bigquery_vector_store import VectorSearchService
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# 📝 NEW ROUTER: Completely separate from existing routers
router = APIRouter()

# 🌐 CLOUD SERVICES: Using existing deployed services
VECTOR_SEARCH_URL = os.getenv("VECTOR_SEARCH_SERVICE_URL", "https://vector-search-185303190462.europe-west1.run.app")
GEMINI_SERVICE_URL = os.getenv("GEMINI_SERVICE_URL", "https://gemini-service-185303190462.europe-west1.run.app")

# 📋 NEW MODELS: RAG-specific request/response models
class RAGQueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question about corporate risks", min_length=10)
    max_documents: Optional[int] = Field(3, description="Maximum documents to retrieve", ge=1, le=10)
    company_filter: Optional[str] = Field(None, description="Filter by specific company name")
    language: Optional[str] = Field("es", description="Response language (es/en)")

class RAGDocumentSource(BaseModel):
    id: str
    score: float
    title: str
    company: str
    date: str
    source: str
    text_preview: str

class RAGAnalysisResponse(BaseModel):
    question: str
    answer: str
    sources: List[RAGDocumentSource]
    confidence: float
    methodology: str
    response_time_ms: int
    timestamp: str

# 🧠 RAG ORCHESTRATOR: Core RAG logic (NEW CLASS)
class RAGOrchestrator:
    """
    🚀 CLOUD-NATIVE RAG: Full integration with deployed microservices
    ✅ Uses: Vector Search Service (BigQuery) + Gemini Service
    """
    
    def __init__(self):
        self.vector_search_url = VECTOR_SEARCH_URL
        self.gemini_service_url = GEMINI_SERVICE_URL
    
    async def analyze_natural_language_query(self, query: RAGQueryRequest) -> RAGAnalysisResponse:
        """Main RAG analysis flow"""
        start_time = datetime.now()
        
        try:
            # Step 1: Retrieve relevant documents
            documents = await self._retrieve_documents(query)
            
            # Step 2: Generate context-aware response
            analysis = await self._generate_analysis(query.question, documents, query.language)
            
            # Step 3: Format response
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return RAGAnalysisResponse(
                question=query.question,
                answer=analysis["answer"],
                sources=self._format_sources(documents),
                confidence=analysis["confidence"],
                methodology="rag_vector_gemini",
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"RAG analysis failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"RAG analysis failed: {str(e)}")
    
    async def _retrieve_documents(self, query: RAGQueryRequest) -> List[Dict[str, Any]]:
        """🔍 STEP 1: Document retrieval using existing vector search service"""
        
        try:
            search_request = {
                "query": query.question,
                "k": query.max_documents
            }
            
            # Add company filter if specified
            if query.company_filter:
                search_request["filter"] = {"company": query.company_filter}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.vector_search_url}/search",
                    json=search_request
                )
                
                if response.status_code == 200:
                    results = response.json()
                    documents = results.get("results", [])
                    logger.info(f"Retrieved {len(documents)} documents for RAG analysis")
                    return documents
                else:
                    logger.error(f"Vector search failed: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Document retrieval failed: {str(e)}")
            return []
    
    async def _generate_analysis(self, question: str, documents: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """🧠 STEP 2: Generate analysis using existing Gemini service"""
        
        try:
            # Prepare context from retrieved documents
            context = self._prepare_context(documents)
            
            # Create RAG prompt for Gemini
            prompt = self._create_rag_prompt(question, context, language)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.gemini_service_url}/generate",
                    json={
                        "prompt": prompt,
                        "max_tokens": 800,
                        "temperature": 0.2
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    raw_answer = result.get("text", "No analysis generated")
                    # Remove asterisks and other markdown formatting to make text cleaner
                    clean_answer = self._clean_markdown_formatting(raw_answer)
                    return {
                        "answer": clean_answer,
                        "confidence": self._calculate_confidence(documents)
                    }
                else:
                    logger.error(f"Gemini analysis failed: {response.status_code} - {response.text}")
                    return {
                        "answer": "Lo siento, no pude generar un análisis en este momento debido a un error del servicio.",
                        "confidence": 0.0
                    }
                    
        except Exception as e:
            logger.error(f"Analysis generation failed: {str(e)}")
            return {
                "answer": f"Error en el análisis: {str(e)}",
                "confidence": 0.0
            }
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """📄 Prepare document context for Gemini analysis"""
        
        if not documents:
            return "No se encontraron documentos relevantes."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            company = metadata.get("company", "Desconocida")
            score = doc.get("score", 0)
            
            context_parts.append(f"""
DOCUMENTO {i} (Relevancia: {score:.2f}, Empresa: {company}):
{doc.get("document", "Sin contenido")}
""")
        
        return "\n".join(context_parts)
    
    def _create_rag_prompt(self, question: str, context: str, language: str) -> str:
        """🎯 Create specialized RAG prompt for D&O risk analysis"""
        
        language_instructions = {
            "es": "Responde en español. Proporciona un análisis ejecutivo claro y profesional.",
            "en": "Respond in English. Provide a clear and professional executive analysis."
        }
        
        return f"""
Eres un experto en análisis de riesgos corporativos D&O (Directores y Administradores). Analiza la siguiente pregunta basándote ÚNICAMENTE en los documentos proporcionados.

PREGUNTA: {question}

DOCUMENTOS DE CONTEXTO:
{context}

INSTRUCCIONES:
1. {language_instructions.get(language, language_instructions["es"])}
2. Basa tu respuesta SOLO en la información de los documentos
3. Si no hay información suficiente, dilo claramente
4. Destaca los riesgos clave y su impacto potencial
5. Proporciona información accionable para ejecutivos
6. Mantén un tono profesional y conciso
7. Menciona las fuentes cuando sea relevante

ANÁLISIS:
"""
    
    def _clean_markdown_formatting(self, text: str) -> str:
        """🧹 Remove asterisks and other markdown formatting to make text cleaner and more appealing"""
        
        if not text:
            return text
        
        # Remove bold markdown formatting (**text**)
        import re
        
        # Remove double asterisks (bold formatting)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        
        # Remove single asterisks (italic formatting) 
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        
        # Clean up any remaining standalone asterisks
        text = re.sub(r'\*+', '', text)
        
        # Clean up extra whitespace that might result from removing formatting
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Reduce multiple newlines
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)  # Remove leading whitespace on lines
        
        return text.strip()
    
    def _calculate_confidence(self, documents: List[Dict[str, Any]]) -> float:
        """📊 Calculate confidence based on document relevance scores"""
        
        if not documents:
            return 0.0
        
        total_score = sum(doc.get("score", 0) for doc in documents)
        avg_score = total_score / len(documents)
        
        # Convert to percentage
        confidence = min(avg_score * 100, 100.0)
        return round(confidence, 1)
    
    def _format_sources(self, documents: List[Dict[str, Any]]) -> List[RAGDocumentSource]:
        """📋 Format document sources for response"""
        
        sources = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            
            sources.append(RAGDocumentSource(
                id=doc.get("id", "unknown"),
                score=round(doc.get("score", 0), 2),
                title=metadata.get("titulo", "Sin título")[:100],
                company=metadata.get("company", "Desconocida"),
                date=metadata.get("fecha", "Fecha desconocida"),
                source=metadata.get("source", "Fuente desconocida"),
                text_preview=doc.get("document", "")[:200] + "..." if len(doc.get("document", "")) > 200 else doc.get("document", "")
            ))
        
        return sources

# 🌐 GLOBAL ORCHESTRATOR: Single instance for endpoint
rag_orchestrator = RAGOrchestrator()

# 🚀 NEW ENDPOINTS: RAG Natural Language Analysis
@router.post("/nlp/ask", response_model=RAGAnalysisResponse)
async def ask_natural_language_question(
    query: RAGQueryRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    🧠 Natural Language Risk Analysis using RAG
    
    Ask questions in natural language about corporate risks and get AI-powered insights.
    
    Examples:
    - "¿Cuáles son los riesgos actuales para Banco Santander?"
    - "What financial risks affect Spanish energy companies?"
    - "¿Hay algún problema regulatorio reciente en el sector bancario?"
    """
    
    logger.info(f"RAG query from user {current_user.get('username', 'unknown')}: {query.question[:100]}...")
    
    try:
        result = await rag_orchestrator.analyze_natural_language_query(query)
        
        logger.info(f"RAG analysis completed: {len(result.sources)} sources, {result.confidence}% confidence")
        
        return result
        
    except Exception as e:
        logger.error(f"RAG endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nlp/examples")
async def get_nlp_examples(current_user: dict = Depends(get_current_active_user)):
    """
    📚 Example questions for natural language analysis
    """
    
    return {
        "spanish_examples": [
            "¿Cuáles son los riesgos actuales para Banco Santander?",
            "¿Hay problemas regulatorios en el sector energético?",
            "¿Qué riesgos financieros afectan a las empresas españolas?",
            "¿Cuáles son los principales riesgos ESG en el sector bancario?",
            "¿Hay alguna investigación judicial reciente sobre empresas cotizadas?"
        ],
        "english_examples": [
            "What are the current risks for Banco Santander?",
            "Are there any regulatory issues in the energy sector?",
            "What financial risks affect Spanish companies?",
            "What are the main ESG concerns for banks?",
            "Are there any recent legal investigations of listed companies?"
        ],
        "tips": [
            "Be specific about the company or sector you're asking about",
            "Ask about specific risk types (financial, legal, regulatory, operational)",
            "Include time frames when relevant (e.g., 'recent risks', 'current issues')",
            "The system works best with Spanish company names and sectors"
        ]
    }

@router.get("/nlp/health")
async def rag_health_check():
    """
    🏥 Health check for RAG system dependencies
    """
    
    health_status = {
        "rag_orchestrator": "healthy",
        "vector_search_service": "unknown",
        "gemini_service": "unknown",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Check vector search service
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{VECTOR_SEARCH_URL}/health")
            health_status["vector_search_service"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health_status["vector_search_service"] = "unreachable"
    
    try:
        # Check Gemini service
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{GEMINI_SERVICE_URL}/health")
            health_status["gemini_service"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health_status["gemini_service"] = "unreachable"
    
    # Determine overall health
    if health_status["vector_search_service"] == "healthy" and health_status["gemini_service"] == "healthy":
        health_status["status"] = "healthy"
    else:
        health_status["status"] = "degraded"
    
    return health_status 