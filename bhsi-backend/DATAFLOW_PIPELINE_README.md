# BHSI Dataflow Pipeline - Comprehensive Architecture Guide

## 🏗️ **System Overview**

The BHSI (Berkshire Hathaway Specialty Insurance) Corporate Project is a comprehensive risk assessment system that analyzes Spanish companies through multiple data sources. The system employs a sophisticated dataflow pipeline that combines real-time data collection, intelligent classification, and advanced analytics.

## 📊 **Core Architecture Components**

### **1. Data Collection Layer (Agents)**

- **Search Agents**: Collect data from multiple sources
- **Analysis Agents**: Process and classify collected data
- **Analytics Agents**: Generate insights and business intelligence

### **2. API Layer**

- **RESTful Endpoints**: Handle client requests and orchestrate workflows
- **Background Processing**: Manage long-running tasks
- **Data Validation**: Ensure data integrity

### **3. Services Layer**

- **Database Integration**: Persist and retrieve data
- **Cloud Services**: External AI/ML processing
- **Analytics Services**: Business intelligence and reporting

## 🔄 **Complete Dataflow Pipeline**

### **Phase 1: Request Initiation**

#### **1.1 API Endpoint Reception**

```
📥 POST /api/v1/streamlined-search
📥 POST /api/v1/companies/analyze
📥 POST /api/v1/companies/batch-analyze
```

**Entry Points:**

- `app/api/v1/endpoints/streamlined_search.py` - Fast search with optimized classification
- `app/api/v1/endpoints/companies.py` - Comprehensive company analysis
- `app/api/v1/endpoints/analysis.py` - Risk assessment endpoints

**Request Processing:**

- Pydantic validation of input parameters
- Company name normalization
- Date range validation
- Source selection (BOE, NewsAPI, RSS feeds)

### **Phase 2: Data Collection (Search Agents)**

#### **2.1 Streamlined Search Orchestrator**

```python
# File: app/agents/search/streamlined_orchestrator.py
class StreamlinedSearchOrchestrator:
    """Ultra-fast search orchestrator - data fetching only"""

    def __init__(self):
        self.agents = {
            "boe": StreamlinedBOEAgent(),
            "newsapi": StreamlinedNewsAPIAgent(),
            "elpais": StreamlinedElPaisAgent(),
            "expansion": StreamlinedExpansionAgent(),
            "elmundo": StreamlinedElMundoAgent(),
            "abc": StreamlinedABCAgent(),
            "lavanguardia": StreamlinedLaVanguardiaAgent(),
            "elconfidencial": StreamlinedElConfidencialAgent(),
            "eldiario": StreamlinedElDiarioAgent(),
            "europapress": StreamlinedEuropaPressAgent(),
            "yahoo_finance": StreamlinedYahooFinanceAgent()
        }
```

**Key Features:**

- **Parallel Processing**: Multiple agents run concurrently
- **No Classification During Search**: Optimized for speed
- **Intelligent Rate Limiting**: Respects API limits
- **Error Resilience**: Individual agent failures don't stop the pipeline

#### **2.2 Data Sources**

**BOE (Spanish Official Gazette)**

- **Agent**: `StreamlinedBOEAgent`
- **Source**: Spanish government official publications
- **Data**: Legal notices, sanctions, regulatory actions
- **API**: BOE Public API
- **Processing**: Full text extraction and metadata parsing

**NewsAPI (International News)**

- **Agent**: `StreamlinedNewsAPIAgent`
- **Source**: Global news articles
- **Data**: Company mentions, financial news, legal developments
- **API**: NewsAPI.org
- **Limits**: 30-day historical data, rate-limited

**RSS Feeds (Spanish News Sources)**

- **El País**: `StreamlinedElPaisAgent`
- **Expansión**: `StreamlinedExpansionAgent`
- **El Mundo**: `StreamlinedElMundoAgent`
- **ABC**: `StreamlinedABCAgent`
- **La Vanguardia**: `StreamlinedLaVanguardiaAgent`
- **El Confidencial**: `StreamlinedElConfidencialAgent`
- **El Diario**: `StreamlinedElDiarioAgent`
- **Europa Press**: `StreamlinedEuropaPressAgent`

**Yahoo Finance**

- **Agent**: `StreamlinedYahooFinanceAgent`
- **Data**: Financial metrics, stock information
- **Processing**: Financial data extraction and normalization

### **Phase 3: Data Processing & Classification**

#### **3.1 Optimized Hybrid Classifier**

```python
# File: app/agents/analysis/optimized_hybrid_classifier.py
class OptimizedHybridClassifier:
    """Ultra-fast keyword gate with smart LLM routing"""

    def __init__(self):
        # Pre-compiled regex patterns for maximum speed
        self._compile_patterns()
        self.stats = {
            "keyword_hits": 0,
            "llm_calls": 0,
            "total_classifications": 0
        }
```

**Classification Strategy:**

1. **Stage 1: Keyword Gate (µ-seconds)**

   - Pre-compiled regex patterns
   - 90%+ classification accuracy
   - Immediate classification for clear cases

2. **Stage 2: Smart LLM Routing**
   - Only for ambiguous cases
   - Cloud-based AI classification
   - Fallback for complex analysis

**Risk Levels:**

- **High-Legal**: Bankruptcy, criminal sanctions, severe penalties
- **Medium-Legal**: Regulatory warnings, administrative proceedings
- **Low-Legal**: Regulatory notices, administrative procedures
- **No-Legal**: Regular business news, non-legal content

#### **3.2 Document Processing Pipeline**

```python
# File: app/agents/analysis/processor.py
class BOEDocumentProcessor:
    """Normalizes raw BOE documents into canonical events"""

    def process_unparsed_documents(self, batch_size: int = 50):
        # Process raw documents in batches
        # Create normalized events
        # Update processing status
```

**Processing Steps:**

1. **Raw Document Parsing**: Extract structured data from raw payloads
2. **Event Normalization**: Create standardized event records
3. **Metadata Enrichment**: Add classification results and confidence scores
4. **Database Persistence**: Save processed events

### **Phase 4: Database Integration**

#### **4.1 Database Integration Service**

```python
# File: app/services/database_integration.py
class DatabaseIntegrationService:
    """Service to integrate search results with database persistence"""

    def save_search_results(self, db, search_results, query, company_name):
        # Process BOE results
        # Process NewsAPI results
        # Process RSS results
        # Process Yahoo Finance results
        # Return save statistics
```

**Database Operations:**

- **Raw Documents**: Store original data from all sources
- **Events**: Create normalized event records
- **Companies**: Track company information and analysis history
- **Assessments**: Store risk assessment results

#### **4.2 Data Models**

**Raw Documents (`raw_docs`)**

- Source identification
- Original payload storage
- Processing status tracking
- Metadata storage

**Events (`events`)**

- Normalized event records
- Risk classification results
- Company associations
- Temporal data

**Companies (`companies`)**

- Company information
- Analysis history
- Risk assessment summaries

### **Phase 5: Analytics & Business Intelligence**

#### **5.1 Analytics Service**

```python
# File: app/agents/analytics/analytics_service.py
class AnalyticsService:
    """Orchestrates analytics operations for the BHSI system"""

    async def get_comprehensive_analytics(self, company_name, include_trends=True):
        # Company-specific analytics
        # Risk trends analysis
        # Sector comparison
        # Performance metrics
```

**Analytics Features:**

- **Company Analytics**: Risk profile analysis
- **Trend Analysis**: Temporal risk patterns
- **Sector Comparison**: Industry benchmarking
- **Performance Monitoring**: System optimization metrics

#### **5.2 BigQuery Integration**

```python
# File: app/agents/analytics/bigquery_client.py
class BigQueryClient:
    """BigQuery analytics client for advanced data analysis"""

    async def get_company_analytics(self, company_name):
        # Query BigQuery for company data
        # Aggregate risk metrics
        # Generate insights
```

**BigQuery Capabilities:**

- **Data Warehousing**: Long-term data storage
- **Advanced Analytics**: Complex queries and aggregations
- **Machine Learning**: Predictive analytics
- **Real-time Dashboards**: Live monitoring

#### **5.3 Cache Management**

```python
# File: app/agents/analytics/cache_manager.py
class AnalyticsCache:
    """Intelligent caching for analytics results"""

    def get(self, cache_key, **kwargs):
        # Check cache for existing results
        # Return cached data if valid
        # Trigger refresh if expired
```

**Caching Strategy:**

- **Result Caching**: Store computed analytics
- **Time-based Expiration**: Automatic cache refresh
- **Key-based Invalidation**: Selective cache updates
- **Performance Optimization**: Reduce redundant computations

### **Phase 6: Cloud Services Integration**

#### **6.1 Cloud Classifier Service**

```python
# File: app/agents/analysis/cloud_classifier.py
class CloudClassifier:
    """Cloud-based AI classification service"""

    async def classify_document(self, text, title, source, section):
        # Send document to cloud AI service
        # Receive classification results
        # Return structured response
```

**Cloud AI Features:**

- **Advanced NLP**: Deep learning-based text analysis
- **Context Understanding**: Semantic analysis of legal documents
- **Multi-language Support**: Spanish and English processing
- **Scalable Processing**: Handle high-volume requests

#### **6.2 Vector Search Service**

```python
# File: app/services/vector_search/main.py
# Cloud-based vector similarity search
# Semantic document matching
# Advanced retrieval capabilities
```

**Vector Search Capabilities:**

- **Semantic Search**: Find similar documents
- **Embedding Storage**: Vector database integration
- **Similarity Scoring**: Relevance ranking
- **Scalable Architecture**: Cloud-native deployment

#### **6.3 Embedder Service**

```python
# File: app/services/embedder/main.py
# Document embedding generation
# Vector representation creation
# Model management and optimization
```

**Embedding Features:**

- **Text Embeddings**: Convert documents to vectors
- **Model Management**: Multiple embedding models
- **Batch Processing**: Efficient bulk operations
- **Quality Optimization**: Continuous model improvement

### **Phase 7: Response Generation**

#### **7.1 Structured Response Format**

```json
{
  "company_name": "Example Corp",
  "risk_assessment": {
    "overall_risk": "red",
    "high_risk_count": 3,
    "medium_risk_count": 5,
    "total_results": 25
  },
  "classified_results": [
    {
      "source": "BOE",
      "date": "2024-01-15",
      "title": "Sanción administrativa",
      "risk_level": "High-Legal",
      "confidence": 0.95,
      "method": "keyword_gate"
    }
  ],
  "analytics": {
    "trends": {...},
    "sectors": {...},
    "performance": {...}
  },
  "processing_stats": {
    "search_time_ms": 2500,
    "classification_time_ms": 1500,
    "total_time_ms": 4000
  }
}
```

#### **7.2 Performance Monitoring**

- **Response Time Tracking**: End-to-end performance measurement
- **Classification Statistics**: Success rates and method distribution
- **Error Monitoring**: Failure tracking and alerting
- **Resource Utilization**: System resource monitoring

## 🚀 **Performance Optimizations**

### **1. Streamlined Search Architecture**

- **No Classification During Search**: Separate data collection from analysis
- **Parallel Processing**: Multiple agents run concurrently
- **Intelligent Caching**: Reduce redundant API calls
- **Rate Limit Management**: Respect external API limits

### **2. Optimized Classification Pipeline**

- **Keyword Gate**: 90%+ classification in microseconds
- **Smart LLM Routing**: Only use AI for ambiguous cases
- **Batch Processing**: Efficient bulk operations
- **Result Caching**: Store classification results

### **3. Database Optimization**

- **Connection Pooling**: Efficient database connections
- **Batch Operations**: Bulk insert/update operations
- **Indexing Strategy**: Optimized query performance
- **Data Deduplication**: Prevent duplicate records

### **4. Cloud Service Integration**

- **Async Processing**: Non-blocking external calls
- **Fallback Mechanisms**: Graceful degradation
- **Load Balancing**: Distribute processing load
- **Auto-scaling**: Dynamic resource allocation

## 🔧 **Configuration & Deployment**

### **Environment Variables**

```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/bhsi_db

# API Keys
NEWSAPI_API_KEY=your_newsapi_key
BOE_API_KEY=your_boe_key

# Cloud Services
GEMINI_API_KEY=your_gemini_key
BIGQUERY_PROJECT_ID=your_project_id

# Performance Settings
MAX_CONCURRENT_SEARCHES=10
CLASSIFICATION_BATCH_SIZE=50
CACHE_TTL_SECONDS=3600
```

### **Service Deployment**

```bash
# Backend API
cd bhsi-backend
python main.py

# Cloud Services (Docker)
docker-compose up -d gemini-service
docker-compose up -d vector-search-service
docker-compose up -d embedder-service
```

## 📈 **Monitoring & Observability**

### **Key Metrics**

- **Response Time**: End-to-end processing time
- **Classification Accuracy**: Success rates by method
- **API Success Rates**: External service reliability
- **Database Performance**: Query execution times
- **Resource Utilization**: CPU, memory, network usage

### **Logging Strategy**

- **Structured Logging**: JSON-formatted log entries
- **Performance Tracking**: Detailed timing information
- **Error Tracking**: Comprehensive error reporting
- **Audit Trail**: Complete request/response logging

## 🔒 **Security & Compliance**

### **Data Protection**

- **Encryption**: Data encryption in transit and at rest
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete access tracking
- **Data Retention**: Configurable retention policies

### **API Security**

- **Authentication**: JWT-based authentication
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error responses

## 🚀 **Future Enhancements**

### **Planned Improvements**

- **Real-time Processing**: Stream processing capabilities
- **Advanced ML Models**: Improved classification accuracy
- **Multi-language Support**: Additional language processing
- **Mobile API**: Optimized mobile endpoints
- **GraphQL Integration**: Flexible query interface

### **Scalability Roadmap**

- **Microservices Architecture**: Service decomposition
- **Event-driven Processing**: Asynchronous workflows
- **Global Distribution**: Multi-region deployment
- **Advanced Analytics**: Predictive modeling

---

## 📚 **Additional Resources**

- **API Documentation**: `/docs` endpoint for interactive API docs
- **Architecture Diagrams**: See `DATAFLOW_ARCHITECTURE.md`
- **Deployment Guide**: See `CLOUD_ARCHITECTURE_GUIDE.md`
- **Testing Guide**: See `tests/README.md`
- **Performance Benchmarks**: See `TEST_ORGANIZATION_SUMMARY.md`

This comprehensive dataflow pipeline provides a robust, scalable, and efficient system for corporate risk assessment, combining real-time data collection with advanced AI-powered analysis and business intelligence.
