#!/usr/bin/env python3
"""
Phase 1 QA Validation Tests for Canada Immigration OS
FAANG-level automated validation covering:
1. Happy-Path E2E flows
2. Multi-Tenant Isolation
3. Config API Sanity
4. Core API functionality
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Any
import httpx

class Phase1Validator:
    """FAANG-level validation suite for Phase 1 implementation"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self.results = {
            "happy_path_e2e": [],
            "multi_tenant": [],
            "config_api": [],
            "health_checks": [],
            "errors": []
        }
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def log_result(self, category: str, test_name: str, status: str, details: str = "", response_time: float = 0):
        """Log test result with FAANG-level detail"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": time.time()
        }
        self.results[category].append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} [{category.upper()}] {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_time > 0:
            print(f"   Response time: {result['response_time_ms']}ms")

    async def validate_health_checks(self):
        """Validate basic health and connectivity"""
        print("\n🔍 HEALTH CHECKS")
        
        # Test 1: API Health Check
        start_time = time.time()
        try:
            response = await self.client.get("/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy" and data.get("database") == "connected":
                    self.log_result("health_checks", "API Health Check", "PASS", 
                                  f"Status: {data.get('status')}, DB: {data.get('database')}", response_time)
                else:
                    self.log_result("health_checks", "API Health Check", "FAIL", 
                                  f"Unexpected response: {data}", response_time)
            else:
                self.log_result("health_checks", "API Health Check", "FAIL", 
                              f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("health_checks", "API Health Check", "FAIL", f"Exception: {str(e)}")

        # Test 2: API Root Endpoint
        start_time = time.time()
        try:
            response = await self.client.get("/")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "Canada Immigration OS API" in data.get("message", ""):
                    self.log_result("health_checks", "API Root Endpoint", "PASS", 
                                  f"Message: {data.get('message')}", response_time)
                else:
                    self.log_result("health_checks", "API Root Endpoint", "FAIL", 
                                  f"Unexpected message: {data}", response_time)
            else:
                self.log_result("health_checks", "API Root Endpoint", "FAIL", 
                              f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("health_checks", "API Root Endpoint", "FAIL", f"Exception: {str(e)}")

    async def validate_happy_path_e2e(self):
        """Validate happy-path end-to-end flows"""
        print("\n🎯 HAPPY-PATH E2E VALIDATION")
        
        # Test 1: Create Person
        start_time = time.time()
        try:
            person_data = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "date_of_birth": "1990-01-15",
                "nationality": "US",
                "passport_number": "US123456789"
            }
            
            response = await self.client.post("/api/v1/v1/persons/", json=person_data)
            response_time = time.time() - start_time
            
            if response.status_code == 201:
                person = response.json()
                person_id = person.get("id")
                self.log_result("happy_path_e2e", "Create Person", "PASS", 
                              f"Created person ID: {person_id}", response_time)
                
                # Test 2: Create Case for Person
                start_time = time.time()
                case_data = {
                    "person_id": person_id,
                    "case_type": "express_entry",
                    "status": "assessment",
                    "priority": "medium",
                    "description": "Express Entry application for skilled worker"
                }
                
                response = await self.client.post("/api/v1/v1/cases/", json=case_data)
                response_time = time.time() - start_time
                
                if response.status_code == 201:
                    case = response.json()
                    case_id = case.get("id")
                    self.log_result("happy_path_e2e", "Create Case", "PASS", 
                                  f"Created case ID: {case_id}", response_time)
                    
                    # Test 3: Retrieve Case with Person
                    start_time = time.time()
                    response = await self.client.get(f"/api/v1/v1/cases/{case_id}")
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        case_detail = response.json()
                        if case_detail.get("person_id") == person_id:
                            self.log_result("happy_path_e2e", "Retrieve Case", "PASS", 
                                          f"Case retrieved with correct person_id", response_time)
                        else:
                            self.log_result("happy_path_e2e", "Retrieve Case", "FAIL", 
                                          f"Person ID mismatch: expected {person_id}, got {case_detail.get('person_id')}", response_time)
                    else:
                        self.log_result("happy_path_e2e", "Retrieve Case", "FAIL", 
                                      f"HTTP {response.status_code}", response_time)
                else:
                    self.log_result("happy_path_e2e", "Create Case", "FAIL", 
                                  f"HTTP {response.status_code}: {response.text}", response_time)
            else:
                self.log_result("happy_path_e2e", "Create Person", "FAIL", 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("happy_path_e2e", "E2E Flow", "FAIL", f"Exception: {str(e)}")

    async def validate_multi_tenant_isolation(self):
        """Validate multi-tenant data isolation"""
        print("\n🏢 MULTI-TENANT ISOLATION VALIDATION")
        
        # Test 1: Create data for tenant 1
        start_time = time.time()
        try:
            headers_tenant1 = {"X-Tenant-ID": "tenant1"}
            person_data_t1 = {
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice.smith@tenant1.com",
                "phone": "+1-555-1111",
                "date_of_birth": "1985-05-20",
                "nationality": "CA",
                "passport_number": "CA111111111"
            }
            
            response = await self.client.post("/api/v1/persons/", json=person_data_t1, headers=headers_tenant1)
            response_time = time.time() - start_time
            
            if response.status_code == 201:
                person_t1 = response.json()
                person_t1_id = person_t1.get("id")
                self.log_result("multi_tenant", "Create Person Tenant1", "PASS", 
                              f"Created person ID: {person_t1_id}", response_time)
                
                # Test 2: Create data for tenant 2
                start_time = time.time()
                headers_tenant2 = {"X-Tenant-ID": "tenant2"}
                person_data_t2 = {
                    "first_name": "Bob",
                    "last_name": "Johnson",
                    "email": "bob.johnson@tenant2.com",
                    "phone": "+1-555-2222",
                    "date_of_birth": "1988-08-10",
                    "nationality": "UK",
                    "passport_number": "UK222222222"
                }
                
                response = await self.client.post("/api/v1/persons/", json=person_data_t2, headers=headers_tenant2)
                response_time = time.time() - start_time
                
                if response.status_code == 201:
                    person_t2 = response.json()
                    person_t2_id = person_t2.get("id")
                    self.log_result("multi_tenant", "Create Person Tenant2", "PASS", 
                                  f"Created person ID: {person_t2_id}", response_time)
                    
                    # Test 3: Verify tenant1 cannot see tenant2 data
                    start_time = time.time()
                    response = await self.client.get(f"/api/v1/persons/{person_t2_id}", headers=headers_tenant1)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 404:
                        self.log_result("multi_tenant", "Tenant Isolation Check", "PASS", 
                                      f"Tenant1 correctly cannot access Tenant2 person", response_time)
                    else:
                        self.log_result("multi_tenant", "Tenant Isolation Check", "FAIL", 
                                      f"Tenant isolation breach: HTTP {response.status_code}", response_time)
                        
                    # Test 4: Verify tenant2 can see their own data
                    start_time = time.time()
                    response = await self.client.get(f"/api/v1/persons/{person_t2_id}", headers=headers_tenant2)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        person_data = response.json()
                        if person_data.get("email") == "bob.johnson@tenant2.com":
                            self.log_result("multi_tenant", "Tenant Data Access", "PASS", 
                                          f"Tenant2 can access their own data", response_time)
                        else:
                            self.log_result("multi_tenant", "Tenant Data Access", "FAIL", 
                                          f"Data corruption: wrong email returned", response_time)
                    else:
                        self.log_result("multi_tenant", "Tenant Data Access", "FAIL", 
                                      f"HTTP {response.status_code}", response_time)
                else:
                    self.log_result("multi_tenant", "Create Person Tenant2", "FAIL", 
                                  f"HTTP {response.status_code}: {response.text}", response_time)
            else:
                self.log_result("multi_tenant", "Create Person Tenant1", "FAIL", 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("multi_tenant", "Multi-tenant Flow", "FAIL", f"Exception: {str(e)}")

    async def validate_config_api(self):
        """Validate configuration API functionality"""
        print("\n⚙️ CONFIG API VALIDATION")
        
        # Test 1: Get Case Types
        start_time = time.time()
        try:
            response = await self.client.get("/api/v1/config/case-types")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                case_types = response.json()
                self.log_result("config_api", "Get Case Types", "PASS", 
                              f"Retrieved case types: {len(case_types) if isinstance(case_types, list) else 'object'}", response_time)
                
                # Test 2: Get Templates
                start_time = time.time()
                response = await self.client.get("/api/v1/config/templates")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    templates = response.json()
                    self.log_result("config_api", "Get Templates", "PASS", 
                                  f"Retrieved templates: {len(templates) if isinstance(templates, list) else 'object'}", response_time)
                else:
                    self.log_result("config_api", "Get Templates", "FAIL", 
                                  f"HTTP {response.status_code}", response_time)
                
                # Test 3: Get Feature Flags (test with a common flag)
                start_time = time.time()
                response = await self.client.get("/api/v1/config/feature-flags/multi_tenant_enabled")
                response_time = time.time() - start_time
                
                if response.status_code in [200, 404]:  # 404 is acceptable if flag doesn't exist
                    status = "PASS" if response.status_code == 200 else "WARN"
                    details = f"Feature flag endpoint accessible (HTTP {response.status_code})"
                    self.log_result("config_api", "Get Feature Flag", status, details, response_time)
                else:
                    self.log_result("config_api", "Get Feature Flag", "FAIL", 
                                  f"HTTP {response.status_code}", response_time)
                
            else:
                self.log_result("config_api", "Get Case Types", "FAIL", 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("config_api", "Config API Flow", "FAIL", f"Exception: {str(e)}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_tests = sum(len(tests) for tests in self.results.values() if isinstance(tests, list))
        passed_tests = sum(1 for category in self.results.values() 
                          if isinstance(category, list)
                          for test in category 
                          if test.get("status") == "PASS")
        failed_tests = total_tests - passed_tests
        
        avg_response_times = {}
        for category, tests in self.results.items():
            if isinstance(tests, list) and tests:
                response_times = [t.get("response_time_ms", 0) for t in tests if t.get("response_time_ms", 0) > 0]
                if response_times:
                    avg_response_times[category] = round(sum(response_times) / len(response_times), 2)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": round((passed_tests / total_tests * 100) if total_tests > 0 else 0, 2),
                "avg_response_times_ms": avg_response_times
            },
            "detailed_results": self.results,
            "recommendations": self._generate_recommendations()
        }
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate FAANG-level recommendations based on test results"""
        recommendations = []
        
        # Check for failed tests
        failed_categories = []
        for category, tests in self.results.items():
            if isinstance(tests, list):
                failed_tests = [t for t in tests if t.get("status") == "FAIL"]
                if failed_tests:
                    failed_categories.append(category)
        
        if failed_categories:
            recommendations.append(f"❌ CRITICAL: Failed tests in categories: {', '.join(failed_categories)}. Immediate attention required.")
        
        # Check response times
        slow_categories = []
        for category, avg_time in self._get_avg_response_times().items():
            if avg_time > 1000:  # > 1 second
                slow_categories.append(f"{category} ({avg_time}ms)")
        
        if slow_categories:
            recommendations.append(f"⚠️ PERFORMANCE: Slow response times detected in: {', '.join(slow_categories)}. Consider optimization.")
        
        # Multi-tenant specific recommendations
        multi_tenant_tests = self.results.get("multi_tenant", [])
        isolation_tests = [t for t in multi_tenant_tests if "isolation" in t.get("test", "").lower()]
        if any(t.get("status") == "FAIL" for t in isolation_tests):
            recommendations.append("🔒 SECURITY: Multi-tenant isolation failures detected. This is a critical security issue.")
        
        if not recommendations:
            recommendations.append("✅ EXCELLENT: All tests passed. Phase 1 implementation meets FAANG-level quality standards.")
        
        return recommendations

    def _get_avg_response_times(self) -> Dict[str, float]:
        """Calculate average response times by category"""
        avg_times = {}
        for category, tests in self.results.items():
            if isinstance(tests, list) and tests:
                response_times = [t.get("response_time_ms", 0) for t in tests if t.get("response_time_ms", 0) > 0]
                if response_times:
                    avg_times[category] = round(sum(response_times) / len(response_times), 2)
        return avg_times

async def main():
    """Main validation runner"""
    print("🚀 PHASE 1 QA VALIDATION - CANADA IMMIGRATION OS")
    print("=" * 60)
    print("FAANG-level automated validation suite")
    print("Testing: Happy-Path E2E, Multi-Tenant Isolation, Config API, Health Checks")
    print("=" * 60)
    
    async with Phase1Validator() as validator:
        # Run all validation suites
        await validator.validate_health_checks()
        await validator.validate_happy_path_e2e()
        await validator.validate_multi_tenant_isolation()
        await validator.validate_config_api()
        
        # Generate and display report
        print("\n📊 VALIDATION REPORT")
        print("=" * 60)
        
        report = validator.generate_report()
        summary = report["summary"]
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']}%")
        
        if summary["avg_response_times_ms"]:
            print("\nAverage Response Times:")
            for category, time_ms in summary["avg_response_times_ms"].items():
                print(f"  {category}: {time_ms}ms")
        
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  {rec}")
        
        # Save detailed report
        report_file = "/tmp/phase1_validation_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Return exit code based on results
        return 0 if summary["failed"] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)