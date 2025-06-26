# Redux Store Configuration

This directory contains the complete Redux setup for the BHSI Risk Assessment application using Redux Toolkit (RTK) and RTK Query.

## 📁 Structure

```
store/
├── store.ts              # Main store configuration
├── hooks.ts              # Typed Redux hooks
├── slices/
│   ├── authSlice.ts      # Authentication state management
│   └── uiSlice.ts        # UI state management
└── api/
    ├── axiosBaseQuery.ts # Custom base query with axios
    └── riskAssessmentApi.ts # API endpoints (matches backend spec)
```

## 🚀 Quick Start

### 1. Import hooks in components:
```typescript
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { useSearchCompanyMutation } from '../store/api/riskAssessmentApi';
```

### 2. Use the Search API (New API Specification):
```typescript
const [searchCompany, { data: results, isLoading, error }] = useSearchCompanyMutation();

// Call the API matching your backend specification
const handleSearch = async () => {
  try {
    const result = await searchCompany({
      company_name: "Banco Santander",
      start_date: "2025-06-01",
      end_date: "2025-06-13",
      include_boe: true,
      include_news: true
    }).unwrap();
    
    console.log('Search results:', result);
    // Handle result.results array
  } catch (error) {
    console.error('Search failed:', error);
  }
};
```

### 3. Access search results:
```typescript
{results && (
  <div>
    <h3>Results for {results.company_name}</h3>
    <p>Search date: {new Date(results.search_date).toLocaleString()}</p>
    <p>Date range: {results.date_range.start} to {results.date_range.end}</p>
    
    {results.results.map((item, index) => (
      <div key={index}>
        <h4>{item.title}</h4>
        <p>Source: {item.source}</p>
        <p>Risk Level: {item.risk_level}</p>
        <p>Confidence: {Math.round(item.confidence * 100)}%</p>
        <a href={item.url} target="_blank">View Source</a>
      </div>
    ))}
  </div>
)}
```

## 🎯 API Specification Compliance

### Search Request (POST /search):
```typescript
interface SearchRequest {
  company_name: string;                    // (required) The company to search for
  start_date?: string;                     // (optional, format: YYYY-MM-DD)
  end_date?: string;                       // (optional, format: YYYY-MM-DD)
  days_back?: number;                      // (optional, default: 7) If no dates, search last N days
  include_boe?: boolean;                   // (optional, default: true) Include BOE results
  include_news?: boolean;                  // (optional, default: true) Include NewsAPI results
}
```

### Search Response:
```typescript
interface SearchResponse {
  company_name: string;                    // Company name that was searched
  search_date: string;                     // ISO timestamp of the search
  date_range: {
    start: string | null;                  // Start date used for the search
    end: string | null;                    // End date used for the search
    days_back: number;                     // Days back used if no explicit dates
  };
  results: SearchResult[];                 // Array of search results
}

interface SearchResult {
  source: 'News' | 'BOE';                  // "News" or "BOE"
  date: string;                            // Publication date (ISO format)
  title: string;                           // Article/document title
  summary: string | null;                  // Article summary/description (can be null)
  risk_level: string;                      // LLM or keyword-based risk label
  confidence: number;                      // Confidence score (0-1)
  url: string;                             // Link to the article or BOE document
  section?: string;                        // BOE specific fields
  identificador?: string;                  // BOE specific fields
}
```

## 🔧 Environment Configuration

Create a `.env` file with:
```
VITE_API_BASE_URL=http://localhost:8000
```

Or set the backend URL in your environment. The default is `http://localhost:8000`.

## 📋 Legacy Compatibility

For backward compatibility with existing components, a `getRiskAssessment` mutation is also available that converts the old format to the new API format:

```typescript
const [getRiskAssessment] = useGetRiskAssessmentMutation();

// Old format still works
await getRiskAssessment({
  companyName: "Banco Santander",
  dataSource: "both",
  dateRange: {
    type: "custom",
    startDate: "2025-06-01",
    endDate: "2025-06-13"
  }
});
```

## 🔐 Authentication

The API automatically injects auth tokens from localStorage:

```typescript
// Login example
dispatch(login({
  id: '1',
  email: 'user@bhsi.com',
  name: 'User Name',
  token: 'your-jwt-token'
}));

// Token is automatically added to all API requests
```

## 🎨 UI State Management

```typescript
// Access UI state
const { notifications, sidebarOpen } = useAppSelector((state) => state.ui);

// Dispatch UI actions
dispatch(setNotification({
  id: Date.now().toString(),
  type: 'success',
  message: 'Operation completed successfully!',
  duration: 3000
}));

dispatch(toggleSidebar());
```

## 📦 Available Hooks

### API Hooks:
- `useSearchCompanyMutation()` - Main search API (matches backend spec)
- `useGetRiskAssessmentMutation()` - Legacy compatibility
- `useGetSavedResultsQuery()` - Get saved results
- `useSaveResultMutation()` - Save a result
- `useDeleteSavedResultMutation()` - Delete a saved result

### State Hooks:
- `useAppSelector()` - Typed useSelector
- `useAppDispatch()` - Typed useDispatch

## 🚨 Error Handling

Automatic error handling for common HTTP status codes:
- **401 Unauthorized**: Automatically clears auth token and redirects to login
- **403 Forbidden**: Logs error to console
- **500 Server Error**: Logs error to console

## 🔄 Cache Management

RTK Query automatically handles caching and invalidation:
- Search results are cached and invalidated when new searches are performed
- Saved results are automatically refreshed when modified

This setup is **ready for your actual backend API** and matches the specification you provided! 