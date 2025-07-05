#!/usr/bin/env python3
"""
BHSI Corporate Risk Assessment - Comprehensive End-to-End Test Suite
Tests all endpoints, cloud services, and system integration
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import traceback

# Configuration
BASE_URL = "http://localhost:8000"
CLOUD_SERVICES = {
    "gemini": "https://gemini-service-185303190462.europe-west1.run.app",
    "embedder": "https://embedder-service-185303190462.europe-west1.run.app", 
    "vector_search": "https://vector-search-185303190462.europe-west1.run.app",
    "bigquery": "https://bigquery-analytics-185303190462.europe-west1.run.app"
}

# Test data
TEST_COMPANIES = [
    "Banco Santander",
    "BBVA",
    "Telefónica", 
    "Repsol",
    "Inditex"
]

TEST_SCENARIOS = [
    {
        "company_name": "Banco Santander",
        "description": "Major Spanish bank with regulatory history",
        "search_terms": ["blanqueo capitales", "investigación", "sanción"],
        "expected_risk": "Medium-High"
    },
    {
        "company_name": "BBVA", 
        "description": "Another major Spanish bank",
        "search_terms": ["compliance", "regulatorio", "BCE"],
        "expected_risk": "Medium"
    }
]

class EndToEndTester:
    def __init__(self):
        self.results = {
            "start_time": datetime.now(),
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
        self.client = None
    
    async def setup(self):
        """Initialize test environment"""
        print("🚀 BHSI END-TO-END TEST SUITE")
        print("=" * 60)
        print(f"🕐 Started at: {self.results['start_time']}")
        print(f"🎯 Base URL: {BASE_URL}")
        print(f"☁️  Cloud Services: {len(CLOUD_SERVICES)} configured")
        print()
        
        # Check if backend is running
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{BASE_URL}/health")
                if response.status_code == 200:
                    print("✅ Backend server is running")
                else:
                    print("❌ Backend server not responding")
                    return False
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            print("💡 Please start the backend server: python main.py")
            return False
        
        self.client = httpx.AsyncClient(timeout=60)
        return True
    
    async def cleanup(self):
        """Cleanup test environment"""
        if self.client:
            await self.client.aclose()
    
    def log_test(self, test_name: str, success: bool, data: Any = None, error: str = None):
        """Log test result"""
        self.results["tests"][test_name] = {
            "success": success,
            "timestamp": datetime.now(),
            "data": data,
            "error": error
        }
        self.results["summary"]["total_tests"] += 1
        if success:
            self.results["summary"]["passed"] += 1
            print(f"   ✅ {test_name}")
        else:
            self.results["summary"]["failed"] += 1
            self.results["summary"]["errors"].append(f"{test_name}: {error}")
            print(f"   ❌ {test_name}: {error}")
    
    async def test_cloud_services(self):
        """Test all cloud services health and functionality"""
        print("\n🔍 Testing Cloud Services")
        print("-" * 30)
        
        for service_name, url in CLOUD_SERVICES.items():
            try:
                start_time = time.time()
                
                # Health check
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(f"{url}/health")
                    
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    health_data = response.json()
                    self.log_test(f"cloud_{service_name}_health", True, {
                        "response_time": response_time,
                        "health_data": health_data
                    })
                    
                    # Test specific functionality for each service
                    if service_name == "gemini":
                        await self.test_gemini_classification()
                    elif service_name == "embedder":
                        await self.test_embedder_service()
                    elif service_name == "bigquery":
                        await self.test_bigquery_analytics()
                        
                else:
                    self.log_test(f"cloud_{service_name}_health", False, 
                                error=f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"cloud_{service_name}_health", False, 
                            error=str(e))
    
    async def test_gemini_classification(self):
        """Test Gemini AI classification"""
        try:
            test_data = {
                "text": "Banco Santander está siendo investigado por presunto blanqueo de capitales",
                "context": "D&O risk assessment"
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{CLOUD_SERVICES['gemini']}/classify", 
                    json=test_data
                )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("gemini_classification", True, result)
            else:
                self.log_test("gemini_classification", False, 
                            error=f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("gemini_classification", False, error=str(e))
    
    async def test_embedder_service(self):
        """Test text embedding service"""
        try:
            test_data = {"text": "Banco Santander riesgo regulatorio"}
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{CLOUD_SERVICES['embedder']}/embed", 
                    json=test_data
                )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("embedder_service", True, {
                    "embedding_dimension": len(result.get("embedding", [])),
                    "has_embedding": "embedding" in result
                })
            else:
                self.log_test("embedder_service", False, 
                            error=f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("embedder_service", False, error=str(e))
    
    async def test_bigquery_analytics(self):
        """Test BigQuery analytics endpoints"""
        endpoints = [
            "/analytics/company/Banco%20Santander",
            "/analytics/risk-trends", 
            "/analytics/alerts",
            "/analytics/sectors",
            "/stats/events"
        ]
        
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(f"{CLOUD_SERVICES['bigquery']}{endpoint}")
                
                test_name = f"bigquery_{endpoint.split('/')[-1]}"
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test(test_name, True, {
                        "endpoint": endpoint,
                        "data_size": len(str(result)),
                        "has_data": bool(result)
                    })
                else:
                    self.log_test(test_name, False, 
                                error=f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(test_name, False, error=str(e))
    
    async def test_api_endpoints(self):
        """Test all backend API endpoints"""
        print("\n🔗 Testing API Endpoints")
        print("-" * 25)
        
        # Test health endpoint
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            self.log_test("api_health", response.status_code == 200, response.json())
        except Exception as e:
            self.log_test("api_health", False, error=str(e))
        
        # Test management summary endpoint
        await self.test_management_summary()
        
        # Test company analysis endpoints
        await self.test_company_analysis()
        
        # Test analytics endpoints
        await self.test_analytics_endpoints()
        
        # Test search endpoints
        await self.test_search_endpoints()
    
    async def test_management_summary(self):
        """Test management summary generation"""
        test_data = {
            "company_name": "Banco Santander",
            "classification_results": [
                {
                    "source": "news",
                    "risk_level": "Medium-Reg",
                    "confidence": 0.7,
                    "evidence": "Investigación por blanqueo de capitales"
                }
            ],
            "include_evidence": True,
            "language": "es"
        }
        
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/v1/analysis/management-summary", 
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("management_summary", True, {
                    "has_executive_summary": "executive_summary" in result,
                    "has_key_findings": "key_findings" in result,
                    "language": "spanish" in result.get("executive_summary", "").lower()
                })
            else:
                self.log_test("management_summary", False, 
                            error=f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("management_summary", False, error=str(e))
    
    async def test_company_analysis(self):
        """Test company analysis endpoints"""
        
        # Test company creation/retrieval
        for company in TEST_COMPANIES[:2]:  # Test first 2 companies
            try:
                # Test company analysis
                test_data = {
                    "company_name": company,
                    "search_depth": "basic",
                    "include_financial": True
                }
                
                response = await self.client.post(
                    f"{BASE_URL}/api/v1/companies/analyze", 
                    json=test_data
                )
                
                test_name = f"company_analysis_{company.replace(' ', '_').lower()}"
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    self.log_test(test_name, True, {
                        "company": company,
                        "has_results": bool(result),
                        "analysis_id": result.get("analysis_id")
                    })
                else:
                    self.log_test(test_name, False, 
                                error=f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(test_name, False, error=str(e))
    
    async def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        endpoints = [
            f"/api/v1/companies/{TEST_COMPANIES[0].replace(' ', '%20')}/analytics",
            "/api/v1/companies/analytics/trends",
            "/api/v1/companies/analytics/comparison", 
            "/api/v1/companies/analytics/health"
        ]
        
        for endpoint in endpoints:
            try:
                response = await self.client.get(f"{BASE_URL}{endpoint}")
                
                test_name = f"analytics_{endpoint.split('/')[-1]}"
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test(test_name, True, {
                        "endpoint": endpoint,
                        "has_data": bool(result)
                    })
                else:
                    self.log_test(test_name, False, 
                                error=f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(test_name, False, error=str(e))
    
    async def test_search_endpoints(self):
        """Test search endpoints"""
        search_data = {
            "company_name": "Banco Santander",
            "search_terms": ["riesgo", "regulatorio"],
            "sources": ["news", "government"],
            "max_results": 10
        }
        
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/v1/search/streamlined", 
                json=search_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("search_streamlined", True, {
                    "total_results": len(result.get("results", [])),
                    "sources_used": list(result.get("sources", {}).keys())
                })
            else:
                self.log_test("search_streamlined", False, 
                            error=f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("search_streamlined", False, error=str(e))
    
    async def test_integration_scenarios(self):
        """Test complete integration scenarios"""
        print("\n🔄 Testing Integration Scenarios")
        print("-" * 33)
        
        for scenario in TEST_SCENARIOS:
            await self.test_full_workflow(scenario)
    
    async def test_full_workflow(self, scenario: Dict[str, Any]):
        """Test complete end-to-end workflow for a company"""
        company_name = scenario["company_name"]
        test_name = f"workflow_{company_name.replace(' ', '_').lower()}"
        
        try:
            workflow_results = {}
            
            # Step 1: Search for company information
            search_data = {
                "company_name": company_name,
                "search_terms": scenario["search_terms"],
                "sources": ["news", "government"],
                "max_results": 5
            }
            
            search_response = await self.client.post(
                f"{BASE_URL}/api/v1/search/streamlined", 
                json=search_data
            )
            
            if search_response.status_code == 200:
                workflow_results["search"] = "success"
            else:
                workflow_results["search"] = f"failed: {search_response.status_code}"
            
            # Step 2: Analyze company
            analysis_data = {
                "company_name": company_name,
                "search_depth": "comprehensive"
            }
            
            analysis_response = await self.client.post(
                f"{BASE_URL}/api/v1/companies/analyze",
                json=analysis_data
            )
            
            if analysis_response.status_code in [200, 201]:
                workflow_results["analysis"] = "success"
                analysis_result = analysis_response.json()
            else:
                workflow_results["analysis"] = f"failed: {analysis_response.status_code}"
                analysis_result = {}
            
            # Step 3: Generate management summary
            summary_data = {
                "company_name": company_name,
                "classification_results": analysis_result.get("classification_results", []),
                "include_evidence": True
            }
            
            summary_response = await self.client.post(
                f"{BASE_URL}/api/v1/analysis/management-summary",
                json=summary_data
            )
            
            if summary_response.status_code == 200:
                workflow_results["summary"] = "success"
            else:
                workflow_results["summary"] = f"failed: {summary_response.status_code}"
            
            # Step 4: Get analytics
            analytics_response = await self.client.get(
                f"{BASE_URL}/api/v1/companies/{company_name.replace(' ', '%20')}/analytics"
            )
            
            if analytics_response.status_code == 200:
                workflow_results["analytics"] = "success"
            else:
                workflow_results["analytics"] = f"failed: {analytics_response.status_code}"
            
            # Evaluate overall workflow success
            success_count = sum(1 for result in workflow_results.values() if result == "success")
            total_steps = len(workflow_results)
            overall_success = success_count >= (total_steps * 0.75)  # 75% success rate
            
            self.log_test(test_name, overall_success, {
                "company": company_name,
                "steps": workflow_results,
                "success_rate": f"{success_count}/{total_steps}",
                "scenario": scenario["description"]
            })
            
        except Exception as e:
            self.log_test(test_name, False, error=str(e))
    
    async def generate_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = end_time - self.results["start_time"]
        
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        print(f"🕐 Duration: {duration}")
        print(f"📊 Total Tests: {self.results['summary']['total_tests']}")
        print(f"✅ Passed: {self.results['summary']['passed']}")
        print(f"❌ Failed: {self.results['summary']['failed']}")
        
        success_rate = (self.results['summary']['passed'] / 
                       self.results['summary']['total_tests'] * 100)
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Categorize test results
        categories = {
            "Cloud Services": [k for k in self.results["tests"].keys() if k.startswith("cloud_")],
            "API Endpoints": [k for k in self.results["tests"].keys() if k.startswith("api_") or k in ["management_summary", "search_streamlined"]],
            "Analytics": [k for k in self.results["tests"].keys() if k.startswith("analytics_") or k.startswith("bigquery_")],
            "Integration": [k for k in self.results["tests"].keys() if k.startswith("workflow_")]
        }
        
        print("\n📋 Results by Category:")
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for test in tests if self.results["tests"][test]["success"])
                total = len(tests)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"   {category}: {passed}/{total} ({rate:.1f}%)")
        
        # Show failed tests
        if self.results['summary']['errors']:
            print("\n❌ Failed Tests:")
            for error in self.results['summary']['errors']:
                print(f"   • {error}")
        
        # Performance metrics
        print("\n⚡ Performance Metrics:")
        cloud_response_times = []
        for test_name, test_data in self.results["tests"].items():
            if (test_name.startswith("cloud_") and test_data["success"] and 
                test_data["data"] and "response_time" in test_data["data"]):
                cloud_response_times.append(test_data["data"]["response_time"])
        
        if cloud_response_times:
            avg_response_time = sum(cloud_response_times) / len(cloud_response_times)
            print(f"   Average Cloud Response Time: {avg_response_time:.2f}s")
            print(f"   Fastest Response: {min(cloud_response_times):.2f}s")
            print(f"   Slowest Response: {max(cloud_response_times):.2f}s")
        
        # System health status
        print(f"\n🎯 System Status: ", end="")
        if success_rate >= 95:
            print("🟢 EXCELLENT - Production Ready")
        elif success_rate >= 85:
            print("🟡 GOOD - Minor Issues")
        elif success_rate >= 70:
            print("🟠 FAIR - Needs Attention")
        else:
            print("🔴 POOR - Critical Issues")
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved: {report_file}")
        
        return success_rate

async def main():
    """Run comprehensive end-to-end tests"""
    tester = EndToEndTester()
    
    try:
        # Setup
        if not await tester.setup():
            return
        
        # Run all test suites
        await tester.test_cloud_services()
        await tester.test_api_endpoints() 
        await tester.test_integration_scenarios()
        
        # Generate report
        success_rate = await tester.generate_report()
        
        print(f"\n🎉 Testing completed with {success_rate:.1f}% success rate!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 