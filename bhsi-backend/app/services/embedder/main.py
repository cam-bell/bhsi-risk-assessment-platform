import os
import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import anyio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize variables
client = None
api_key = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and clean up on shutdown."""
    global client, api_key
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY is missing; endpoints will return 500")
    else:
        try:
            genai.configure(api_key=api_key)
            client = genai
            logger.info("Successfully initialized Google AI client")
        except Exception as e:
            logger.error(f"Failed to initialize Google AI client: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

class EmbeddingRequest(BaseModel):
    text: str
    model: str = "models/text-embedding-004"

class EmbeddingResponse(BaseModel):
    embedding: list[float]
    model: str

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_embedding(text: str, model_name: str) -> list[float]:
    """Get embedding for text using Google's Generative AI API with retry logic."""
    if not client or not api_key:
        raise ValueError("Google AI client not configured")
        
    try:
        logger.info(f"Getting embedding for text using model: {model_name}")
        
        # Use the correct embedding method
        def _get_embedding_sync():
            result = genai.embed_content(
                model=model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        
        # Run the blocking API call in a threadpool
        embedding = await anyio.to_thread.run_sync(_get_embedding_sync)
        
        # Validate the response
        if not isinstance(embedding, list) or not all(isinstance(x, (int, float)) for x in embedding):
            logger.error(f"Invalid embedding response: {type(embedding)}")
            raise ValueError("Invalid embedding response format")
            
        logger.info(f"Successfully generated embedding of length: {len(embedding)}")
        return embedding
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

@app.post("/embed", response_model=EmbeddingResponse)
async def create_embedding(request: EmbeddingRequest):
    """Create an embedding for the given text."""
    try:
        if not client or not api_key:
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable - API key not configured"
            )
            
        logger.info(f"Received embedding request for model: {request.model}")
        
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
            
        # Get embedding
        embedding = await get_embedding(request.text, request.model)
        
        return EmbeddingResponse(
            embedding=embedding,
            model=request.model
        )
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies API key and model availability."""
    try:
        # Check if API key is configured
        if not client or not api_key:
            return {
                "status": "unhealthy",
                "api_key_configured": False,
                "model_available": False,
                "error": "API key not configured"
            }
            
        # Try a simple embedding to verify the model works
        def _test_embedding():
            result = genai.embed_content(
                model="models/text-embedding-004",
                content="test",
                task_type="retrieval_document"
            )
            return result['embedding']
        
        test_result = await anyio.to_thread.run_sync(_test_embedding)
        
        if not isinstance(test_result, list) or len(test_result) == 0:
            raise ValueError("Model test failed - could not generate test embedding")
        
        return {
            "status": "healthy",
            "api_key_configured": True,
            "model_available": True,
            "embedding_dimension": len(test_result)
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
        "service": "Embedder Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "embed": "/embed"
        }
    } 