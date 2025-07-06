# Risk Assessment System Documentation

## Overview

This document provides a comprehensive overview of the Risk Assessment Search system, RSS feeds filtering, Management Summary generation, and all related components. It details file relationships, data flow, and integration points to help team members understand the system architecture and facilitate integration into different branches.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Risk Assessment Search](#risk-assessment-search)
3. [RSS Feeds Integration](#rss-feeds-integration)
4. [Management Summary System](#management-summary-system)
5. [Frontend Components](#frontend-components)
6. [API Endpoints](#api-endpoints)
7. [Data Flow](#data-flow)
8. [Integration Points](#integration-points)
9. [Configuration](#configuration)

---

## System Architecture

### High-Level Flow

```
Frontend (React/TypeScript)
    ↓ HTTP Requests
Backend API (FastAPI/Python)
    ↓ Orchestration
Search Orchestrator
    ↓ Parallel Execution
Multiple Search Agents (BOE, NewsAPI, RSS Feeds)
    ↓ Classification
Risk Classifier
    ↓ Analysis
Management Summarizer
    ↓ Response
Frontend Display Components
```

### Core Components

- **Frontend**: React with TypeScript, Material-UI, Redux Toolkit
- **Backend**: FastAPI with Python, async/await patterns
- **Search**: Multi-source orchestration (BOE, NewsAPI, RSS feeds)
- **Analysis**: AI-powered risk classification and summarization
- **Storage**: BigQuery, SQLite, in-memory caching

---

## Risk Assessment Search

### Backend Components

#### 1. Search Orchestrator

**File**: `bhsi-backend/app/agents/search/streamlined_orchestrator.py`

**Purpose**: Coordinates multiple search agents for comprehensive data collection

**Key Methods**:

- `search_all()`: Main orchestration method
- `__init__()`: Initializes all search agents

**Dependencies**:

```python
# Search Agents
- StreamlinedBOEAgent
- StreamlinedNewsAPIAgent
- StreamlinedElPaisAgent
- StreamlinedExpansionAgent
- StreamlinedElMundoAgent
- StreamlinedABCAgent
- StreamlinedLaVanguardiaAgent
- StreamlinedElConfidencialAgent
- StreamlinedElDiarioAgent
- StreamlinedEuropaPressAgent
- StreamlinedYahooFinanceAgent
```

**Configuration**:

```python
self.agents = {
    "boe": StreamlinedBOEAgent(),
    "newsapi": StreamlinedNewsAPIAgent(),
    "elpais": StreamlinedElPaisAgent(),
    # ... other agents
}
```

#### 2. API Endpoints

**File**: `bhsi-backend/app/api/v1/endpoints/search.py`

**Main Endpoint**: `POST /api/v1/streamlined/search`

**Request Model**:

```python
class SearchRequest(BaseModel):
    company_name: str
    start_date?: str
    end_date?: str
    days_back?: int = 7
    include_boe?: bool = True
    include_news?: bool = True
    include_rss?: bool = True
    rss_feeds?: List[str]
```

**Response Model**:

```python
{
    "company_name": str,
    "search_date": str,
    "date_range": {...},
    "results": List[SearchResult],
    "metadata": {...},
    "performance": {...}
}
```

#### 3. Risk Classification

**File**: `bhsi-backend/app/agents/analysis/optimized_hybrid_classifier.py`

**Purpose**: Classifies search results by risk level

**Classification Levels**:

- `High-Legal`, `High-Financial`, `High-Regulatory`, `High-Operational`
- `Medium-Legal`, `Medium-Financial`, `Medium-Regulatory`, `Medium-Operational`
- `Low-Legal`, `Low-Financial`, `Low-Regulatory`, `Low-Operational`

---

## RSS Feeds Integration

### RSS Agent Architecture

#### 1. Base Agent

**File**: `bhsi-backend/app/agents/search/base_agent.py`

**Purpose**: Abstract base class for all search agents

**Key Methods**:

- `search()`: Abstract method for search implementation
- `_parse_date()`: Date parsing utilities
- `_extract_content()`: Content extraction helpers

#### 2. Individual RSS Agents

##### El País Agent

**File**: `bhsi-backend/app/agents/search/streamlined_elpais_agent.py`

**Feeds**:

```python
self.feeds = [
    {"category": "portada", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"},
    {"category": "economia", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada"},
    {"category": "negocios", "url": "https://feeds.elpais.com/mrss-s/list/ep/site/elpais.com/section/economia/subsection/negocios"},
    {"category": "tecnologia", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada"},
    {"category": "clima", "url": "https://feeds.elpais.com/mrss-s/list/ep/site/elpais.com/section/clima-y-medio-ambiente"}
]
```

##### Expansión Agent

**File**: `bhsi-backend/app/agents/search/streamlined_expansion_agent.py`

**Feeds**:

```python
self.feeds = [
    # Empresas
    {"category": "empresas-nombramientos", "url": "https://e00-expansion.uecdn.es/rss/empresas/nombramientos.xml"},
    {"category": "empresas-distribucion", "url": "https://e00-expansion.uecdn.es/rss/empresas/distribucion.xml"},
    {"category": "empresas-banca", "url": "https://e00-expansion.uecdn.es/rss/empresasbanca.xml"},
    # Economía
    {"category": "economia-politica", "url": "https://e00-expansion.uecdn.es/rss/economia/politica.xml"},
    # Jurídico
    {"category": "juridico-sentencias", "url": "https://e00-expansion.uecdn.es/rss/juridicosentencias.xml"},
    # ... more feeds
]
```

##### Other RSS Agents

- **El Mundo**: `streamlined_elmundo_agent.py`
- **ABC**: `streamlined_abc_agent.py`
- **La Vanguardia**: `streamlined_lavanguardia_agent.py`
- **El Confidencial**: `streamlined_elconfidencial_agent.py`
- **El Diario**: `streamlined_eldiario_agent.py`
- **Europa Press**: `streamlined_europapress_agent.py`

#### 3. RSS Feed Selection (Frontend)

**File**: `bhsi-frontend/src/components/TrafficLightQuery.tsx`

**Configuration**:

```typescript
const RSS_FEEDS = [
  { value: "elpais", label: "El País" },
  { value: "expansion", label: "Expansión" },
  { value: "elmundo", label: "El Mundo" },
  { value: "abc", label: "ABC" },
  { value: "lavanguardia", label: "La Vanguardia" },
  { value: "elconfidencial", label: "El Confidencial" },
  { value: "eldiario", label: "El Diario" },
  { value: "europapress", label: "Europa Press" },
];
```

**State Management**:

```typescript
const [selectedRssFeeds, setSelectedRssFeeds] = useState<string[]>(
  RSS_FEEDS.map((f) => f.value)
);
```

---

## Management Summary System

### Backend Components

#### 1. Management Summarizer

**File**: `bhsi-backend/app/agents/analysis/management_summarizer.py`

**Purpose**: Generates executive-level risk analysis summaries

**Key Methods**:

- `generate_summary()`: Main summary generation method
- `_cloud_gemini_summary()`: AI-powered summary using Gemini
- `_template_summary()`: Fallback template-based summary
- `_build_risk_breakdown()`: Risk categorization
- `_get_financial_health()`: Financial data integration

**API Endpoint**: `POST /api/v1/analysis/management-summary`

**Request Model**:

```python
class ManagementSummaryRequest(BaseModel):
    company_name: str
    classification_results: List[Dict[str, Any]]
    include_evidence: bool = True
    language: str = "es"
```

**Response Model**:

```python
{
    "company_name": str,
    "overall_risk": str,
    "executive_summary": str,
    "risk_breakdown": Dict[str, RiskBreakdown],
    "key_findings": List[str],
    "recommendations": List[str],
    "financial_health": FinancialHealth,
    "compliance_status": ComplianceStatus,
    "key_risks": List[KeyRisk],
    "generated_at": str,
    "method": str
}
```

#### 2. Risk Breakdown Categories

```python
risk_breakdown = {
    "legal": {"level": "red/orange/green", "reasoning": str, "evidence": List[str], "confidence": float},
    "financial": {...},
    "regulatory": {...},
    "operational": {...},
    "shareholding": {...},
    "dismissals": {...},
    "environmental": {...}
}
```

#### 3. Financial Health Integration

**File**: `bhsi-backend/app/agents/search/streamlined_yahoo_finance_agent.py`

**Purpose**: Provides financial metrics for risk assessment

**Data Points**:

- Price changes (7-day, 30-day)
- Revenue changes (YoY)
- Risk indicators
- Market performance metrics

---

## Frontend Components

### 1. Main Search Interface

**File**: `bhsi-frontend/src/components/TrafficLightQuery.tsx`

**Purpose**: Primary search interface with data source selection

**Key Features**:

- Company name/VAT input
- Data source selection (BOE, NewsAPI, RSS)
- RSS feed selection with checkboxes
- Date range configuration
- Search execution

**State Management**:

```typescript
const [query, setQuery] = useState("");
const [boeEnabled, setBoeEnabled] = useState(true);
const [newsEnabled, setNewsEnabled] = useState(true);
const [rssEnabled, setRssEnabled] = useState(true);
const [selectedRssFeeds, setSelectedRssFeeds] = useState<string[]>([]);
const [dateRangeType, setDateRangeType] = useState<"preset" | "custom">(
  "preset"
);
```

### 2. Results Display

**File**: `bhsi-frontend/src/components/TrafficLightResult.tsx`

**Purpose**: Displays search results and risk assessment

**Key Sections**:

- Overall risk indicator (traffic light)
- Parameter breakdown table
- Search results summary
- Management summary integration
- Detailed results dialog

**Management Summary Integration**:

```typescript
const [getManagementSummary, { data: summary, isLoading: summaryLoading }] =
  useGetManagementSummaryMutation();

// Trigger management summary generation
await getManagementSummary({
  company_name: result.company,
  classification_results: searchResults,
  language: "es",
});
```

### 3. Management Summary Components

#### Summary Header

**File**: `bhsi-frontend/src/components/ManagementSummary/SummaryHeader.tsx`

**Purpose**: Displays company info, overall risk, and language toggle

#### Risk Breakdown Grid

**File**: `bhsi-frontend/src/components/ManagementSummary/RiskBreakdownGrid.tsx`

**Purpose**: Visual grid of risk categories with confidence indicators

#### Financial Health Panel

**File**: `bhsi-frontend/src/components/ManagementSummary/FinancialHealthPanel.tsx`

**Purpose**: Displays financial indicators and health status

#### Key Findings List

**File**: `bhsi-frontend/src/components/ManagementSummary/KeyFindingsList.tsx`

**Purpose**: Lists key risk findings from analysis

#### Recommendations Checklist

**File**: `bhsi-frontend/src/components/ManagementSummary/RecommendationsChecklist.tsx`

**Purpose**: Displays actionable recommendations

#### Key Risks Panel

**File**: `bhsi-frontend/src/components/ManagementSummary/KeyRisksPanel.tsx`

**Purpose**: Shows detailed risk items with severity levels

#### Compliance Status Panel

**File**: `bhsi-frontend/src/components/ManagementSummary/ComplianceStatusPanel.tsx`

**Purpose**: Displays regulatory compliance status

### 4. State Management

**File**: `bhsi-frontend/src/store/api/analyticsApi.ts`

**Management Summary Hook**:

```typescript
export const useGetManagementSummaryMutation =
  analyticsApi.useGetManagementSummaryMutation;
```

**Request/Response Types**:

```typescript
interface ManagementSummaryRequest {
  company_name: string;
  classification_results?: any[];
  language?: string;
}

interface ManagementSummaryResponse {
  company_name: string;
  overall_risk: string;
  executive_summary: string;
  risk_breakdown: Record<string, RiskBreakdown>;
  key_findings: string[];
  recommendations: string[];
  // ... other fields
}
```

---

## API Endpoints

### 1. Search Endpoints

```
POST /api/v1/streamlined/search
POST /api/v1/search
POST /api/v1/companies/analyze
POST /api/v1/companies/unified-analysis
```

### 2. Analysis Endpoints

```
POST /api/v1/analysis/management-summary
GET /api/v1/analysis/summary-templates
```

### 3. Analytics Endpoints

```
GET /api/v1/companies/analytics/trends
GET /api/v1/companies/analytics/comparison
GET /api/v1/companies/analytics/health
```

### 4. BigQuery Assessment

```
POST /api/v1/bigquery/assess
GET /api/v1/bigquery/status
```

---

## Data Flow

### 1. Search Flow

```
User Input → TrafficLightQuery → API Request → StreamlinedSearchOrchestrator
    ↓
Parallel Agent Execution (BOE, NewsAPI, RSS Feeds)
    ↓
Result Aggregation → Risk Classification → Response
    ↓
TrafficLightResult → Management Summary Generation
```

### 2. RSS Feed Flow

```
RSS Agent Selection → Feed URL Fetching → Content Parsing
    ↓
Query Matching → Result Filtering → Classification
    ↓
Response Assembly → Frontend Display
```

### 3. Management Summary Flow

```
Classification Results → ManagementSummarizer → Gemini AI Analysis
    ↓
Risk Breakdown → Financial Health → Compliance Status
    ↓
Template Fallback (if AI fails) → Response Assembly
    ↓
Frontend Component Rendering
```

---

## Integration Points

### 1. Backend Integration

- **Search Orchestrator**: Central coordination point
- **Risk Classifier**: Post-search analysis
- **Management Summarizer**: Executive summary generation
- **Cache Manager**: Performance optimization
- **BigQuery Integration**: Data persistence

### 2. Frontend Integration

- **Redux Store**: State management
- **RTK Query**: API communication
- **Material-UI**: Component library
- **React Router**: Navigation
- **Context API**: Company management

### 3. External Services

- **Gemini AI**: Summary generation
- **Yahoo Finance**: Financial data
- **NewsAPI**: International news
- **BOE**: Spanish government publications
- **RSS Feeds**: Spanish news sources

---

## Configuration

### 1. Environment Variables

```bash
# Backend
VITE_API_BASE_URL=http://localhost:8000
USE_MOCK_ORCHESTRATOR=false
GEMINI_SERVICE_URL=https://gemini-service-185303190462.europe-west1.run.app

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

### 2. RSS Feed Configuration

```typescript
// Frontend RSS feed selection
const RSS_FEEDS = [
  { value: "elpais", label: "El País" },
  { value: "expansion", label: "Expansión" },
  // ... other feeds
];

// Backend agent mapping
self.agents = {
  elpais: StreamlinedElPaisAgent(),
  expansion: StreamlinedExpansionAgent(),
  // ... other agents
};
```

### 3. Risk Classification Configuration

```python
# Risk level mappings
risk_colors = {
    "High-Legal": "red",
    "Medium-Legal": "orange",
    "Low-Legal": "green",
    "No-Legal": "green"
}

# Category keywords
category_keywords = {
    "legal": ["sanción", "sentencia", "procedimiento", "tribunal", "delito"],
    "financial": ["concurso", "insolvencia", "pérdidas", "facturación", "deuda"],
    "regulatory": ["cnmv", "banco de españa", "cnmc", "aepd", "dgsfp", "sepblac"],
    # ... other categories
}
```

---

## Migration and Integration Guide

### 1. Adding New RSS Feeds

1. Create new agent file: `streamlined_[feedname]_agent.py`
2. Extend `BaseSearchAgent` class
3. Define feeds array with URLs
4. Add to orchestrator agents dictionary
5. Update frontend RSS_FEEDS array
6. Test integration

### 2. Modifying Risk Categories

1. Update `category_keywords` in management summarizer
2. Modify risk breakdown logic
3. Update frontend risk breakdown components
4. Test classification accuracy

### 3. Adding New Analysis Features

1. Extend `ManagementSummarizer` class
2. Add new API endpoints
3. Create frontend components
4. Update Redux store types
5. Test end-to-end flow

### 4. Performance Optimization

1. Implement caching strategies
2. Optimize database queries
3. Use background processing for heavy operations
4. Monitor API response times
5. Implement error handling and fallbacks

---

## Error Handling and Fallbacks

### 1. Search Failures

- Individual agent failures don't stop entire search
- Fallback to mock data if all agents fail
- Graceful degradation with partial results

### 2. AI Service Failures

- Template-based fallback for management summaries
- Cached results for repeated requests
- Error logging and monitoring

### 3. Frontend Error Handling

- Loading states for all async operations
- Error boundaries for component failures
- User-friendly error messages

---

## Testing Strategy

### 1. Unit Tests

- Individual agent functionality
- Risk classification accuracy
- API endpoint validation

### 2. Integration Tests

- End-to-end search flow
- Management summary generation
- Frontend-backend communication

### 3. Performance Tests

- Search response times
- RSS feed availability
- AI service reliability

---

## Monitoring and Logging

### 1. Backend Logging

```python
logger.info(f"📰 RSS search: '{query}'")
logger.error(f"❌ {agent_name} search failed: {e}")
logger.debug(f"✅ {agent_name}: {result_count} results")
```

### 2. Frontend Logging

```typescript
console.log("Search results:", result);
console.error("Search failed:", error);
```

### 3. Performance Metrics

- Search response times
- Classification accuracy
- AI service availability
- RSS feed success rates

---

This documentation provides a comprehensive overview of the Risk Assessment System architecture, components, and integration points. Use this as a reference for understanding the system and facilitating integration into different branches.
