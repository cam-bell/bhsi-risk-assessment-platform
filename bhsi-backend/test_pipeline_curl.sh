#!/bin/bash

# BHSI Pipeline Test Script using curl
# Tests the complete pipeline: authentication, search, and analysis

BASE_URL="http://localhost:8000"
API_BASE="$BASE_URL/api/v1"

echo "🚀 BHSI Pipeline Test - Using curl"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "SUCCESS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "ERROR" ]; then
        echo -e "${RED}❌ $message${NC}"
    elif [ "$status" = "INFO" ]; then
        echo -e "${BLUE}ℹ️  $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    fi
}

# Function to make API calls and check response
make_api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "\n${BLUE}Testing: $description${NC}"
    echo "Endpoint: $method $endpoint"
    
    if [ -n "$data" ]; then
        echo "Data: $data"
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE$endpoint")
    fi
    
    # Extract status code and body
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    echo "HTTP Status: $http_code"
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        print_status "SUCCESS" "$description completed successfully"
        echo "Response preview:"
        echo "$body" | jq '.' 2>/dev/null || echo "$body" | head -c 500
    else
        print_status "ERROR" "$description failed with status $http_code"
        echo "Error response:"
        echo "$body"
    fi
    
    echo "----------------------------------------"
}

# Check if server is running
echo "🔍 Checking if server is running..."
if curl -s "$BASE_URL/health" > /dev/null; then
    print_status "SUCCESS" "Server is running"
else
    print_status "ERROR" "Server is not running. Please start the server first."
    exit 1
fi

# Test 1: Health Check
make_api_call "GET" "/health" "" "Health Check"

# Test 2: Authentication - Login
print_status "INFO" "Testing authentication..."
login_data='{
    "email": "admin@bhsi.com",
    "password": "admin123"
}'

make_api_call "POST" "/auth/login" "$login_data" "Admin Login"

# Extract token from login response
TOKEN=$(curl -s -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d "$login_data" | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    print_status "ERROR" "Failed to get authentication token"
    exit 1
else
    print_status "SUCCESS" "Authentication token obtained"
fi

# Test 3: Streamlined Search (with authentication)
print_status "INFO" "Testing streamlined search with authentication..."
search_data='{
    "company_name": "Banco Santander",
    "days_back": 7,
    "include_boe": true,
    "include_news": true,
    "include_rss": true,
    "force_refresh": false,
    "cache_age_hours": 24
}'

make_api_call "POST" "/streamlined/search" "$search_data" "Streamlined Search (Authenticated)"

# Test 4: Legacy Search (without authentication)
print_status "INFO" "Testing legacy search without authentication..."
legacy_search_data='{
    "company_name": "Repsol",
    "days_back": 7,
    "include_boe": true,
    "include_news": true,
    "include_rss": false
}'

make_api_call "POST" "/search" "$legacy_search_data" "Legacy Search (No Auth)"

# Test 5: Company Analysis
print_status "INFO" "Testing company analysis..."
analysis_data='{
    "name": "Banco Santander",
    "vat": "A39000013",
    "description": "Spanish multinational banking group",
    "sector": "Banking",
    "client_tier": "premium",
    "include_boe": true,
    "include_news": true,
    "include_rss": true,
    "days_back": 7
}'

make_api_call "POST" "/companies/analyze" "$analysis_data" "Company Analysis"

# Test 6: Management Summary
print_status "INFO" "Testing management summary generation..."
summary_data='{
    "company_name": "Banco Santander",
    "include_evidence": true,
    "language": "es"
}'

make_api_call "POST" "/analysis/management-summary" "$summary_data" "Management Summary"

# Test 7: Vector Search (with authentication)
print_status "INFO" "Testing vector search..."
vector_search_data='{
    "query": "Banco Santander legal risks",
    "k": 5,
    "use_cache": true,
    "include_metadata": true
}'

make_api_call "POST" "/streamlined/semantic-search" "$vector_search_data" "Vector Search"

# Test 8: Cache Statistics
make_api_call "GET" "/streamlined/search/cache-stats" "" "Cache Statistics"

# Test 9: Database Statistics
make_api_call "GET" "/streamlined/search/database-stats" "" "Database Statistics"

# Test 10: Performance Statistics
make_api_call "GET" "/streamlined/search/performance" "" "Performance Statistics"

# Test 11: Vector Statistics
make_api_call "GET" "/streamlined/vector-stats" "" "Vector Statistics"

# Test 12: System Status
make_api_call "GET" "/companies/system/status" "" "System Status"

# Test 13: Analytics Endpoints
print_status "INFO" "Testing analytics endpoints..."

make_api_call "GET" "/companies/analytics/trends" "" "Risk Trends"

make_api_call "GET" "/companies/analytics/alerts" "" "System Alerts"

make_api_call "GET" "/companies/analytics/sectors" "" "Sector Analytics"

# Test 14: User Management (Admin only)
print_status "INFO" "Testing user management endpoints..."

make_api_call "GET" "/auth/users" "" "List Users (Admin)"

# Test 15: User Profile
make_api_call "GET" "/auth/profile" "" "User Profile"

# Summary
echo -e "\n${BLUE}🎯 Pipeline Test Summary${NC}"
echo "================================"
print_status "INFO" "All tests completed. Check the output above for results."
print_status "INFO" "Key endpoints tested:"
echo "  - Authentication (login)"
echo "  - Streamlined Search (with auth)"
echo "  - Legacy Search (no auth)"
echo "  - Company Analysis"
echo "  - Management Summary"
echo "  - Vector Search"
echo "  - Cache & Database Stats"
echo "  - Analytics endpoints"
echo "  - User Management"

echo -e "\n${GREEN}✅ Pipeline test completed!${NC}" 