# BHSI Corporate Risk Assessment System

## Executive Summary

The BHSI (Banking, Healthcare, and Strategic Investments) Corporate Risk Assessment System is a comprehensive enterprise-grade platform designed for automated assessment of Directors and Officers (D&O) liability risks across Spanish corporations. The system leverages advanced AI technologies, cloud-native microservices architecture, and multi-source data integration to provide real-time risk intelligence for insurance underwriting and corporate governance decisions.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Core Services](#core-services)
4. [Data Sources and Integration](#data-sources-and-integration)
5. [Risk Classification Engine](#risk-classification-engine)
6. [Cloud Infrastructure](#cloud-infrastructure)
7. [API Documentation](#api-documentation)
8. [Installation and Setup](#installation-and-setup)
9. [Usage Examples](#usage-examples)
10. [Data Flow Architecture](#data-flow-architecture)
11. [Performance Optimization](#performance-optimization)
12. [Security and Compliance](#security-and-compliance)
13. [Monitoring and Analytics](#monitoring-and-analytics)
14. [Development Guidelines](#development-guidelines)
15. [Troubleshooting](#troubleshooting)

## System Architecture

### Overview

The BHSI system implements a hybrid cloud-native architecture combining microservices, AI-powered analysis, and real-time data processing. The architecture is designed for scalability, reliability, and regulatory compliance in the financial services sector.

### Architectural Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │ Authentication  │
│   React/TypeScript│ ──▶│   FastAPI      │◄──▶│    Service      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Search          │    │ Classification  │    │   Analytics     │
│ Orchestrator    │◄──▶│    Engine       │◄──▶│    Service      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Sources   │    │ Cloud Services  │    │   BigQuery      │
│ BOE/News/RSS    │    │ Gemini/Vector   │    │   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Design Principles

- **Microservices Architecture**: Modular, independently deployable services
- **Event-Driven Processing**: Asynchronous data processing and real-time updates
- **Cloud-Native Design**: Leveraging Google Cloud Platform services
- **Hybrid AI Integration**: Combining rule-based and machine learning approaches
- **Enterprise Security**: Role-based access control and data encryption
- **Scalable Data Pipeline**: Handling high-volume document processing

## Technology Stack

### Backend Technologies

**Core Framework**
- **FastAPI**: Modern, high-performance web framework for Python APIs
- **Python 3.11+**: Primary programming language with async/await support
- **Pydantic**: Data validation and serialization using Python type hints
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **Alembic**: Database migration tool for SQLAlchemy

**AI and Machine Learning**
- **Google Gemini Pro 1.5**: Large Language Model for document classification
- **Sentence Transformers**: Text embedding generation for semantic search
- **scikit-learn**: Machine learning utilities and performance metrics
- **NLTK**: Natural language processing toolkit for text preprocessing

**Data Processing**
- **Pandas**: Data manipulation and analysis library
- **NumPy**: Numerical computing and array operations
- **aiohttp**: Asynchronous HTTP client/server for Python
- **httpx**: Modern async HTTP client for API integrations

**Cloud and Infrastructure**
- **Google Cloud Platform**: Primary cloud infrastructure provider
- **BigQuery**: Enterprise data warehouse for analytics and storage
- **Cloud Run**: Serverless container platform for microservices
- **Vertex AI**: Machine learning platform for model deployment

### Frontend Technologies

**Core Framework**
- **React 18**: JavaScript library for building user interfaces
- **TypeScript**: Typed superset of JavaScript for enhanced development
- **Vite**: Next-generation frontend build tool
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development

**State Management and Routing**
- **Redux Toolkit**: State management with query caching capabilities
- **React Router**: Declarative routing for React applications
- **React Hook Form**: Performant forms with minimal re-renders

**UI Components and Visualization**
- **Recharts**: Composable charting library for React
- **Lucide React**: Beautiful and customizable icon library
- **Radix UI**: Low-level UI primitives for accessible components

### Database Technologies

**Primary Database**
- **PostgreSQL**: Advanced open-source relational database
- **BigQuery**: Google Cloud's serverless data warehouse
- **ChromaDB**: Vector database for semantic search capabilities

**Caching and Performance**
- **Redis**: In-memory data structure store for caching
- **Application-level caching**: Multi-layer caching strategy

## Core Services

### 1. Search Orchestrator Service

The Search Orchestrator coordinates data retrieval across multiple information sources, implementing intelligent routing and load balancing.

**Key Features:**
- Multi-source search coordination (BOE, NewsAPI, RSS feeds)
- Intelligent query optimization and routing
- Rate limiting and API quota management
- Result aggregation and deduplication
- Performance monitoring and metrics collection

**Implementation:**
- **File**: `app/agents/search/streamlined_orchestrator.py`
- **Agents**: BOE, NewsAPI, RSS (El País, Expansión, ABC, La Vanguardia)
- **Caching**: Multi-level caching with TTL-based invalidation

### 2. Risk Classification Engine

Advanced hybrid classification system combining rule-based filtering with AI-powered analysis for optimal performance and accuracy.

**Classification Pipeline:**
1. **Keyword Gate Filter** (90%+ efficiency): Ultra-fast pattern matching
2. **Section Code Analysis**: Regulatory section-based risk assessment
3. **LLM Classification**: Gemini Pro analysis for ambiguous cases
4. **Confidence Scoring**: Multi-factor confidence calculation

**Performance Metrics:**
- Average processing time: <200ms per document
- Classification accuracy: >92% for legal risk detection
- Cost optimization: 90% reduction in LLM API calls

### 3. Analytics and Reporting Service

Comprehensive analytics platform providing business intelligence and risk insights.

**Capabilities:**
- Real-time risk trend analysis
- Company comparison and benchmarking
- Sector-wide risk assessment
- Regulatory compliance monitoring
- Executive dashboard generation

### 4. Vector Search and RAG Service

Retrieval-Augmented Generation (RAG) system enabling natural language queries over corporate risk data.

**Architecture:**
- **Vector Storage**: BigQuery-based vector database
- **Embedding Model**: Google Text Embedding 004
- **Search Algorithm**: Cosine similarity with metadata filtering
- **Response Generation**: Gemini Pro with context augmentation

## Data Sources and Integration

### Official Government Sources

**BOE (Boletín Oficial del Estado)**
- **Description**: Spanish official state gazette
- **Content**: Legal proceedings, regulatory changes, sanctions
- **Integration**: RESTful API with date-range queries
- **Update Frequency**: Daily publication monitoring
- **Data Volume**: ~1,000-5,000 documents per day

### News and Media Sources

**NewsAPI Integration**
- **Coverage**: International and Spanish financial news
- **Sources**: Reuters, Bloomberg, Financial Times, Expansión
- **Filtering**: Company-specific keyword matching
- **Language**: Spanish and English content processing

**RSS Feed Aggregation**
- **El País**: Leading Spanish newspaper
- **Expansión**: Financial and business news
- **ABC**: Conservative Spanish daily
- **La Vanguardia**: Catalan-based national newspaper
- **Europa Press**: Spanish news agency

### Financial Data Integration

**Yahoo Finance API**
- **Stock Data**: Real-time and historical pricing
- **Company Fundamentals**: Financial ratios and metrics
- **Market Analytics**: Risk indicators and volatility measures
- **Ticker Resolution**: Advanced company name to ticker mapping

## Risk Classification Engine

### Methodology

The risk classification system implements a sophisticated multi-stage approach designed for accuracy, performance, and cost efficiency.

### Stage 1: Keyword Gate Filter

**Purpose**: Eliminate 90%+ of documents without LLM processing
**Processing Time**: <1ms per document
**Accuracy**: >95% for clear-cut cases

**Pattern Categories:**
- **High-Legal**: Criminal proceedings, bankruptcy, severe sanctions
- **Medium-Legal**: Administrative procedures, compliance issues
- **Low-Legal**: Regulatory notices, authorizations
- **No-Legal**: Business news, sports, entertainment

### Stage 2: Section Code Analysis

**BOE Section Mapping:**
- **JUS (Justice)**: Legal proceedings and court decisions
- **CNMC**: Competition authority decisions
- **AEPD**: Data protection authority actions
- **CNMV**: Securities market regulator notices
- **BDE**: Central bank communications

### Stage 3: LLM Classification

**Model**: Google Gemini Pro 1.5
**Trigger Conditions**: Ambiguous documents passing keyword gate
**Processing**: Contextual analysis with domain-specific prompts
**Output**: Risk level with confidence score and reasoning

### Performance Optimization

**Caching Strategy:**
- **L1 Cache**: In-memory classification results (1 hour TTL)
- **L2 Cache**: Database-backed results (24 hour TTL)
- **L3 Cache**: Cloud-based persistent storage

**Cost Optimization:**
- 90% reduction in LLM API calls through keyword filtering
- Intelligent batching of cloud service requests
- Adaptive rate limiting based on API quotas

## Cloud Infrastructure

### Google Cloud Platform Services

**Compute Services**
- **Cloud Run**: Serverless containers for microservices
- **Compute Engine**: Virtual machines for persistent workloads
- **Cloud Functions**: Event-driven serverless functions

**Data Services**
- **BigQuery**: Data warehouse for analytics and vector storage
- **Cloud Storage**: Object storage for documents and artifacts
- **Cloud SQL**: Managed PostgreSQL for transactional data

**AI/ML Services**
- **Vertex AI**: Machine learning platform and model hosting
- **Cloud Natural Language**: Text analysis and entity extraction
- **Document AI**: Automated document processing

### Microservices Deployment

**Service URLs:**
- Gemini Service: `https://gemini-service-185303190462.europe-west1.run.app`
- Embedder Service: `https://embedder-service-185303190462.europe-west1.run.app`
- Vector Search: `https://vector-search-185303190462.europe-west1.run.app`
- BigQuery Analytics: `https://bigquery-analytics-185303190462.europe-west1.run.app`

**Configuration:**
- **Region**: europe-west1 (Belgium) for GDPR compliance
- **Scaling**: Automatic scaling based on request volume
- **Health Monitoring**: Continuous health checks and alerting

## API Documentation

### Authentication Endpoints

**POST /api/v1/auth/login**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_info": {
    "email": "user@example.com",
    "user_type": "analyst"
  }
}
```

### Search Endpoints

**POST /api/v1/streamlined/search**
```json
{
  "company_name": "Banco Santander",
  "days_back": 30,
  "include_boe": true,
  "include_news": true,
  "include_rss": false,
  "force_refresh": false
}
```

**Response Structure:**
```json
{
  "results": [
    {
      "source": "BOE",
      "title": "Document title",
      "risk_level": "High-Legal",
      "confidence": 0.92,
      "date": "2024-01-15",
      "url": "https://boe.es/...",
      "summary": "Document summary..."
    }
  ],
  "metadata": {
    "total_results": 25,
    "processing_time": 4.2,
    "cache_status": "fresh"
  }
}
```

### Analysis Endpoints

**POST /api/v1/companies/analyze**
```json
{
  "name": "Company Name",
  "vat": "A12345678",
  "sector": "Banking",
  "days_back": 30
}
```

### RAG Natural Language Endpoints

**POST /api/v1/analysis/nlp/ask**
```json
{
  "question": "What are the main regulatory risks for Spanish banks?",
  "max_documents": 5,
  "language": "es"
}
```

## Installation and Setup

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- Google Cloud Platform account
- NewsAPI account (optional)

### Backend Setup

1. **Clone Repository**
```bash
git clone <repository-url>
cd bhsi-corporate-project-ie/bhsi-backend
```

2. **Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Database Setup**
```bash
alembic upgrade head
```

6. **Start Development Server**
```bash
cd bhsi-backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to Frontend Directory**
```bash
cd bhsi-frontend
```

2. **Install Dependencies**
```bash
npm install
```

3. **Start Development Server**
```bash
npm run dev
```

### Production Deployment

**Backend Deployment:**
```bash
./deploy_cloud_services.ps1
```

**Frontend Deployment:**
```bash
npm run build
# Deploy build artifacts to your hosting platform
```

## Usage Examples

### Basic Company Search

```python
import requests

# Authentication
auth_response = requests.post("http://localhost:8000/api/v1/auth/login", 
    json={"email": "admin@bhsi.com", "password": "admin123"})
token = auth_response.json()["access_token"]

# Company search
search_response = requests.post("http://localhost:8000/api/v1/streamlined/search",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "company_name": "Banco Santander",
        "days_back": 30,
        "include_boe": true,
        "include_news": true
    })

results = search_response.json()
print(f"Found {len(results['results'])} documents")
```

### RAG Natural Language Query

```python
# Natural language risk analysis
rag_response = requests.post("http://localhost:8000/api/v1/analysis/nlp/ask",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "question": "¿Cuáles son los principales riesgos regulatorios para Banco Santander?",
        "max_documents": 10,
        "language": "es"
    })

analysis = rag_response.json()
print(f"Answer: {analysis['answer']}")
print(f"Confidence: {analysis['confidence']}%")
```

## Data Flow Architecture

### Request Processing Pipeline

1. **API Gateway**: Request validation and authentication
2. **Search Orchestrator**: Multi-source data retrieval coordination
3. **Classification Engine**: Hybrid AI-powered risk analysis
4. **Analytics Service**: Business intelligence processing
5. **Response Aggregation**: Result compilation and formatting

### Data Storage Pipeline

1. **Raw Document Ingestion**: Original document storage
2. **Vector Embedding**: Semantic representation generation
3. **BigQuery Storage**: Structured data warehouse storage
4. **Cache Population**: Multi-level cache warming
5. **Analytics Processing**: Business metrics calculation

### Real-time Processing

- **Event Streaming**: Real-time document processing
- **Incremental Updates**: Delta processing for efficiency
- **Change Detection**: Automated monitoring for new content
- **Alert Generation**: Proactive risk notification system

## Performance Optimization

### Caching Strategy

**Multi-Level Caching:**
1. **Application Cache**: In-memory results (Redis)
2. **Database Cache**: Query result caching
3. **CDN Cache**: Static asset distribution
4. **API Cache**: External API response caching

### Database Optimization

**Query Optimization:**
- Indexed searches on company names and dates
- Materialized views for complex analytics
- Partitioning for large time-series data
- Connection pooling and prepared statements

### Cloud Service Optimization

**API Cost Management:**
- Intelligent batching of LLM requests
- Caching of embedding vectors
- Rate limiting and quota management
- Circuit breaker patterns for resilience

## Security and Compliance

### Data Protection

**GDPR Compliance:**
- Data minimization principles
- Right to be forgotten implementation
- Consent management systems
- Data processing transparency

**Security Measures:**
- JWT-based authentication
- Role-based access control (RBAC)
- API rate limiting and DDoS protection
- Encryption at rest and in transit

### Audit and Monitoring

**Comprehensive Logging:**
- API request/response logging
- Risk classification audit trails
- User activity monitoring
- System performance metrics

## Monitoring and Analytics

### System Metrics

**Performance Indicators:**
- Request latency and throughput
- Classification accuracy rates
- API success/failure ratios
- Resource utilization metrics

**Business Metrics:**
- Risk assessment volumes
- User engagement analytics
- Data source reliability
- Cost per analysis calculation

### Alerting System

**Automated Alerts:**
- System health monitoring
- Data quality issues
- Security incident detection
- Performance degradation warnings

## Development Guidelines

### Code Quality Standards

**Python Backend:**
- PEP 8 style compliance
- Type hints for all functions
- Comprehensive docstring documentation
- Unit test coverage >80%

**TypeScript Frontend:**
- ESLint and Prettier configuration
- Strict TypeScript compilation
- Component testing with Jest
- Accessibility compliance (WCAG 2.1)

### Git Workflow

**Branch Strategy:**
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature development
- `hotfix/*`: Critical bug fixes

### Testing Strategy

**Backend Testing:**
- Unit tests with pytest
- Integration tests for API endpoints
- Performance testing with load simulation
- Security testing with automated tools

**Frontend Testing:**
- Component unit tests
- End-to-end testing with Playwright
- Visual regression testing
- Cross-browser compatibility testing

## Troubleshooting

### Common Issues

**Authentication Problems:**
- Verify JWT token validity
- Check user permissions and roles
- Validate API endpoint accessibility

**Search Performance Issues:**
- Monitor cache hit rates
- Check external API rate limits
- Verify database query performance

**Classification Accuracy Issues:**
- Review keyword gate patterns
- Validate LLM prompt engineering
- Check training data quality

### Debugging Tools

**Logging and Monitoring:**
- Structured logging with correlation IDs
- Performance profiling tools
- Real-time monitoring dashboards
- Error tracking and alerting

### Support and Maintenance

**Regular Maintenance Tasks:**
- Database optimization and cleanup
- Cache warming and invalidation
- Security patch management
- Performance monitoring and tuning

---

## Contributing

We welcome contributions to the BHSI Corporate Risk Assessment System. Please read our contributing guidelines and submit pull requests for review.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For technical support or business inquiries, please contact the BHSI development team.
