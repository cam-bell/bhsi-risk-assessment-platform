# BHSI DATA FLOW ARCHITECTURE

## 📋 **COMPLETE SYSTEM DATA FLOW**

This document details **every step** that occurs when a search API endpoint is triggered, including all database interactions, LLM calls, file operations, and cloud service integrations.

---

## 🚀 **STEP-BY-STEP DATA FLOW**

### **PHASE 1: API REQUEST INITIATION**

#### **1.1 FastAPI Request Reception**
```
📥 POST /api/v1/search
File: app/api/v1/endpoints/search.py:unified_search()
```

**Input Processing:**
- **Request Model:** `UnifiedSearchRequest` (Pydantic validation)
- **Parameters Extracted:**
  - `company_name`: Target company name
  - `start_date`: Optional start date (YYYY-MM-DD)
  - `end_date`: Optional end date (YYYY-MM-DD) 
  - `days_back`: Fallback time range (default: 7 days)
  - `include_boe`: Boolean for BOE search (default: True)
  - `include_news`: Boolean for news search (default: True)

**Files Involved:**
- `app/api/v1/endpoints/search.py` - Main endpoint handler
- `app/api/v1/router.py` - Route registration
- `main.py` - FastAPI app initialization

**No Database Interactions Yet**

---

### **PHASE 2: COMPONENT INITIALIZATION**

#### **2.1 Streamlined Search Orchestrator Initialization**
```
🔧 StreamlinedSearchOrchestrator()
File: app/agents/search/streamlined_orchestrator.py:__init__()
```

**Actions:**
- Creates agent dictionary with streamlined agents
- No database connections established
- No external API calls made

**Files Involved:**
- `app/agents/search/streamlined_orchestrator.py`

#### **2.2 Optimized Hybrid Classifier Initialization**
```
🔧 OptimizedHybridClassifier()
File: app/agents/analysis/optimized_hybrid_classifier.py:__init__()
```

**Actions:**
- Compiles regex patterns for keyword matching
- Initializes performance statistics tracking
- Sets up lazy-loading for cloud classifier (not loaded yet)

**Files Involved:**
- `app/agents/analysis/optimized_hybrid_classifier.py`

**No Database Interactions**

---

### **PHASE 3: STREAMLINED SEARCH EXECUTION**

#### **3.1 Search Agent Configuration**
```
🔍 orchestrator.search_all()
File: app/agents/search/streamlined_orchestrator.py:search_all()
```

**Logic:**
- Determines active agents based on request parameters
- If `include_boe=True` → adds "boe" to active_agents
- If `include_news=True` → adds "newsapi" to active_agents

#### **3.2 BOE Agent Search (if enabled)**
```
📰 StreamlinedBOEAgent.search()
File: app/agents/search/streamlined_boe_agent.py:search()
```

**Date Range Processing:**
- Validates and adjusts date ranges to prevent future dates
- Ensures start_date ≤ end_date
- Handles weekend/holiday considerations

**BOE API Integration:**
- **File:** `app/agents/search/BOE.py`
- **Functions Called:**
  - `fetch_boe_summary(date_str)` - Gets BOE summary for specific date
  - `iter_items(summary)` - Iterates through BOE items
  - `full_text(item)` - Extracts full text content

**External API Calls:**
- **Target:** BOE Public API (`https://boe.es/...`)
- **Method:** HTTP GET requests for each date in range
- **Rate Limiting:** Respectful delays between requests
- **Error Handling:** 404 errors expected for non-publication days

**Data Processing:**
- Simple string matching: `query.lower() in title.lower()`
- **NO CLASSIFICATION DURING SEARCH** (major optimization)
- Extracts: title, section, date, URL, full text
- Returns structured results without risk analysis

**Files Involved:**
- `app/agents/search/streamlined_boe_agent.py`
- `app/agents/search/BOE.py`
- `app/agents/search/base_agent.py`

**No Database Interactions in Search Phase**

#### **3.3 NewsAPI Agent Search (if enabled)**
```
📱 StreamlinedNewsAPIAgent.search()
File: app/agents/search/streamlined_newsapi_agent.py:search()
```

**Date Range Adjustment:**
- Enforces NewsAPI 30-day historical limit
- Automatically adjusts start_date if outside limit
- Logs warnings when dates are modified

**NewsAPI Integration:**
- **Target:** NewsAPI.org (`https://newsapi.org/v2/everything`)
- **Authentication:** API key in headers
- **Parameters:**
  - `q`: Company name query
  - `language`: "es" (Spanish)
  - `from`/`to`: Date range
  - `pageSize`: Results per page (max 100)
  - `sortBy`: "publishedAt"

**External API Call:**
- **Method:** HTTP GET with async client (aiohttp)
- **Timeout:** 10 seconds
- **Rate Limiting:** Built into NewsAPI
- **Error Handling:** HTTP status and API error responses

**Data Processing:**
- **NO CLASSIFICATION DURING SEARCH** (major optimization)
- Extracts: title, source, author, date, URL, description, content
- Returns clean structured data without risk analysis

**Files Involved:**
- `app/agents/search/streamlined_newsapi_agent.py`
- `app/agents/search/base_agent.py`

**No Database Interactions in Search Phase**

---

### **PHASE 4: BULK HYBRID CLASSIFICATION**

#### **4.1 Classification Loop Initiation**
```
🏷️ Bulk Classification Phase
File: app/api/v1/endpoints/search.py:unified_search()
```

**Process:**
- Iterates through all search results from all sources
- Processes BOE results and NewsAPI articles separately
- Applies optimized hybrid classification to each document

#### **4.2 BOE Results Classification**
```
🔍 BOE Document Classification
For each BOE result:
```

**Input Data:**
- `text`: Full document text from BOE
- `title`: Document title (titulo)
- `source`: "BOE"
- `section`: Section code (seccion_codigo)

**Classification Call:**
```
📊 classifier.classify_document()
File: app/agents/analysis/optimized_hybrid_classifier.py:classify_document()
```

#### **4.3 Optimized Hybrid Classification Process**

**STAGE 1: Ultra-Fast Keyword Gate (µ-seconds)**
```
⚡ Keyword Gate Analysis
File: app/agents/analysis/optimized_hybrid_classifier.py:_keyword_gate()
```

**Section Code Check (fastest):**
- Checks if section in high_risk_sections: {'JUS', 'CNMC', 'AEPD', 'CNMV', 'BDE', 'DGSFP', 'SEPBLAC'}
- If match → Returns "High-Legal" with 0.95 confidence
- Processing time: ~0.05ms

**Pattern Matching (pre-compiled regex):**

1. **No-Legal Patterns (checked first for quick elimination):**
   - Sports: "fútbol", "deportes"
   - Business: "beneficios", "facturación", "crecimiento"
   - Entertainment: "entretenimiento", "espectáculos"
   - If match → Returns "No-Legal" with 0.90 confidence

2. **High-Legal Patterns:**
   - Bankruptcy: "concurso de acreedores", "administración concursal", "suspensión de pagos"
   - Criminal: "sentencia penal", "proceso penal", "delito societario"
   - Severe sanctions: "sanción grave", "expediente sancionador"
   - Financial crimes: "blanqueo de capitales", "financiación del terrorismo"
   - If match → Returns "High-Legal" with 0.92 confidence

3. **Medium-Legal Patterns:**
   - Warnings: "requerimiento", "advertencia", "apercibimiento"
   - Administrative: "expediente administrativo", "procedimiento sancionador"
   - Compliance: "deficiencia", "irregularidad", "incumplimiento"
   - If match → Returns "Medium-Legal" with 0.87 confidence

4. **Low-Legal Patterns:**
   - Regulatory: "circular", "normativa", "regulación"
   - Administrative: "autorización", "licencia", "registro"
   - If match → Returns "Low-Legal" with 0.82 confidence

5. **Short Text Filter:**
   - If text < 100 chars AND no legal indicators → Returns "No-Legal" with 0.85 confidence

**Performance Tracking:**
- Updates `stats["keyword_hits"]` counter
- Records processing time in milliseconds
- **90%+ of cases resolved here** (no LLM needed)

**STAGE 2: Smart LLM Routing (only for ambiguous cases)**
```
🧠 LLM Classification (only if keyword gate fails)
File: app/agents/analysis/optimized_hybrid_classifier.py:_should_use_llm()
```

**LLM Routing Decision:**
- Must contain legal content indicators: "tribunal", "juzgado", "sentencia", "proceso", "expediente", "sanción", "multa", "infracción", "normativ", "regulación"
- Must be substantial (≥50 characters)
- Skips routine administrative patterns: "nombramiento", "cese", "dimisión"

**If LLM Required:**
```
☁️ Cloud Gemini Classification
File: app/agents/analysis/cloud_classifier.py:classify_document()
```

**Cloud Service Call:**
- **Target:** `https://gemini-service-185303190462.europe-west1.run.app/classify`
- **Method:** HTTP POST with document data
- **Timeout:** 30 seconds
- **Payload:** JSON with text, title, source, section
- **Response:** Classification with label, confidence, reason

**Fallback Chain:**
1. **Primary:** Cloud Gemini Service
2. **Secondary:** Local Ollama/Llama3 (if cloud fails)
3. **Emergency:** Default "No-Legal" classification

**Performance Tracking:**
- Updates `stats["llm_calls"]` counter
- Records total processing time
- **<10% of cases require LLM** (major cost savings)

#### **4.4 News Articles Classification**
```
📱 News Article Classification
For each NewsAPI article:
```

**Input Data:**
- `text`: Article content or description
- `title`: Article headline
- `source`: "News"
- `section`: News source name

**Same hybrid classification process as BOE, optimized for news content**

#### **4.5 Result Aggregation**
```
📋 Result Processing
File: app/api/v1/endpoints/search.py:unified_search()
```

**For Each Classified Result:**
- Combines classification data with source metadata
- Adds performance metrics (processing_time_ms, method)
- Structures response according to API schema

**BOE Result Structure:**
```json
{
  "source": "BOE",
  "date": "2025-06-10",
  "title": "Document title",
  "summary": "Text summary...",
  "risk_level": "High-Legal",
  "confidence": 0.92,
  "method": "keyword_high_legal",
  "processing_time_ms": 0.15,
  "url": "https://boe.es/...",
  "identificador": "BOE-A-2025-...",
  "seccion": "JUS",
  "seccion_nombre": "Justicia"
}
```

**News Result Structure:**
```json
{
  "source": "News",
  "date": "2025-06-17T...",
  "title": "News headline",
  "summary": "Article description...",
  "risk_level": "Medium-Legal",
  "confidence": 0.87,
  "method": "keyword_medium_legal", 
  "processing_time_ms": 0.12,
  "url": "https://news.com/...",
  "author": "Reporter Name",
  "source_name": "News Source"
}
```

---

### **PHASE 5: DATA STORAGE (CONDITIONAL)**

#### **5.1 Raw Document Storage (if configured)**
```
💾 Raw Document Storage
File: app/crud/raw_docs.py
Table: raw_docs
```

**When Triggered:**
- Only if document ingestion is enabled
- Typically for BOE documents requiring persistent storage
- Not triggered by standard search API calls

**Database Operations:**
```sql
INSERT INTO raw_docs (
    source, 
    payload, 
    meta, 
    created_at
) VALUES (?, ?, ?, ?)
```

**Data Stored:**
- `source`: "BOE" or "NewsAPI"
- `payload`: JSON-encoded raw document
- `meta`: Metadata including identificador, section, URL
- `created_at`: Timestamp

#### **5.2 Events Storage (if configured)**
```
📊 Risk Events Storage
File: app/crud/events.py
Table: events
```

**When Triggered:**
- Only for high-risk classifications
- Configurable threshold (e.g., High-Legal or confidence > 0.8)
- Optional company association

**Database Operations:**
```sql
INSERT INTO events (
    company_id,
    title,
    description, 
    risk_level,
    confidence,
    source,
    date_occurred,
    classification_method,
    created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
```

#### **5.3 Company Association (if applicable)**
```
🏢 Company Entity Management
File: app/crud/company.py
Table: companies
```

**Company Lookup/Creation:**
```sql
SELECT id FROM companies WHERE name = ?
-- If not found:
INSERT INTO companies (name, created_at) VALUES (?, ?)
```

---

### **PHASE 6: CLOUD SERVICES INTEGRATION (OPTIONAL)**

#### **6.1 Cloud Gemini Service**
```
☁️ Gemini AI Classification
Service: https://gemini-service-185303190462.europe-west1.run.app
```

**When Called:**
- Only for ambiguous documents (failed keyword gate)
- Only if `_should_use_llm()` returns True
- Estimated <10% of total documents

**Request to Cloud Service:**
```http
POST /classify
Content-Type: application/json

{
  "text": "Document text...",
  "title": "Document title",
  "source": "BOE",
  "section": "JUS"
}
```

**Cloud Service Processing:**
- **File:** `app/services/gemini/main.py`
- **Model:** Gemini-1.5-Pro via Vertex AI
- **Prompt:** Spanish D&O risk analysis
- **Response:** JSON with label, confidence, reason

**Response from Cloud Service:**
```json
{
  "label": "High-Legal",
  "confidence": 0.91,
  "reason": "Procedimiento concursal detectado",
  "processing_time": 3.2
}
```

#### **6.2 Cloud Embedder Service (if semantic search enabled)**
```
🔍 Document Embedding
Service: https://embedder-service-185303190462.europe-west1.run.app
```

**When Called:**
- For semantic similarity search
- Vector storage and retrieval
- Not part of standard classification flow

**Request:**
```http
POST /embed
{
  "texts": ["Document text 1", "Document text 2", ...]
}
```

**Response:**
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "model": "text-embedding-004",
  "dimensions": 768
}
```

#### **6.3 Vector Search Service (if semantic search enabled)**
```
🔍 Vector Similarity Search
Service: https://vector-search-185303190462.europe-west1.run.app
```

**Storage:**
- In-memory vector store
- **File:** `app/services/vector_search/main.py`
- **Method:** Cosine similarity matching

#### **6.4 BigQuery Analytics Service (if analytics enabled)**
```
📊 Analytics & Reporting
Service: https://bigquery-analytics-185303190462.europe-west1.run.app
```

**Dataset:** `risk_monitoring`
**Tables:**
- `companies` - Company master data
- `events` - Risk events and classifications  
- `raw_docs` - Raw document storage

**When Called:**
- Batch analytics jobs
- Company risk scoring
- Historical trend analysis
- Not part of real-time search flow

---

### **PHASE 7: RESPONSE PREPARATION**

#### **7.1 Result Sorting and Filtering**
```
📋 Response Preparation
File: app/api/v1/endpoints/search.py:unified_search()
```

**Processing Steps:**
1. **Date Validation:**
   - Filters out results with invalid dates
   - Converts date formats to ISO standard
   - Handles parsing errors gracefully

2. **Sorting:**
   - Sorts by date (most recent first)
   - Secondary sort by risk level
   - Maintains source diversity

3. **Metadata Calculation:**
   - Counts total results by source
   - Calculates high-risk result count
   - Compiles performance statistics

#### **7.2 Performance Metrics Compilation**
```
📊 Performance Statistics
```

**Metrics Collected:**
- Total classification time
- Search time breakdown
- Keyword gate efficiency percentage
- LLM usage percentage
- Processing time per document
- Error rates and fallback usage

**Example Performance Data:**
```json
{
  "total_time_seconds": "4.21",
  "search_time_seconds": "2.85", 
  "classification_time_seconds": "1.36",
  "keyword_efficiency": "95.7%",
  "llm_usage": "4.3%",
  "performance_gain": "95.7% faster than LLM-only"
}
```

#### **7.3 Final Response Assembly**
```
📤 Response Generation
```

**Complete Response Structure:**
```json
{
  "company_name": "Banco Santander",
  "search_date": "2025-06-17T14:30:45.123Z",
  "date_range": {
    "start": "2025-06-15",
    "end": "2025-06-17", 
    "days_back": 3
  },
  "results": [...],
  "metadata": {
    "total_results": 23,
    "boe_results": 3,
    "news_results": 20,
    "high_risk_results": 1,
    "sources_searched": ["boe", "newsapi"]
  },
  "performance": {...}
}
```

---

## 🗄️ **DATABASE SCHEMA DETAILS**

### **Table: companies**
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table: events**
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER REFERENCES companies(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    risk_level VARCHAR(50),
    confidence FLOAT,
    source VARCHAR(100),
    date_occurred DATE,
    classification_method VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table: raw_docs**
```sql
CREATE TABLE raw_docs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(100) NOT NULL,
    payload BLOB,
    meta JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚡ **PERFORMANCE OPTIMIZATION SUMMARY**

### **Major Bottlenecks Eliminated:**
1. **LLM in Search Loops** - Removed classification from search agents
2. **Redundant API Calls** - Streamlined agent architecture  
3. **Inefficient Fallbacks** - Smart routing instead of chain
4. **Duplicate Processing** - Bulk classification after search

### **Current Performance Profile:**
- **Search Phase:** 2-5 seconds (data fetching only)
- **Classification Phase:** 1-3 seconds (90%+ keyword gate)
- **Total Response Time:** 3-10 seconds (vs previous 2+ minutes)
- **LLM Usage:** <10% of documents (vs previous 100%)
- **Cost Reduction:** 90%+ fewer cloud API calls

### **Monitoring Points:**
- Keyword gate efficiency (target: >90%)
- LLM routing accuracy (minimize false positives)
- Cloud service availability (fallback readiness)
- Response time percentiles (P95 < 15 seconds)
- Error rates by component (<1% target)

---

**This completes the comprehensive data flow documentation covering every file, database interaction, API call, and processing step in the BHSI Corporate Risk Assessment system.** 