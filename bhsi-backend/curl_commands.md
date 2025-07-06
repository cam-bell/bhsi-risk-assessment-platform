# BHSI Pipeline - Curl Test Commands

## Prerequisites

- Server running on `http://localhost:8000`
- Admin user created: `admin@bhsi.com` / `admin123`

## 1. Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

## 2. Authentication

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@bhsi.com",
    "password": "admin123"
  }'
```

### Extract Token (save to variable)

```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@bhsi.com",
    "password": "admin123"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"
```

## 3. Streamlined Search (with authentication)

```bash
curl -X POST "http://localhost:8000/api/v1/streamlined/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "company_name": "Banco Santander",
    "days_back": 7,
    "include_boe": true,
    "include_news": true,
    "include_rss": false,
    "force_refresh": false,
    "cache_age_hours": 24
  }'
```

## 4. Legacy Search (no authentication required)

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Repsol",
    "days_back": 7,
    "include_boe": true,
    "include_news": true,
    "include_rss": false
  }'
```

## 5. Company Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/companies/analyze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Banco Santander",
    "vat": "A39000013",
    "description": "Spanish multinational banking group",
    "sector": "Banking",
    "client_tier": "premium",
    "include_boe": true,
    "include_news": true,
    "include_rss": false,
    "days_back": 7
  }'
```

## 6. Management Summary

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/management-summary" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "company_name": "Banco Santander",
    "include_evidence": true,
    "language": "es"
  }'
```

## 7. Vector Search

```bash
curl -X POST "http://localhost:8000/api/v1/streamlined/semantic-search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "Banco Santander legal risks",
    "k": 5,
    "use_cache": true,
    "include_metadata": true
  }'
```

## 8. Statistics Endpoints

### Cache Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/streamlined/search/cache-stats" \
  -H "Authorization: Bearer $TOKEN"
```

### Database Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/streamlined/search/database-stats" \
  -H "Authorization: Bearer $TOKEN"
```

### Performance Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/streamlined/search/performance" \
  -H "Authorization: Bearer $TOKEN"
```

### Vector Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/streamlined/vector-stats" \
  -H "Authorization: Bearer $TOKEN"
```

## 9. Analytics Endpoints

### Risk Trends

```bash
curl -X GET "http://localhost:8000/api/v1/companies/analytics/trends" \
  -H "Authorization: Bearer $TOKEN"
```

### System Alerts

```bash
curl -X GET "http://localhost:8000/api/v1/companies/analytics/alerts" \
  -H "Authorization: Bearer $TOKEN"
```

### Sector Analytics

```bash
curl -X GET "http://localhost:8000/api/v1/companies/analytics/sectors" \
  -H "Authorization: Bearer $TOKEN"
```

## 10. User Management

### List Users (Admin only)

```bash
curl -X GET "http://localhost:8000/api/v1/auth/users" \
  -H "Authorization: Bearer $TOKEN"
```

### User Profile

```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer $TOKEN"
```

## 11. System Status

```bash
curl -X GET "http://localhost:8000/api/v1/companies/system/status" \
  -H "Authorization: Bearer $TOKEN"
```

## Quick Test Script

Run the quick test script:

```bash
./quick_curl_test.sh
```

## Full Test Script

Run the comprehensive test script:

```bash
./test_pipeline_curl.sh
```

## Expected Results

### Successful Search Response

- `metadata.total_results` > 0
- `performance.total_time_seconds` < 10
- `cache_info.search_method` shows "cached" or "fresh"

### Successful Analysis Response

- `risk_assessment.overall_risk` is "red", "orange", or "green"
- `processing_time.total_time` < 30 seconds

### Authentication

- `access_token` present in login response
- 401 errors for protected endpoints without token
- 200 success for protected endpoints with valid token
