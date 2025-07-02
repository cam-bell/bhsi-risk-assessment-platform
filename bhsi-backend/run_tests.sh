#!/bin/bash

# BHSI Backend Test Runner
# Usage: ./run_tests.sh [test_category] [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_CATEGORY="all"
VERBOSE=""
COVERAGE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --coverage|-c)
            COVERAGE="--cov=app"
            shift
            ;;
        --help|-h)
            echo "BHSI Backend Test Runner"
            echo ""
            echo "Usage: $0 [test_category] [options]"
            echo ""
            echo "Test Categories:"
            echo "  all              Run all tests (default)"
            echo "  integration      Run integration tests only"
            echo "  rss_agents       Run RSS agent tests only"
            echo "  analytics        Run analytics tests only"
            echo "  api              Run API tests only"
            echo "  agents           Run agent tests only"
            echo "  utils            Run utility tests only"
            echo ""
            echo "Options:"
            echo "  --verbose, -v    Verbose output"
            echo "  --coverage, -c   Run with coverage report"
            echo "  --help, -h       Show this help message"
            echo ""
            exit 0
            ;;
        *)
            TEST_CATEGORY="$1"
            shift
            ;;
    esac
done

echo -e "${BLUE}🧪 BHSI Backend Test Runner${NC}"
echo -e "${BLUE}========================${NC}"

# Determine test path based on category
case $TEST_CATEGORY in
    "all")
        TEST_PATH="tests"
        echo -e "${YELLOW}Running all tests...${NC}"
        ;;
    "integration")
        TEST_PATH="tests/integration"
        echo -e "${YELLOW}Running integration tests...${NC}"
        ;;
    "rss_agents")
        TEST_PATH="tests/rss_agents"
        echo -e "${YELLOW}Running RSS agent tests...${NC}"
        ;;
    "analytics")
        TEST_PATH="tests/analytics"
        echo -e "${YELLOW}Running analytics tests...${NC}"
        ;;
    "api")
        TEST_PATH="tests/api"
        echo -e "${YELLOW}Running API tests...${NC}"
        ;;
    "agents")
        TEST_PATH="tests/agents"
        echo -e "${YELLOW}Running agent tests...${NC}"
        ;;
    "utils")
        TEST_PATH="tests/utils"
        echo -e "${YELLOW}Running utility tests...${NC}"
        ;;
    *)
        echo -e "${RED}Error: Unknown test category '$TEST_CATEGORY'${NC}"
        echo "Use --help for available options"
        exit 1
        ;;
esac

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not detected${NC}"
    echo "Consider activating your virtual environment first"
fi

# Run the tests
echo -e "${BLUE}Test path: $TEST_PATH${NC}"
echo -e "${BLUE}Command: python -m pytest $TEST_PATH $VERBOSE $COVERAGE${NC}"
echo ""

if python -m pytest $TEST_PATH $VERBOSE $COVERAGE; then
    echo -e "${GREEN}✅ Tests completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}❌ Tests failed!${NC}"
    exit 1
fi 