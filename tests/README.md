# FastAPI Test Suite

This directory contains comprehensive tests for the Mergington High School Activities API.

## Test Structure

- `conftest.py` - Test configuration and shared fixtures
- `test_api.py` - Main test suite covering all API endpoints

## Test Coverage

The test suite covers:

### API Endpoints
- `GET /` - Root redirect to static files
- `GET /activities` - Retrieve all activities
- `POST /activities/{activity_name}/signup` - Student registration
- `POST /activities/{activity_name}/unregister` - Student unregistration

### Test Categories

#### TestActivitiesAPI
- Basic endpoint functionality
- Success and error scenarios
- Data validation and integrity
- Edge cases (non-existent activities, duplicate registrations, etc.)

#### TestActivityBusinessLogic
- Business logic validation
- Complete workflow testing (signup → verify → unregister → verify)
- Capacity limits and constraints
- Special character handling

## Running Tests

### Run all tests:
```bash
python -m pytest
```

### Run with verbose output:
```bash
python -m pytest -v
```

### Run with coverage report:
```bash
python -m pytest --cov=src --cov-report=term-missing
```

### Run specific test file:
```bash
python -m pytest tests/test_api.py
```

### Run specific test:
```bash
python -m pytest tests/test_api.py::TestActivitiesAPI::test_signup_for_activity_success
```

## Test Results

✅ **13 tests passing**  
✅ **97% code coverage**  
✅ **Comprehensive API testing**  
✅ **Business logic validation**  

## Dependencies

The following testing dependencies are required:
- `pytest` - Testing framework
- `httpx` - HTTP client for testing FastAPI
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting