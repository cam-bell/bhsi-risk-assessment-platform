# BHSI Corporate Risk Assessment API

A high-performance corporate risk assessment system that combines Bank of Spain (BOE) official documents and news sources with AI-powered classification for Spanish D&O (Directors & Officers) risk analysis.

## 🏗️ **SYSTEM ARCHITECTURE**

### **Core Design Philosophy**

The system follows a **streamlined architecture** optimized for performance:

1. **Fast Data Fetching** - Search agents fetch raw data without classification
2. **Bulk Hybrid Classification** - Optimized keyword gate + smart LLM routing
3. **Cloud-Native Services** - Microservices for scalability and reliability
4. **Intelligent Fallbacks** - Multiple classification tiers for optimal speed

### **Main Application Entry Point**

```
main.py                    # ← Single entry point for the entire application
```

### **API Structure**

```
app/
├── api/v1/
│   ├── router.py          # Main API router
│   └── endpoints/
│       ├── search.py      # 🔍 Unified search endpoints (BOE + News)
│       └── companies.py   # 🏢 Company analysis endpoints
```

### **Search Components (Ultra-Fast)**

```
app/agents/search/
├── streamlined_orchestrator.py      # Coordinates fast search agents
├── streamlined_boe_agent.py         # BOE data fetching (no classification)
├── streamlined_newsapi_agent.py     # News data fetching (no classification)
├── base_agent.py                    # Base class for search agents
└── BOE.py                          # BOE API integration utilities
```

### **Analysis Components (Optimized Hybrid)**

```
app/agents/analysis/
├── optimized_hybrid_classifier.py   # 90%+ keyword gate + LLM routing
├── cloud_classifier.py             # Cloud Gemini service integration
├── classifier.py                   # Local Ollama fallback classifier
├── gemini_agent.py                 # Gemini AI agent
├── cloud_embedder.py               # Cloud embedding service
├── embedder.py                     # Local embedding fallback
└── processor.py                    # Data processing utilities
```

### **Database Layer**

```
app/
├── models/                         # SQLAlchemy ORM models
│   ├── company.py                  # Company entity model
│   ├── events.py                   # Risk events model
│   ├── raw_docs.py                 # Raw document storage
│   └── user.py                     # User management
├── crud/                           # Database operations
│   ├── base.py                     # Base CRUD operations
│   ├── company.py                  # Company CRUD operations
│   ├── events.py                   # Events CRUD operations
│   └── raw_docs.py                 # Document CRUD operations
├── schemas/                        # Pydantic request/response models
│   └── company.py                  # Company API schemas
└── db/                            # Database configuration
    ├── base.py                     # Database base model
    ├── session.py                  # Database session management
    └── init_db.py                  # Database initialization
```

### **Core Configuration**

```
app/core/
├── config.py                       # Application configuration
└── keywords.py                     # Risk keyword management
```

### **Cloud Microservices**

```
app/services/                       # Google Cloud Run microservices
├── gemini/                         # Gemini AI classification service
│   ├── main.py                     # FastAPI service for Gemini
│   ├── Dockerfile                  # Container configuration
│   └── requirements.txt            # Service dependencies
├── embedder/                       # Document embedding service
│   ├── main.py                     # FastAPI service for embeddings
│   ├── Dockerfile                  # Container configuration
│   └── requirements.txt            # Service dependencies
├── vector_search/                  # Vector similarity search
│   ├── main.py                     # In-memory vector store
│   ├── Dockerfile                  # Container configuration
│   └── requirements.txt            # Service dependencies
└── bigquery/                       # Analytics and reporting
    ├── main.py                     # BigQuery integration service
    ├── Dockerfile                  # Container configuration
    └── requirements.txt            # Service dependencies
```

## 🚀 **PERFORMANCE OPTIMIZATIONS**

### **Problem Solved**

The original system was extremely slow (2+ minutes per search) because:

- BOE and NewsAPI agents called slow LLM classifier for every document in search loops
- Multiple redundant classification processes
- Inefficient fallback mechanisms

### **Solution Implemented**

1. **Streamlined Search Phase** - Fast data fetching only, no classification
2. **Optimized Hybrid Classification** - 90%+ handled by µ-second keyword gate
3. **Smart LLM Routing** - Only truly ambiguous cases sent to expensive LLM
4. **Bulk Processing** - Classify all results after search completion

### **Performance Results**

- ⚡ **Response Time:** 3-10 seconds (vs previous 2+ minutes)
- 🎯 **Keyword Efficiency:** 90%+ cases handled in µ-seconds
- 🧠 **LLM Usage:** <10% of cases require expensive LLM analysis
- 💰 **Cost Reduction:** 90%+ reduction in cloud API calls

## 📡 **API ENDPOINTS**

### **🔍 Main Search API**

```http
POST /api/v1/search
```

**Request:**

```json
{
  "company_name": "Banco Santander",
  "start_date": "2025-03-19",
  "end_date": "2025-06-17",
  "include_boe": true,
  "include_news": true
}
```

**Response Structure:**

```json
{
  "company_name": "Banco Santander",
  "search_date": "2025-06-17T...",
  "date_range": {...},
  "results": [
    {
      "source": "BOE",
      "date": "2025-06-10",
      "title": "...",
      "summary": "...",
      "risk_level": "High-Legal",
      "confidence": 0.92,
      "method": "keyword_high_legal",
      "processing_time_ms": 0.15,
      "url": "...",
      "identificador": "...",
      "seccion": "..."
    }
  ],
  "metadata": {
    "total_results": 23,
    "boe_results": 3,
    "news_results": 20,
    "high_risk_results": 1
  },
  "performance": {
    "keyword_efficiency": "95.7%",
    "llm_usage": "4.3%",
    "total_time_seconds": "4.21",
    "search_time_seconds": "2.85",
    "classification_time_seconds": "1.36"
  }
}
```

### **🏢 Company Analysis API**

```http
POST /api/v1/companies/analyze
GET  /api/v1/companies/system/status
```

### **📊 System Health & Performance**

```http
GET  /                           # API overview
GET  /health                     # Health check
GET  /api/v1/search/health       # Search services health
GET  /api/v1/search/performance  # Performance statistics
GET  /docs                       # Interactive API documentation
```

## 🧠 **AI CLASSIFICATION SYSTEM**

### **Optimized Hybrid Architecture**

```
📄 DOCUMENT
       ↓
🚀 STAGE 1: Keyword Gate (µ-seconds - 90%+ efficiency)
   ├─ Section Codes: JUS, CNMC, AEPD, CNMV, BDE → High-Legal
   ├─ High-Risk Patterns: "concurso", "sanción grave" → High-Legal
   ├─ Medium-Risk Patterns: "requerimiento", "advertencia" → Medium-Legal
   ├─ Low-Risk Patterns: "circular", "normativa" → Low-Legal
   └─ Non-Legal Patterns: "deportes", "beneficios" → No-Legal
       ↓ (only for ambiguous cases)
🧠 STAGE 2: Smart LLM Routing (3-5s - <10% usage)
   ├─ Cloud Gemini Service (Primary)
   ├─ Local Ollama Fallback (Secondary)
   └─ Default Classification (Emergency)
```

### **Risk Classification Categories**

- **High-Legal:** Bankruptcy, criminal sanctions, severe regulatory violations
- **Medium-Legal:** Administrative sanctions, regulatory warnings, compliance issues
- **Low-Legal:** Regulatory notices, administrative procedures, licensing
- **No-Legal:** Business news, sports, entertainment, routine operations

### **Spanish D&O Risk Patterns**

The keyword gate is specifically optimized for Spanish legal terminology:

- **Bankruptcy:** "concurso de acreedores", "administración concursal", "suspensión de pagos"
- **Sanctions:** "sanción grave", "expediente sancionador", "multa"
- **Legal Proceedings:** "sentencia penal", "proceso penal", "delito societario"
- **Regulatory:** "requerimiento", "advertencia", "incumplimiento"

## 🌐 **CLOUD SERVICES INTEGRATION**

### **Deployed Google Cloud Run Services**

| Service                | URL                                                            | Purpose                      | Status    |
| ---------------------- | -------------------------------------------------------------- | ---------------------------- | --------- |
| **Gemini AI**          | `https://gemini-service-185303190462.europe-west1.run.app`     | Advanced text classification | ✅ Active |
| **Embedder**           | `https://embedder-service-185303190462.europe-west1.run.app`   | Document embeddings          | ✅ Active |
| **Vector Search**      | `https://vector-search-185303190462.europe-west1.run.app`      | Similarity search            | ✅ Active |
| **BigQuery Analytics** | `https://bigquery-analytics-185303190462.europe-west1.run.app` | Data analytics               | ✅ Active |

### **Service Integration Flow**

1. **Primary Classification:** Cloud Gemini for contextual analysis
2. **Embedding Generation:** Cloud Embedder for semantic search
3. **Vector Storage:** Cloud Vector Search for similarity matching
4. **Analytics:** BigQuery for data insights and reporting

## 📝 **DATA SOURCES**

### **BOE (Boletín Oficial del Estado)**

- **Source:** Official Spanish government gazette
- **Coverage:** Legal proceedings, regulatory changes, company sanctions
- **API:** Direct integration with BOE's public API
- **Rate Limits:** No official limits, respectful usage implemented
- **Date Range:** Supports historical data, weekend/holiday aware

### **NewsAPI**

- **Source:** International news aggregator
- **Coverage:** Spanish language business and financial news
- **API:** RESTful API with authentication
- **Rate Limits:** 30-day historical limit (automatically handled)
- **Filtering:** Spanish language, business category focus

## 🔧 **DEVELOPMENT & DEPLOYMENT**

### **Quick Start**

```bash
# Development server
cd bhsi-backend
python main.py

# Production server
./start-prod.sh

# Run tests
pytest tests/

# Performance test
python quick_optimized_test.py
```

### **Environment Variables**

```bash
# Required for cloud services
GOOGLE_CLOUD_PROJECT=bhsi-corporate-analysis
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# API Keys
NEWSAPI_KEY=your_newsapi_key
BOE_API_KEY=optional_boe_key

# Database
DATABASE_URL=sqlite:///./bhsi.db

# Local fallback
OLLAMA_HOST=http://localhost:11434
```

### **Dependencies**

- **FastAPI:** Modern async web framework
- **SQLAlchemy:** Database ORM
- **Pydantic:** Data validation and serialization
- **Google Cloud:** AI services integration
- **aiohttp:** Async HTTP client
- **pytest:** Testing framework

## 📊 **DATABASE SCHEMA**

### **Tables**

- **companies:** Company entities and metadata
- **events:** Risk events and classifications
- **raw_docs:** Raw document storage for processing
- **users:** User management and authentication

### **Key Relationships**

- Company → Events (one-to-many)
- Events → Raw Documents (many-to-many)
- Users → Companies (many-to-many access control)

## 🔍 **MONITORING & PERFORMANCE**

### **Built-in Metrics**

- Classification method distribution
- Processing time breakdowns
- Keyword gate efficiency rates
- LLM usage statistics
- Search performance metrics

### **Health Checks**

- Service availability monitoring
- Database connection health
- Cloud service status
- Performance threshold alerts

## 📚 **TESTING**

### **Test Suite Coverage**

```bash
tests/
├── agents/
│   └── test_analysis.py          # Hybrid classifier tests
├── api/
│   └── test_companies.py         # API endpoint tests
└── utils/
    └── utils.py                  # Test utilities
```

### **Performance Benchmarks**

- Classification speed tests (<5ms average)
- Search performance validation
- Keyword gate efficiency verification
- End-to-end response time monitoring

## Google Cloud Authentication for Local Development

To use BigQuery and other Google Cloud services locally, you must authenticate with your Google account:

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) if you haven't already.
2. Run the following command in your terminal:

   ```sh
   gcloud auth application-default login
   ```

   This will open a browser window for you to log in. Once complete, your local environment will have the necessary credentials to access Google Cloud services (including BigQuery) using your IAM permissions.

**Note:** This is for development only. Production should use a service account with appropriate permissions.

---

**Built with:** FastAPI, Google Cloud, Gemini AI, SQLAlchemy, Pydantic

**Architecture:** Streamlined microservices with optimized hybrid AI classification

**Performance:** 90%+ improvement through intelligent keyword filtering and cloud optimization
