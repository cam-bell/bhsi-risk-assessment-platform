"""
RAG System Configuration

🚀 NEW FILE: Isolated RAG configuration
⚠️ REMOVABLE: Can be deleted without affecting existing system
🔧 ADDITIVE: Uses existing environment variables where possible
"""

import os
from typing import Dict, Any

class RAGConfig:
    """
    🎯 RAG-specific configuration isolated from main system config
    📋 Uses existing cloud service URLs from environment
    """
    
    # 🌐 Cloud Services (using existing deployed services)
    VECTOR_SEARCH_URL = os.getenv(
        "VECTOR_SEARCH_URL", 
        "https://vector-search-185303190462.europe-west1.run.app"
    )
    
    GEMINI_SERVICE_URL = os.getenv(
        "GEMINI_SERVICE_URL",
        "https://gemini-service-185303190462.europe-west1.run.app"
    )
    
    # 🧠 RAG Parameters
    DEFAULT_MAX_DOCUMENTS = 3
    MAX_ALLOWED_DOCUMENTS = 10
    DEFAULT_LANGUAGE = "es"
    
    # ⏱️ Timeouts
    VECTOR_SEARCH_TIMEOUT = 30.0
    GEMINI_TIMEOUT = 60.0
    HEALTH_CHECK_TIMEOUT = 10.0
    
    # 📊 Response Quality
    MIN_CONFIDENCE_THRESHOLD = 0.1
    DEFAULT_CONFIDENCE = 0.0
    
    # 🎯 Prompting
    MAX_CONTEXT_LENGTH = 3000
    MAX_RESPONSE_TOKENS = 800
    TEMPERATURE = 0.2
    
    @classmethod
    def get_service_urls(cls) -> Dict[str, str]:
        """Get all service URLs for health checks"""
        return {
            "vector_search": cls.VECTOR_SEARCH_URL,
            "gemini": cls.GEMINI_SERVICE_URL
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate RAG configuration"""
        
        config_status = {
            "valid": True,
            "issues": [],
            "services": {}
        }
        
        # Check service URLs
        for service, url in cls.get_service_urls().items():
            if not url or not url.startswith("https://"):
                config_status["valid"] = False
                config_status["issues"].append(f"{service} URL invalid: {url}")
            
            config_status["services"][service] = {
                "url": url,
                "configured": bool(url and url.startswith("https://"))
            }
        
        return config_status

# 🌍 Global RAG configuration instance
rag_config = RAGConfig() 