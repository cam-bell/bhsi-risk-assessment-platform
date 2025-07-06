#!/bin/bash

# Quick BHSI Pipeline Test using curl
# Simple test of main endpoints

BASE_URL="http://localhost:8000"
API_BASE="$BASE_URL/api/v1"

echo "🚀 Quick BHSI Pipeline Test"
echo "============================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}1. Testing Health Check...${NC}"
curl -s "$BASE_URL/health" | jq '.' 2>/dev/null || curl -s "$BASE_URL/health"

echo -e "\n${BLUE}2. Testing Admin Login...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "admin@bhsi.com",
        "password": "admin123"
    }')

echo "$LOGIN_RESPONSE" | jq '.' 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✅ Login successful, token obtained${NC}"
    
    echo -e "\n${BLUE}3. Testing Streamlined Search (with auth)...${NC}"
    curl -s -X POST "$API_BASE/streamlined/search" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{
            "company_name": "Banco Santander",
            "days_back": 7,
            "include_boe": true,
            "include_news": true,
            "include_rss": false,
            "force_refresh": false
        }' | jq '.metadata, .performance' 2>/dev/null || echo "Search completed"
    
    echo -e "\n${BLUE}4. Testing Legacy Search (no auth)...${NC}"
    curl -s -X POST "$API_BASE/search" \
        -H "Content-Type: application/json" \
        -d '{
            "company_name": "Repsol",
            "days_back": 7,
            "include_boe": true,
            "include_news": true,
            "include_rss": false
        }' | jq '.metadata, .performance' 2>/dev/null || echo "Legacy search completed"
    
    echo -e "\n${BLUE}5. Testing Company Analysis...${NC}"
    curl -s -X POST "$API_BASE/companies/analyze" \
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
        }' | jq '.risk_assessment.overall_risk, .processing_time' 2>/dev/null || echo "Analysis completed"
    
    echo -e "\n${BLUE}6. Testing Cache Stats...${NC}"
    curl -s -X GET "$API_BASE/streamlined/search/cache-stats" \
        -H "Authorization: Bearer $TOKEN" | jq '.cache_system, .cache_benefits' 2>/dev/null || echo "Cache stats retrieved"
    
    echo -e "\n${BLUE}7. Testing Performance Stats...${NC}"
    curl -s -X GET "$API_BASE/streamlined/search/performance" \
        -H "Authorization: Bearer $TOKEN" | jq '.architecture, .improvements' 2>/dev/null || echo "Performance stats retrieved"
    
else
    echo -e "${RED}❌ Login failed${NC}"
fi

echo -e "\n${GREEN}✅ Quick test completed!${NC}" 