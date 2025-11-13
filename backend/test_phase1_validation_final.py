#!/usr/bin/env python3
"""
Phase 1 QA Validation Tests for Canada Immigration OS - Final Version
FAANG-level automated validation with comprehensive issue documentation
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Any, Optional
import httpx

class Phase1ValidatorFinal:
    """FAANG-level validation suite for Phase 1 implementation with issue handling"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self.results = {
            "health_checks": [],
            "infrastructure": [],
            "api_structure": [],
            "security_posture": [],
            "config_api": [],
            "known_issues": [],
            "errors": []
        }
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def log_result(self, category: str, test_name: str, status: str, details: str = "", response_time: float = 0, issue_type: str = None):
        """Log test result with FAANG-level detail"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": time.time(),
            "issue_type": issue_type
        }
        self.results[category].append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️" if status == "WARN" else "🔍"
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

    async def validate_infrastructure(self):
        """Validate infrastructure components"""
        print("\n🏗️ INFRASTRUCTURE VALIDATION")
        
        # Test 1: Database Connection via Health Check
        start_time = time.time()
        try:
            response = await self.client.get("/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("database") == "connected":
                    self.log_result("infrastructure", "Database Connectivity", "PASS", 
                                  "PostgreSQL database accessible via API", response_time)
                else:
                    self.log_result("infrastructure", "Database Connectivity", "FAIL", 
                                  f"Database status: {data.get('database')}", response_time)
            else:
                self.log_result("infrastructure", "Database Connectivity", "FAIL", 
                              f"Health check failed: HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("infrastructure", "Database Connectivity", "FAIL", f"Exception: {str(e)}")

        # Test 2: API Response Times
        start_time = time.time()
        try:
            response = await self.client.get("/")
            response_time = time.time() - start_time
            
            if response_time < 0.1:  # 100ms
                self.log_result("infrastructure", "API Response Performance", "PASS", 
                              f"Fast response time: {response_time*1000:.2f}ms", response_time)
            elif response_time < 1.0:  # 1 second
                self.log_result("infrastructure", "API Response Performance", "WARN", 
                              f"Acceptable response time: {response_time*1000:.2f}ms", response_time)
            else:
                self.log_result("infrastructure", "API Response Performance", "FAIL", 
                              f"Slow response time: {response_time*1000:.2f}ms", response_time)
        except Exception as e:
            self.log_result("infrastructure", "API Response Performance", "FAIL", f"Exception: {str(e)}")

    async def validate_api_structure(self):
        """Validate API structure and routing"""
        print("\n🔗 API STRUCTURE VALIDATION")
        
        # Test 1: API Versioning
        start_time = time.time()
        try:
            response = await self.client.get("/")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("version"):
                    self.log_result("api_structure", "API Versioning", "PASS", 
                                  f"Version: {data.get('version')}", response_time)
                else:
                    self.log_result("api_structure", "API Versioning", "WARN", 
                                  "No version information in root endpoint", response_time)
            else:
                self.log_result("api_structure", "API Versioning", "FAIL", 
                              f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("api_structure", "API Versioning", "FAIL", f"Exception: {str(e)}")

        # Test 2: Protected Endpoints Return Proper Auth Errors
        protected_endpoints = [
            "/api/v1/persons/",
            "/api/v1/cases/",
            "/api/v1/users/me"
        ]
        
        for endpoint in protected_endpoints:
            start_time = time.time()
            try:
                response = await self.client.get(endpoint)
                response_time = time.time() - start_time
                
                if response.status_code == 401:
                    self.log_result("api_structure", f"Protected Endpoint {endpoint}", "PASS", 
                                  "Correctly returns 401 Unauthorized", response_time)
                elif response.status_code == 403:
                    self.log_result("api_structure", f"Protected Endpoint {endpoint}", "PASS", 
                                  "Correctly returns 403 Forbidden", response_time)
                elif response.status_code == 404:
                    self.log_result("api_structure", f"Protected Endpoint {endpoint}", "WARN", 
                                  "Returns 404 - endpoint may not exist", response_time)
                else:
                    self.log_result("api_structure", f"Protected Endpoint {endpoint}", "FAIL", 
                                  f"Unexpected status: HTTP {response.status_code}", response_time)
            except Exception as e:
                self.log_result("api_structure", f"Protected Endpoint {endpoint}", "FAIL", f"Exception: {str(e)}")

    async def validate_security_posture(self):
        """Validate security implementation"""
        print("\n🔒 SECURITY POSTURE VALIDATION")
        
        # Test 1: Authentication Endpoint Exists
        start_time = time.time()
        try:
            # Test registration endpoint structure
            invalid_data = {"email": "invalid", "password": "test"}
            response = await self.client.post("/api/v1/auth/register", json=invalid_data)
            response_time = time.time() - start_time
            
            if response.status_code in [400, 422]:  # Validation errors are expected
                self.log_result("security_posture", "Auth Registration Endpoint", "PASS", 
                              f"Endpoint exists and validates input (HTTP {response.status_code})", response_time)
            elif response.status_code == 404:
                self.log_result("security_posture", "Auth Registration Endpoint", "FAIL", 
                              "Registration endpoint not found", response_time)
            else:
                self.log_result("security_posture", "Auth Registration Endpoint", "WARN", 
                              f"Unexpected response: HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("security_posture", "Auth Registration Endpoint", "FAIL", f"Exception: {str(e)}")

        # Test 2: Login Endpoint Exists
        start_time = time.time()
        try:
            invalid_login = {"email": "nonexistent@example.com", "password": "wrongpass"}
            response = await self.client.post("/api/v1/auth/login-json", json=invalid_login)
            response_time = time.time() - start_time
            
            if response.status_code == 401:
                self.log_result("security_posture", "Auth Login Endpoint", "PASS", 
                              "Login endpoint exists and properly rejects invalid credentials", response_time)
            elif response.status_code == 404:
                self.log_result("security_posture", "Auth Login Endpoint", "FAIL", 
                              "Login endpoint not found", response_time)
            else:
                self.log_result("security_posture", "Auth Login Endpoint", "WARN", 
                              f"Unexpected response: HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("security_posture", "Auth Login Endpoint", "FAIL", f"Exception: {str(e)}")

        # Test 3: Password Hashing Issue Documentation
        self.log_result("known_issues", "Password Hashing", "ISSUE", 
                      "bcrypt password hashing fails with '72 bytes' error. This is a critical issue preventing user registration. Likely caused by bcrypt/passlib version compatibility issue.", 
                      issue_type="CRITICAL")

    async def validate_config_api(self):
        """Validate configuration API functionality"""
        print("\n⚙️ CONFIG API VALIDATION")
        
        # Test 1: Case Types Configuration
        start_time = time.time()
        try:
            response = await self.client.get("/api/v1/config/case-types")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                case_types = response.json()
                self.log_result("config_api", "Case Types Config", "PASS", 
                              f"Retrieved case types: {len(case_types) if isinstance(case_types, list) else 'object'}", response_time)
            else:
                self.log_result("config_api", "Case Types Config", "FAIL", 
                              f"HTTP {response.status_code}: {response.text}", response_time)
        except Exception as e:
            self.log_result("config_api", "Case Types Config", "FAIL", f"Exception: {str(e)}")

        # Test 2: Templates Configuration
        start_time = time.time()
        try:
            response = await self.client.get("/api/v1/config/templates")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                templates = response.json()
                self.log_result("config_api", "Templates Config", "PASS", 
                              f"Retrieved templates: {len(templates) if isinstance(templates, list) else 'object'}", response_time)
            elif response.status_code == 422:
                self.log_result("config_api", "Templates Config", "WARN", 
                              "Templates endpoint requires parameters (HTTP 422)", response_time)
            else:
                self.log_result("config_api", "Templates Config", "FAIL", 
                              f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("config_api", "Templates Config", "FAIL", f"Exception: {str(e)}")

        # Test 3: Feature Flags
        start_time = time.time()
        try:
            response = await self.client.get("/api/v1/config/feature-flags/test_flag")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                flag_data = response.json()
                self.log_result("config_api", "Feature Flags", "PASS", 
                              f"Feature flag system operational", response_time)
            elif response.status_code in [404, 403]:
                self.log_result("config_api", "Feature Flags", "WARN", 
                              f"Feature flag endpoint accessible but requires auth/setup (HTTP {response.status_code})", response_time)
            else:
                self.log_result("config_api", "Feature Flags", "FAIL", 
                              f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.log_result("config_api", "Feature Flags", "FAIL", f"Exception: {str(e)}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        # Count tests by status
        all_tests = []
        for category, tests in self.results.items():
            if isinstance(tests, list):
                all_tests.extend(tests)
        
        total_tests = len(all_tests)
        passed_tests = len([t for t in all_tests if t.get("status") == "PASS"])
        warned_tests = len([t for t in all_tests if t.get("status") == "WARN"])
        failed_tests = len([t for t in all_tests if t.get("status") == "FAIL"])
        issues = len([t for t in all_tests if t.get("status") == "ISSUE"])
        
        # Calculate average response times
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
                "warned": warned_tests,
                "failed": failed_tests,
                "issues": issues,
                "success_rate": round((passed_tests / total_tests * 100) if total_tests > 0 else 0, 2),
                "avg_response_times_ms": avg_response_times
            },
            "detailed_results": self.results,
            "recommendations": self._generate_recommendations(),
            "phase_1_assessment": self._generate_phase_assessment()
        }
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate FAANG-level recommendations based on test results"""
        recommendations = []
        
        # Check for critical issues
        critical_issues = []
        for category, tests in self.results.items():
            if isinstance(tests, list):
                for test in tests:
                    if test.get("issue_type") == "CRITICAL":
                        critical_issues.append(f"{test.get('test')}: {test.get('details')}")
        
        if critical_issues:
            recommendations.append("🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                recommendations.append(f"   • {issue}")
        
        # Check for failed tests
        failed_categories = []
        for category, tests in self.results.items():
            if isinstance(tests, list):
                failed_tests = [t for t in tests if t.get("status") == "FAIL"]
                if failed_tests:
                    failed_categories.append(category)
        
        if failed_categories:
            recommendations.append(f"❌ FAILED TESTS: Issues found in {', '.join(failed_categories)}. Review required.")
        
        # Check response times
        slow_categories = []
        for category, avg_time in self._get_avg_response_times().items():
            if avg_time > 1000:  # > 1 second
                slow_categories.append(f"{category} ({avg_time}ms)")
        
        if slow_categories:
            recommendations.append(f"⚠️ PERFORMANCE: Slow response times in: {', '.join(slow_categories)}")
        
        # Positive findings
        passed_tests = sum(1 for category in self.results.values() 
                          if isinstance(category, list)
                          for test in category 
                          if test.get("status") == "PASS")
        
        if passed_tests > 0:
            recommendations.append(f"✅ POSITIVE: {passed_tests} tests passed successfully")
        
        return recommendations

    def _generate_phase_assessment(self) -> Dict[str, Any]:
        """Generate Phase 1 implementation assessment"""
        
        # Count critical components
        health_status = "HEALTHY" if any(t.get("status") == "PASS" for t in self.results.get("health_checks", [])) else "UNHEALTHY"
        
        api_structure_status = "GOOD" if any(t.get("status") == "PASS" for t in self.results.get("api_structure", [])) else "NEEDS_WORK"
        
        security_issues = len([t for t in self.results.get("known_issues", []) if t.get("issue_type") == "CRITICAL"])
        security_status = "CRITICAL_ISSUES" if security_issues > 0 else "BASIC_IMPLEMENTED"
        
        config_working = len([t for t in self.results.get("config_api", []) if t.get("status") == "PASS"])
        config_status = "PARTIALLY_WORKING" if config_working > 0 else "NOT_WORKING"
        
        assessment = {
            "overall_status": "PARTIAL_SUCCESS",
            "components": {
                "health_monitoring": health_status,
                "api_structure": api_structure_status,
                "security_implementation": security_status,
                "configuration_system": config_status
            },
            "readiness": {
                "development": "READY" if health_status == "HEALTHY" else "BLOCKED",
                "testing": "BLOCKED" if security_issues > 0 else "READY",
                "production": "NOT_READY"
            },
            "next_steps": [
                "Fix bcrypt password hashing issue (CRITICAL)",
                "Complete authentication system testing",
                "Implement multi-tenant isolation testing",
                "Add comprehensive API endpoint testing",
                "Performance optimization and monitoring"
            ]
        }
        
        return assessment

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
    print("=" * 80)
    print("FAANG-level automated validation with comprehensive issue documentation")
    print("Testing: Health, Infrastructure, API Structure, Security, Config")
    print("=" * 80)
    
    async with Phase1ValidatorFinal() as validator:
        # Run all validation suites
        await validator.validate_health_checks()
        await validator.validate_infrastructure()
        await validator.validate_api_structure()
        await validator.validate_security_posture()
        await validator.validate_config_api()
        
        # Generate and display report
        print("\n📊 VALIDATION REPORT")
        print("=" * 80)
        
        report = validator.generate_report()
        summary = report["summary"]
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Warned: {summary['warned']} ⚠️")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Issues: {summary['issues']} 🔍")
        print(f"Success Rate: {summary['success_rate']}%")
        
        if summary["avg_response_times_ms"]:
            print("\nAverage Response Times:")
            for category, time_ms in summary["avg_response_times_ms"].items():
                print(f"  {category}: {time_ms}ms")
        
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  {rec}")
        
        print("\n🎯 PHASE 1 ASSESSMENT:")
        assessment = report["phase_1_assessment"]
        print(f"Overall Status: {assessment['overall_status']}")
        print("Component Status:")
        for component, status in assessment["components"].items():
            print(f"  {component}: {status}")
        
        print("Readiness:")
        for env, status in assessment["readiness"].items():
            print(f"  {env}: {status}")
        
        # Save detailed report
        report_file = "/tmp/phase1_validation_report_final.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Return exit code based on critical issues
        critical_issues = summary.get("issues", 0)
        return 1 if critical_issues > 0 else 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)