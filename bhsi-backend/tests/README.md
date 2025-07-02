# BHSI Backend Test Suite

This directory contains all tests for the BHSI backend system, organized by functionality and test type.

## Test Organization

### `/agents/`

- **test_analysis.py** - Tests for analysis agents and processing
- **test_news_agent.py** - Tests for news agent functionality

### `/analytics/`

- **test_analytics_frontend.py** - Tests for analytics frontend integration

### `/api/`

- **test_companies.py** - Tests for company-related API endpoints

### `/integration/`

- **test_database_integration.py** - Database integration and CRUD operations
- **test_integrated_search.py** - End-to-end search functionality tests
- **test_mock_system.py** - Mock system and service tests

### `/rss_agents/`

- **test_abc_agent.py** - ABC news agent specific tests
- **test_elconfidencial_agent.py** - El Confidencial agent tests
- **test_eldiario_agent.py** - El Diario agent tests
- **test_europapress_agent.py** - Europa Press agent tests
- **test_integrated_rss_agents.py** - RSS agents integration tests
- **test_lavanguardia_agent.py** - La Vanguardia agent tests
- **test_rss_agents.py** - General RSS agents functionality
- **test_rss_api.py** - RSS API endpoint tests
- **simple_rss_test.py** - Simple RSS functionality tests

### `/utils/`

- **test_import.py** - Import and module loading tests
- **test_logs.py** - Logging functionality tests
- **test_new_features.py** - New feature tests
- **quick_test.py** - Quick utility tests
- **utils.py** - Test utilities and helpers

## Running Tests

### Run all tests:

```bash
pytest
```

### Run specific test categories:

```bash
# Run only integration tests
pytest tests/integration/

# Run only RSS agent tests
pytest tests/rss_agents/

# Run only analytics tests
pytest tests/analytics/

# Run only API tests
pytest tests/api/
```

### Run specific test files:

```bash
# Run a specific test file
pytest tests/integration/test_database_integration.py

# Run with verbose output
pytest tests/rss_agents/test_abc_agent.py -v
```

### Run tests with coverage:

```bash
pytest --cov=app tests/
```

## Test Configuration

- **conftest.py** - Global pytest configuration and fixtures
- **pytest.ini** - Pytest configuration file (in root directory)

## Best Practices

1. **Test Naming**: All test files should be prefixed with `test_`
2. **Test Functions**: All test functions should be prefixed with `test_`
3. **Organization**: Group related tests in appropriate subdirectories
4. **Fixtures**: Use conftest.py for shared fixtures
5. **Documentation**: Add docstrings to test functions explaining what they test

## Migration Notes

All test files have been moved from the root directory to this organized structure.
Update any import statements or test runners that reference the old locations.
