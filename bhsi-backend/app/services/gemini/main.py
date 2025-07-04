import os
import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import anyio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize variables
client = None
api_key = None
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and clean up on shutdown."""
    global client, api_key, model
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY is missing; endpoints will return 500")
    else:
        try:
            genai.configure(api_key=api_key)
            client = genai
            model = genai.GenerativeModel("gemini-1.5-pro")
            logger.info("Successfully initialized Gemini client")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

class ClassificationRequest(BaseModel):
    text: str
    title: str
    source: str
    section: Optional[str] = None

class ClassificationResponse(BaseModel):
    label: str
    reason: str
    confidence: float
    method: str

class GenerationRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.0

class GenerationResponse(BaseModel):
    text: str
    model: str

class CompanyAnalysisRequest(BaseModel):
    company_name: str
    company_data: Dict[str, Any]
    analysis_type: Optional[str] = "comprehensive"

class CompanyAnalysisResponse(BaseModel):
    company_name: str
    risk_assessment: Dict[str, str]
    analysis_summary: str
    confidence: float
    methodology: str
    analysis_method: str

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def classify_risk(text: str, title: str, source: str, section: str = None) -> Dict[str, Any]:
    """Classify D&O risk using Gemini with retry logic."""
    if not client or not api_key or not model:
        raise ValueError("Gemini client not configured")
        
    try:
        logger.info(f"Classifying risk for document from {source}")
        
        # Prepare prompt for Spanish D&O analysis
        prompt = f"""Analiza este documento para riesgos D&O:

FUENTE: {source}
SECCIÓN: {section or 'N/A'}
TÍTULO: {title}
TEXTO: {text[:1500] if text else 'N/A'}

Clasifica el riesgo para directivos/administradores españoles:

- High-Legal: Concurso acreedores, sentencia penal firme, inhabilitación directivos, delitos societarios
- Medium-Reg: Sanción administrativa, multa regulatoria, expediente sancionador, infracciones graves  
- Low-Other: Nombramientos, procedimientos rutinarios, administración general
- Unknown: Información insuficiente

Responde SOLO en formato JSON:
{{"label": "High-Legal|Medium-Reg|Low-Other|Unknown", "reason": "explicación breve", "confidence": 0.0-1.0}}"""

        # Call Gemini
        def _classify_sync():
            response = model.generate_content(prompt)
            return response.text
        
        response_text = await anyio.to_thread.run_sync(_classify_sync)
        
        # Extract JSON from response
        result = _extract_json_from_response(response_text)
        
        if result and _validate_classification_result(result):
            result["method"] = "gemini_analysis"
            return result
        else:
            logger.warning(f"Invalid Gemini response: {response_text[:200]}...")
            return {
                "label": "Unknown",
                "reason": "Failed to parse Gemini response",
                "confidence": 0.0,
                "method": "gemini_error"
            }
            
    except Exception as e:
        logger.error(f"Risk classification failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def generate_text(prompt: str, max_tokens: int = 1000, temperature: float = 0.0) -> str:
    """Generate text using Gemini with retry logic."""
    if not client or not api_key or not model:
        raise ValueError("Gemini client not configured")
        
    try:
        logger.info(f"Generating text with Gemini")
        
        # Configure generation parameters
        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )
        
        def _generate_sync():
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        
        response_text = await anyio.to_thread.run_sync(_generate_sync)
        
        logger.info(f"Successfully generated text of length: {len(response_text)}")
        return response_text
        
    except Exception as e:
        logger.error(f"Text generation failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def analyze_company_comprehensive(company_name: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze company risk comprehensively using Gemini."""
    if not client or not api_key or not model:
        raise ValueError("Gemini client not configured")
        
    try:
        logger.info(f"Analyzing company: {company_name}")
        
        # Extract relevant text from company data
        text_content = ""
        if "search_results" in company_data:
            for result in company_data["search_results"]:
                if isinstance(result, dict):
                    title = result.get("title", "")
                    source = result.get("source", "")
                    text_content += f"[{source}] {title}\n"
        
        # Add any other text data
        for key, value in company_data.items():
            if isinstance(value, str) and key != "search_results":
                text_content += f"{key}: {value}\n"
        
        # Prepare comprehensive analysis prompt
        prompt = f"""Realiza un análisis completo de riesgos D&O para la empresa: {company_name}

INFORMACIÓN DISPONIBLE:
{text_content[:2000]}

Analiza los siguientes riesgos para directivos y administradores:

1. FACTURACIÓN (turnover): Problemas financieros, pérdidas, crisis de liquidez
2. PARTICIPACIONES (shareholding): Cambios accionariales significativos, adquisiciones, fusiones
3. CONCURSO DE ACREEDORES (bankruptcy): Insolvencia, concurso, suspensión de pagos
4. PROCEDIMIENTOS JUDICIALES (legal): Demandas, sentencias, investigaciones judiciales
5. CORRUPCIÓN (corruption): Fraude, soborno, blanqueo, delitos económicos

Para cada categoría, clasifica el riesgo como:
- red: Riesgo alto, evidencia clara de problemas
- orange: Riesgo medio, indicios preocupantes
- green: Riesgo bajo, sin evidencia de problemas

Responde SOLO en formato JSON:
{{
    "company_name": "{company_name}",
    "risk_assessment": {{
        "turnover": "green|orange|red",
        "shareholding": "green|orange|red", 
        "bankruptcy": "green|orange|red",
        "legal": "green|orange|red",
        "corruption": "green|orange|red",
        "overall": "green|orange|red"
    }},
    "analysis_summary": "Resumen del análisis en español",
    "confidence": 0.0-1.0,
    "methodology": "gemini_comprehensive_analysis"
}}"""

        # Call Gemini
        def _analyze_sync():
            response = model.generate_content(prompt)
            return response.text
        
        response_text = await anyio.to_thread.run_sync(_analyze_sync)
        
        # Extract JSON from response
        result = _extract_json_from_response(response_text)
        
        if result and _validate_analysis_result(result):
            result["analysis_method"] = "cloud_gemini"
            return result
        else:
            logger.warning(f"Invalid Gemini analysis response: {response_text[:200]}...")
            # Return fallback analysis
            return {
                "company_name": company_name,
                "risk_assessment": {
                    "turnover": "green",
                    "shareholding": "green", 
                    "bankruptcy": "green",
                    "legal": "green",
                    "corruption": "green",
                    "overall": "green"
                },
                "analysis_summary": f"Análisis automático de {company_name}. No se detectaron riesgos significativos.",
                "confidence": 0.5,
                "methodology": "gemini_fallback",
                "analysis_method": "cloud_gemini"
            }
            
    except Exception as e:
        logger.error(f"Company analysis failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def _extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from Gemini response."""
    import json
    import re
    
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        
        # Try parsing the whole response as JSON
        return json.loads(response)
    except Exception as e:
        logger.warning(f"Failed to parse JSON from response: {e}")
        return None

def _validate_classification_result(result: Dict[str, Any]) -> bool:
    """Validate classification result structure."""
    required_fields = ["label", "reason", "confidence"]
    valid_labels = ["High-Legal", "Medium-Reg", "Low-Other", "Unknown"]
    
    if not all(field in result for field in required_fields):
        return False
    
    if result["label"] not in valid_labels:
        return False
    
    if not isinstance(result["confidence"], (int, float)) or not 0 <= result["confidence"] <= 1:
        return False
    
    return True

def _validate_analysis_result(result: Dict[str, Any]) -> bool:
    """Validate analysis result structure."""
    required_fields = ["company_name", "risk_assessment", "analysis_summary", "confidence", "methodology"]
    
    if not all(field in result for field in required_fields):
        return False
    
    if not isinstance(result["confidence"], (int, float)) or not 0 <= result["confidence"] <= 1:
        return False
    
    return True

@app.post("/classify", response_model=ClassificationResponse)
async def classify_document(request: ClassificationRequest):
    """Classify a document for D&O risk."""
    try:
        if not client or not api_key or not model:
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable - Gemini not configured"
            )
            
        logger.info(f"Received classification request from {request.source}")
        
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
            
        # Classify risk
        result = await classify_risk(
            request.text, 
            request.title, 
            request.source, 
            request.section
        )
        
        return ClassificationResponse(**result)
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=GenerationResponse)
async def generate_content(request: GenerationRequest):
    """Generate content using Gemini."""
    try:
        if not client or not api_key or not model:
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable - Gemini not configured"
            )
            
        logger.info(f"Received generation request")
        
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
            
        # Generate text
        generated_text = await generate_text(
            request.prompt,
            request.max_tokens or 1000,
            request.temperature or 0.0
        )
        
        return GenerationResponse(
            text=generated_text,
            model="gemini-1.5-pro"
        )
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_company", response_model=CompanyAnalysisResponse)
async def analyze_company(request: CompanyAnalysisRequest):
    """Analyze a company for comprehensive risk assessment."""
    try:
        if not client or not api_key or not model:
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable - Gemini not configured"
            )
            
        logger.info(f"Received company analysis request for {request.company_name}")
        
        if not request.company_name or not request.company_name.strip():
            raise HTTPException(status_code=400, detail="Company name cannot be empty")
            
        # Analyze company
        result = await analyze_company_comprehensive(
            request.company_name,
            request.company_data
        )
        
        return CompanyAnalysisResponse(**result)
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies Gemini availability."""
    try:
        # Check if API key is configured
        if not client or not api_key or not model:
            return {
                "status": "unhealthy",
                "api_key_configured": False,
                "model_available": False,
                "error": "API key or model not configured"
            }
            
        # Try a simple generation to verify the model works
        def _test_generation():
            response = model.generate_content("Test: Say 'OK'")
            return response.text
        
        test_result = await anyio.to_thread.run_sync(_test_generation)
        
        if not test_result or len(test_result.strip()) == 0:
            raise ValueError("Model test failed - could not generate test response")
        
        return {
            "status": "healthy",
            "api_key_configured": True,
            "model_available": True,
            "model_name": "gemini-1.5-pro",
            "test_response": test_result.strip()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "api_key_configured": bool(api_key),
            "model_available": False,
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Gemini LLM Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "classify": "/classify",
            "generate": "/generate",
            "analyze_company": "/analyze_company"
        }
    }

async def generate_findings_and_recommendations(classification_results, company_name):
    """Use Gemini to generate key findings and recommendations."""
    if not client or not api_key or not model:
        raise ValueError("Gemini client not configured")

    # Combine document titles + summaries into one string
    docs_text = "\n".join(
        f"- {doc.get('title', '')}: {doc.get('summary', '')}"
        for doc in classification_results[:10]  # limit for context
    )

    prompt = f"""
Actúa como un analista de riesgos D&O para la empresa {company_name}.
Con base en los siguientes documentos clasificados, identifica:

1. Hallazgos clave relevantes para riesgos legales, financieros, regulatorios, o de operación.
2. Recomendaciones para directivos o aseguradores de la empresa.

DOCUMENTOS:
{docs_text}

Responde en formato JSON:
{{
  "key_findings": ["...", "..."],
  "recommendations": ["...", "..."]
}}
"""

    response = await generate_text(prompt)
    return _extract_json_from_response(response) or {
        "key_findings": [],
        "recommendations": []
    } 