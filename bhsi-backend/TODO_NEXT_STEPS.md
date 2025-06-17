# BHSI TODO: Next Steps & Cloud Services Integration

## 🎯 **CURRENT SYSTEM STATUS (What We Have Today)**

### ✅ **Implemented & Working**
- **Core Search System**: Streamlined BOE + NewsAPI search (90%+ performance improvement)
- **Optimized Hybrid Classifier**: Keyword gate + smart LLM routing (<10% LLM usage)
- **Main API Endpoints**: `/api/v1/search` - unified search with classification
- **Health Monitoring**: System health and performance tracking
- **Documentation**: Comprehensive README and data flow documentation

### ✅ **Cloud Services Deployed (Not Yet Integrated)**
- **Gemini Service**: `https://gemini-service-185303190462.europe-west1.run.app`
  - `/classify` - Document risk classification
  - `/generate` - Text generation 
  - `/analyze_company` - Comprehensive company analysis
- **Embedder Service**: `https://embedder-service-185303190462.europe-west1.run.app`
  - `/embed` - Document embeddings using text-embedding-004
- **Vector Search Service**: `https://vector-search-185303190462.europe-west1.run.app`
  - `/embed` - Add documents to vector store
  - `/search` - Semantic similarity search
- **BigQuery Analytics**: `https://bigquery-analytics-185303190462.europe-west1.run.app`
  - `/analytics/company/{identifier}` - Company analytics
  - `/analytics/risk-trends` - Risk trend analysis
  - `/analytics/alerts` - Alert summaries
  - `/analytics/sectors` - Sector analysis

---

## 🚀 **PHASE 1: PRIORITY INTEGRATIONS (Start Small)**

### **1.1 Management Summary Endpoint (HIGH PRIORITY)**
**New Endpoint**: `POST /api/v1/analysis/management-summary`

**Purpose**: Provide executive-level explanation of why a company was classified with specific risk levels.

**Request:**
```json
{
  "company_name": "Banco Santander",
  "classification_results": [...],  // From search endpoint
  "include_evidence": true,
  "language": "es"
}
```

**Response:**
```json
{
  "company_name": "Banco Santander",
  "overall_risk": "orange",
  "executive_summary": "Executive summary in Spanish...",
  "risk_breakdown": {
    "legal": {
      "level": "red",
      "reasoning": "2 high-risk regulatory sanctions found",
      "evidence": ["BOE document 1", "News article 2"],
      "confidence": 0.92
    },
    "financial": {
      "level": "green", 
      "reasoning": "No financial distress indicators found",
      "evidence": [],
      "confidence": 0.85
    }
  },
  "key_findings": ["Finding 1", "Finding 2"],
  "recommendations": ["Action 1", "Action 2"],
  "generated_at": "2025-01-17T...",
  "method": "cloud_gemini_analysis"
}
```

**Implementation Files**:
- Create: `app/api/v1/endpoints/analysis.py`
- Update: `app/api/v1/router.py` (add analysis routes)
- Create: `app/agents/analysis/management_summarizer.py`

### **1.2 Cloud Gemini Integration for Management Summaries**
**Goal**: Use Cloud Gemini for generating executive summaries when keyword gate fails

**Integration Points**:
- `management_summarizer.py` calls Cloud Gemini service
- Fallback to local keyword-based summaries
- Cache summaries in database to avoid repeated LLM calls

**Implementation**:
```python
# In management_summarizer.py
async def generate_summary(self, company_name: str, classification_results: List[Dict]) -> Dict:
    # Try cloud Gemini first
    try:
        summary = await self._cloud_gemini_summary(company_name, classification_results)
        return summary
    except Exception:
        # Fallback to template-based summary
        return self._template_summary(company_name, classification_results)
```

### **1.3 Basic Analytics Integration**
**New Endpoint**: `GET /api/v1/companies/{company_name}/analytics`

**Purpose**: Basic analytics for a specific company using BigQuery service

**Response**:
```json
{
  "company_name": "Banco Santander",
  "total_events": 45,
  "risk_distribution": {"High-Legal": 3, "Medium-Legal": 12, "Low-Legal": 30},
  "latest_events": [...],
  "trend_last_30_days": [...],
  "alert_summary": {...}
}
```

**Implementation**:
- Add analytics method to `companies.py`
- Call BigQuery service directly for company analytics
- Handle service unavailability gracefully

---

## 🚀 **PHASE 2: ENHANCED FEATURES (Expand Gradually)**

### **2.1 Smart Classification Enhancement**
**Goal**: Use cloud services to improve classification accuracy for ambiguous cases

**Enhancement**:
- When keyword gate confidence < 0.8, call Cloud Gemini for second opinion
- Combine keyword + cloud results for hybrid confidence score
- Store classification rationale for management summaries

**Implementation**:
```python
# In optimized_hybrid_classifier.py
async def classify_with_cloud_enhancement(self, text: str, title: str) -> Dict:
    keyword_result = await self._keyword_gate(text, title)
    
    if keyword_result["confidence"] < 0.8:
        # Get second opinion from cloud
        cloud_result = await self._cloud_classification(text, title)
        # Combine results for final classification
        return self._combine_classifications(keyword_result, cloud_result)
    
    return keyword_result
```

### **2.2 Document Storage & Retrieval**
**New Endpoints**:
- `POST /api/v1/documents/store` - Store documents in vector database
- `GET /api/v1/documents/similar/{doc_id}` - Find similar documents

**Purpose**: Enable semantic search across historical documents

**Integration**:
- Use Embedder service to create embeddings
- Store in Vector Search service
- Link to BigQuery for metadata storage

### **2.3 Risk Trend Analysis**
**New Endpoint**: `GET /api/v1/analytics/trends`

**Purpose**: System-wide risk trends using BigQuery analytics

**Response**:
```json
{
  "period": "last_90_days",
  "overall_trends": [...],
  "sector_breakdown": [...],
  "risk_evolution": [...],
  "alert_patterns": [...]
}
```

---

## 🚀 **PHASE 3: ADVANCED FEATURES (Future Expansion)**

### **3.1 Real-time Alerting System**
**Goal**: Proactive risk monitoring with intelligent alerts

**Features**:
- Configurable risk thresholds per company
- Real-time monitoring of BOE/news feeds
- Smart alert deduplication
- Email/webhook notifications

### **3.2 Batch Processing & Monitoring**
**Goal**: Large-scale company analysis and monitoring

**Features**:
- Bulk company analysis endpoints
- Scheduled monitoring jobs
- Performance optimization for large datasets
- Background task processing

### **3.3 Advanced Analytics Dashboard**
**Goal**: Comprehensive risk analytics and reporting

**Features**:
- Sector risk comparisons
- Historical risk evolution
- Predictive risk modeling
- Custom report generation

---

## 🛠️ **IMPLEMENTATION PRIORITY ORDER**

### **Week 1-2: Management Summary**
1. ✅ Create `analysis.py` endpoint file
2. ✅ Implement `management_summarizer.py` 
3. ✅ Integrate Cloud Gemini service
4. ✅ Add basic template fallbacks
5. ✅ Test with existing classification results

### **Week 3-4: Basic Analytics**
1. ✅ Add company analytics endpoint
2. ✅ Integrate BigQuery service calls
3. ✅ Handle service failures gracefully
4. ✅ Add analytics to existing company analysis flow

### **Week 5-6: Enhanced Classification**
1. ✅ Modify hybrid classifier for cloud enhancement
2. ✅ Add confidence combination logic
3. ✅ Store rationale for summaries
4. ✅ Performance testing

---

## 📋 **SPECIFIC FILES TO CREATE/MODIFY**

### **New Files to Create**:
```
app/api/v1/endpoints/analysis.py          # Management summary endpoint
app/agents/analysis/management_summarizer.py  # Summary generation logic
app/agents/analytics/                     # Analytics integration
├── bigquery_client.py                   # BigQuery service client
├── analytics_service.py                 # Analytics orchestration
└── cache_manager.py                     # Response caching
```

### **Files to Modify**:
```
app/api/v1/router.py                      # Add analysis routes
app/api/v1/endpoints/companies.py        # Add analytics integration
app/agents/analysis/optimized_hybrid_classifier.py  # Cloud enhancement
app/core/config.py                        # Add cloud service URLs
```

### **Database Enhancements**:
```sql
-- Add summary cache table
CREATE TABLE analysis_summaries (
    id INTEGER PRIMARY KEY,
    company_name VARCHAR(255),
    summary_hash VARCHAR(64),
    summary_data TEXT,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Add classification rationale
ALTER TABLE events ADD COLUMN rationale TEXT;
```

---

## 🎯 **SUCCESS METRICS**

### **Phase 1 Targets**:
- ✅ Management summary generation time < 5 seconds
- ✅ Cloud service integration success rate > 95%
- ✅ Fallback handling for all service failures
- ✅ Spanish language summaries for all risk categories

### **Phase 2 Targets**:
- ✅ Analytics response time < 3 seconds
- ✅ Vector search precision > 80%
- ✅ Enhanced classification accuracy improvement > 10%

### **Performance Requirements**:
- ✅ Maintain current 3-10 second search response times
- ✅ Keep LLM usage under 15% (currently <10%)
- ✅ All new endpoints must have health checks and monitoring

---

## ⚠️ **IMPORTANT CONSIDERATIONS**

### **Error Handling**:
- All cloud service calls must have timeouts (30s max)
- Graceful degradation when services unavailable
- Clear error messages for users
- Fallback to local/cached results

### **Cost Management**:
- Cache management summaries (expire after 24h)
- Rate limiting for expensive cloud calls
- Monitor BigQuery usage costs
- Optimize vector search query frequency

### **Security**:
- Validate all company names and inputs
- Sanitize data before cloud service calls
- Log all cloud service interactions
- Implement request authentication for sensitive endpoints

---

**Start with Phase 1 (Management Summary) as it provides immediate user value and establishes patterns for cloud service integration. Each phase builds incrementally on the previous one while maintaining system stability and performance.** 