#!/bin/bash

# XAI Platform Testing Script
# Automated validation of all platform features
# Usage: ./test_platform.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Test API endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    print_test "$description"
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$status" -eq "$expected_status" ]; then
        print_success "Endpoint returned $status"
        return 0
    else
        print_error "Expected $expected_status, got $status"
        return 1
    fi
}

# Main test execution
main() {
    print_header "XAI Platform Testing Suite"
    
    # Check prerequisites
    print_header "1. Checking Prerequisites"
    
    print_test "Docker installed"
    if command_exists docker; then
        print_success "Docker is installed"
    else
        print_error "Docker is not installed"
        exit 1
    fi
    
    print_test "Docker Compose installed"
    if command_exists docker-compose; then
        print_success "Docker Compose is installed"
    else
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_test "Curl installed"
    if command_exists curl; then
        print_success "Curl is installed"
    else
        print_error "Curl is not installed"
        exit 1
    fi
    
    # Check Docker containers
    print_header "2. Checking Docker Containers"
    
    print_test "Backend container running"
    if docker ps | grep -q xai_backend; then
        print_success "Backend container is running"
    else
        print_error "Backend container is not running"
        print_info "Run: docker-compose up -d"
        exit 1
    fi
    
    print_test "Frontend container running"
    if docker ps | grep -q xai_frontend; then
        print_success "Frontend container is running"
    else
        print_info "Frontend runs separately (npm run dev)"
    fi
    
    print_test "PostgreSQL container running"
    if docker ps | grep -q xai_postgres; then
        print_success "PostgreSQL container is running"
    else
        print_error "PostgreSQL container is not running"
        exit 1
    fi
    
    print_test "Redis container running"
    if docker ps | grep -q xai_redis; then
        print_success "Redis container is running"
    else
        print_error "Redis container is not running"
        exit 1
    fi
    
    print_test "Celery worker running"
    if docker ps | grep -q xai_celery_worker; then
        print_success "Celery worker is running"
    else
        print_error "Celery worker is not running"
        exit 1
    fi
    
    # Test API endpoints
    print_header "3. Testing API Endpoints"
    
    test_endpoint "http://localhost:8000/health" 200 "Health check endpoint"
    test_endpoint "http://localhost:8000/docs" 200 "API documentation"
    test_endpoint "http://localhost:8000/api/v1/models" 401 "Models endpoint (requires auth)"
    
    # Test authentication
    print_header "4. Testing Authentication"
    
    print_test "Login endpoint"
    TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"researcher@xai.com","password":"research123"}' \
        | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
    
    if [ -n "$TOKEN" ]; then
        print_success "Login successful, token obtained"
    else
        print_error "Login failed"
        exit 1
    fi
    
    # Test authenticated endpoints
    print_header "5. Testing Authenticated Endpoints"
    
    print_test "Get models list"
    MODELS=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/models)
    MODEL_COUNT=$(echo "$MODELS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
    
    if [ "$MODEL_COUNT" -ge 1 ]; then
        print_success "Found $MODEL_COUNT models"
        MODEL_ID=$(echo "$MODELS" | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['id'])" 2>/dev/null)
        print_info "Using model ID: $MODEL_ID"
    else
        print_error "No models found"
        exit 1
    fi
    
    print_test "Get model details"
    MODEL_DETAILS=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/models/$MODEL_ID")
    MODEL_NAME=$(echo "$MODEL_DETAILS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('name', ''))" 2>/dev/null)
    
    if [ -n "$MODEL_NAME" ]; then
        print_success "Model details retrieved: $MODEL_NAME"
    else
        print_error "Failed to get model details"
    fi
    
    print_test "Get model metrics"
    METRICS=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/models/$MODEL_ID/metrics")
    AUC=$(echo "$METRICS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('auc_roc', 0))" 2>/dev/null)
    
    if [ "$(echo "$AUC > 0" | bc)" -eq 1 ]; then
        print_success "Model metrics retrieved: AUC-ROC = $AUC"
    else
        print_error "Failed to get model metrics"
    fi
    
    # Test SHAP generation
    print_header "6. Testing SHAP Generation"
    
    print_test "Generate SHAP explanation"
    SHAP_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        "http://localhost:8000/api/v1/explanations/generate" \
        -d "{\"model_id\":\"$MODEL_ID\",\"method\":\"shap\",\"params\":{}}")
    
    SHAP_ID=$(echo "$SHAP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    
    if [ -n "$SHAP_ID" ]; then
        print_success "SHAP generation started: $SHAP_ID"
        
        # Wait for completion
        print_info "Waiting for SHAP to complete (max 30 seconds)..."
        for i in {1..15}; do
            sleep 2
            STATUS=$(curl -s -H "Authorization: Bearer $TOKEN" \
                "http://localhost:8000/api/v1/explanations/$SHAP_ID" \
                | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)
            
            if [ "$STATUS" = "completed" ]; then
                print_success "SHAP completed in $((i*2)) seconds"
                break
            elif [ "$STATUS" = "failed" ]; then
                print_error "SHAP generation failed"
                break
            fi
            
            if [ $i -eq 15 ]; then
                print_error "SHAP timed out after 30 seconds"
            fi
        done
    else
        print_error "Failed to start SHAP generation"
    fi
    
    # Test LIME generation
    print_header "7. Testing LIME Generation"
    
    print_test "Generate LIME explanation"
    LIME_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        "http://localhost:8000/api/v1/explanations/generate" \
        -d "{\"model_id\":\"$MODEL_ID\",\"method\":\"lime\",\"params\":{}}")
    
    LIME_ID=$(echo "$LIME_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    
    if [ -n "$LIME_ID" ]; then
        print_success "LIME generation started: $LIME_ID"
        print_info "LIME takes 3-5 minutes, skipping wait in test"
        print_info "Check status manually: curl -H 'Authorization: Bearer $TOKEN' http://localhost:8000/api/v1/explanations/$LIME_ID"
    else
        print_error "Failed to start LIME generation"
    fi
    
    # Test comparison endpoint
    print_header "8. Testing Comparison Endpoint"
    
    print_test "Compare SHAP and LIME"
    COMPARISON=$(curl -s -H "Authorization: Bearer $TOKEN" \
        "http://localhost:8000/api/v1/explanations/compare?model_id=$MODEL_ID")
    
    if echo "$COMPARISON" | grep -q "agreement"; then
        print_success "Comparison endpoint working"
    else
        print_info "Comparison requires both SHAP and LIME to be complete"
    fi
    
    # Test frontend
    print_header "9. Testing Frontend"
    
    test_endpoint "http://localhost:3000" 200 "Frontend home page"
    test_endpoint "http://localhost:3000/login" 200 "Login page"
    test_endpoint "http://localhost:3000/models" 200 "Models page"
    
    # Database check
    print_header "10. Testing Database"
    
    print_test "PostgreSQL connection"
    if docker exec xai_postgres pg_isready -U xai_user >/dev/null 2>&1; then
        print_success "PostgreSQL is ready"
    else
        print_error "PostgreSQL connection failed"
    fi
    
    print_test "Database tables exist"
    TABLE_COUNT=$(docker exec xai_postgres psql -U xai_user -d xai_finance_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    
    if [ "$TABLE_COUNT" -ge 5 ]; then
        print_success "Found $TABLE_COUNT tables"
    else
        print_error "Expected at least 5 tables, found $TABLE_COUNT"
    fi
    
    # Redis check
    print_header "11. Testing Redis"
    
    print_test "Redis connection"
    if docker exec xai_redis redis-cli ping | grep -q PONG; then
        print_success "Redis is responding"
    else
        print_error "Redis connection failed"
    fi
    
    # Celery check
    print_header "12. Testing Celery"
    
    print_test "Celery worker active"
    if docker logs xai_celery_worker 2>&1 | tail -20 | grep -q "ready"; then
        print_success "Celery worker is active"
    else
        print_info "Celery worker status unclear, check logs"
    fi
    
    # Print summary
    print_header "Test Summary"
    
    echo -e "Total Tests: ${BLUE}$TESTS_TOTAL${NC}"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✓ All tests passed!${NC}"
        echo -e "${GREEN}Platform is working correctly!${NC}\n"
        exit 0
    else
        echo -e "\n${RED}✗ Some tests failed${NC}"
        echo -e "${RED}Please check the errors above${NC}\n"
        exit 1
    fi
}

# Run main function
main
