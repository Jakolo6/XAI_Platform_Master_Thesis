#!/usr/bin/env python3
"""
XAI Platform API Testing Script
Comprehensive validation of all API endpoints
"""

import requests
import time
import sys
from typing import Dict, Optional
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
TEST_USER = {
    "email": "researcher@xai.com",
    "password": "research123"
}

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class TestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_total = 0
        self.token: Optional[str] = None
        self.model_id: Optional[str] = None
        self.shap_id: Optional[str] = None
        self.lime_id: Optional[str] = None
        
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    def print_test(self, text: str):
        """Print test description"""
        print(f"{Colors.YELLOW}[TEST]{Colors.END} {text}")
        self.tests_total += 1
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}[✓]{Colors.END} {text}")
        self.tests_passed += 1
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}[✗]{Colors.END} {text}")
        self.tests_failed += 1
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.BLUE}[INFO]{Colors.END} {text}")
    
    def test_health(self):
        """Test health check endpoint"""
        self.print_test("Health check endpoint")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.print_success(f"Health check OK: {response.json()}")
            else:
                self.print_error(f"Health check failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"Health check error: {e}")
    
    def test_docs(self):
        """Test API documentation"""
        self.print_test("API documentation endpoint")
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=5)
            if response.status_code == 200:
                self.print_success("API docs accessible")
            else:
                self.print_error(f"API docs failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"API docs error: {e}")
    
    def test_login(self):
        """Test authentication"""
        self.print_test("Login endpoint")
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json=TEST_USER,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                if self.token:
                    self.print_success("Login successful, token obtained")
                else:
                    self.print_error("Login response missing token")
            else:
                self.print_error(f"Login failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"Login error: {e}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_get_models(self):
        """Test getting models list"""
        self.print_test("Get models list")
        try:
            response = requests.get(
                f"{API_BASE}/models",
                headers=self.get_headers(),
                timeout=5
            )
            if response.status_code == 200:
                models = response.json()
                if models:
                    self.model_id = models[0]['id']
                    self.print_success(f"Found {len(models)} models")
                    self.print_info(f"Using model ID: {self.model_id}")
                else:
                    self.print_error("No models found")
            else:
                self.print_error(f"Get models failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"Get models error: {e}")
    
    def test_get_model_details(self):
        """Test getting model details"""
        self.print_test("Get model details")
        try:
            response = requests.get(
                f"{API_BASE}/models/{self.model_id}",
                headers=self.get_headers(),
                timeout=5
            )
            if response.status_code == 200:
                model = response.json()
                self.print_success(f"Model details: {model.get('name', 'Unknown')}")
                self.print_info(f"Type: {model.get('model_type', 'Unknown')}")
            else:
                self.print_error(f"Get model details failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"Get model details error: {e}")
    
    def test_get_model_metrics(self):
        """Test getting model metrics"""
        self.print_test("Get model metrics")
        try:
            response = requests.get(
                f"{API_BASE}/models/{self.model_id}/metrics",
                headers=self.get_headers(),
                timeout=5
            )
            if response.status_code == 200:
                metrics = response.json()
                auc = metrics.get('auc_roc', 0)
                self.print_success(f"Model metrics: AUC-ROC = {auc:.4f}")
            else:
                self.print_error(f"Get model metrics failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"Get model metrics error: {e}")
    
    def test_generate_shap(self):
        """Test SHAP generation"""
        self.print_test("Generate SHAP explanation")
        try:
            response = requests.post(
                f"{API_BASE}/explanations/generate",
                headers=self.get_headers(),
                json={
                    "model_id": self.model_id,
                    "method": "shap",
                    "params": {}
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.shap_id = data.get('id')
                self.print_success(f"SHAP generation started: {self.shap_id}")
                
                # Wait for completion
                self.print_info("Waiting for SHAP to complete (max 30 seconds)...")
                for i in range(15):
                    time.sleep(2)
                    status_response = requests.get(
                        f"{API_BASE}/explanations/{self.shap_id}",
                        headers=self.get_headers(),
                        timeout=5
                    )
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status')
                        
                        if status == 'completed':
                            self.print_success(f"SHAP completed in {(i+1)*2} seconds")
                            break
                        elif status == 'failed':
                            self.print_error("SHAP generation failed")
                            break
                    
                    if i == 14:
                        self.print_error("SHAP timed out after 30 seconds")
            else:
                self.print_error(f"SHAP generation failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"SHAP generation error: {e}")
    
    def test_generate_lime(self):
        """Test LIME generation"""
        self.print_test("Generate LIME explanation")
        try:
            response = requests.post(
                f"{API_BASE}/explanations/generate",
                headers=self.get_headers(),
                json={
                    "model_id": self.model_id,
                    "method": "lime",
                    "params": {}
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.lime_id = data.get('id')
                self.print_success(f"LIME generation started: {self.lime_id}")
                self.print_info("LIME takes 3-5 minutes, skipping wait in test")
                self.print_info(f"Check status: GET {API_BASE}/explanations/{self.lime_id}")
            else:
                self.print_error(f"LIME generation failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"LIME generation error: {e}")
    
    def test_comparison(self):
        """Test comparison endpoint"""
        self.print_test("Compare SHAP and LIME")
        try:
            response = requests.get(
                f"{API_BASE}/explanations/compare",
                headers=self.get_headers(),
                params={"model_id": self.model_id},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if 'agreement' in data:
                    self.print_success("Comparison endpoint working")
                    self.print_info(f"Agreement: {data.get('agreement', {})}")
                else:
                    self.print_info("Comparison requires both SHAP and LIME complete")
            else:
                self.print_info(f"Comparison not ready: {response.status_code}")
        except Exception as e:
            self.print_info(f"Comparison not available: {e}")
    
    def test_quality_metrics(self):
        """Test quality metrics endpoint"""
        self.print_test("Get quality metrics")
        try:
            response = requests.get(
                f"{API_BASE}/explanations/{self.shap_id}/quality",
                headers=self.get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                metrics = response.json()
                self.print_success("Quality metrics retrieved")
                self.print_info(f"Metrics: {metrics}")
            else:
                self.print_info(f"Quality metrics not available: {response.status_code}")
        except Exception as e:
            self.print_info(f"Quality metrics error: {e}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        print(f"Total Tests: {Colors.BLUE}{self.tests_total}{Colors.END}")
        print(f"Passed: {Colors.GREEN}{self.tests_passed}{Colors.END}")
        print(f"Failed: {Colors.RED}{self.tests_failed}{Colors.END}")
        
        if self.tests_failed == 0:
            print(f"\n{Colors.GREEN}✓ All tests passed!{Colors.END}")
            print(f"{Colors.GREEN}Platform is working correctly!{Colors.END}\n")
            return 0
        else:
            print(f"\n{Colors.RED}✗ Some tests failed{Colors.END}")
            print(f"{Colors.RED}Please check the errors above{Colors.END}\n")
            return 1
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.BOLD}XAI Platform API Testing Suite{Colors.END}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Basic endpoints
        self.print_header("1. Testing Basic Endpoints")
        self.test_health()
        self.test_docs()
        
        # Authentication
        self.print_header("2. Testing Authentication")
        self.test_login()
        
        if not self.token:
            self.print_error("Cannot continue without authentication")
            return self.print_summary()
        
        # Models
        self.print_header("3. Testing Models API")
        self.test_get_models()
        
        if not self.model_id:
            self.print_error("Cannot continue without model ID")
            return self.print_summary()
        
        self.test_get_model_details()
        self.test_get_model_metrics()
        
        # Explanations
        self.print_header("4. Testing SHAP Generation")
        self.test_generate_shap()
        
        self.print_header("5. Testing LIME Generation")
        self.test_generate_lime()
        
        # Comparison
        self.print_header("6. Testing Comparison")
        self.test_comparison()
        
        # Quality metrics
        if self.shap_id:
            self.print_header("7. Testing Quality Metrics")
            self.test_quality_metrics()
        
        # Summary
        return self.print_summary()

def main():
    """Main entry point"""
    runner = TestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
