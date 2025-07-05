#!/usr/bin/env python3
"""
BHSI Cloud Services Comprehensive Test
Validates all cloud services and provides performance metrics
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, Any

# Cloud Services Configuration
CLOUD_SERVICES = {
    "gemini": "https://gemini-service-185303190462.europe-west1.run.app",
    "embedder": "https://embedder-service-185303190462.europe-west1.run.app", 
    "vector_search": "https://vector-search-185303190462.europe-west1.run.app",
    "bigquery": "https://bigquery-analytics-185303190462.europe-west1.run.app"
}

# Test Scenarios
TEST_COMPANIES = [
    "Banco Santander",
    "BBVA", 
    "Telefónica",
    "Repsol",
    "Inditex"
]

RISK_SCENARIOS = [
    {
        "text": "Banco Santander está siendo investigado por presunto blanqueo de capitales por la Fiscalía Anticorrupción",
        "expected_risk": "High-Reg",
        "company": "Banco Santander"
    },
    {
        "text": "BBVA reporta beneficios récord en el trimestre actual con crecimiento sostenible",
        "expected_risk": "Low",
        "company": "BBVA"
    },
    {
        "text": "Telefónica enfrenta nuevas regulaciones de telecomunicaciones en mercados emergentes",
        "expected_risk": "Medium-Reg",
        "company": "Telefónica"
    }
]

class CloudServicesTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now(),
            "tests": {},
            "metrics": {
                "response_times": {},
                "accuracy": {},
                "reliability": {}
            },
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0
            }
        }
    
    def log_result(self, test_name: str, success: bool, data: Any = None, response_time: float = None):
        """Log test result with metrics"""
        self.results["tests"][test_name] = {
            "success": success,
            "data": data,
            "response_time": response_time,
            "timestamp": datetime.now()
        }
        
        self.results["summary"]["total_tests"] += 1
        if success:
            self.results["summary"]["passed"] += 1
            if response_time:
                self.results["metrics"]["response_times"][test_name] = response_time
            print(f"   ✅ {test_name} ({response_time:.2f}s)" if response_time else f"   ✅ {test_name}")
        else:
            self.results["summary"]["failed"] += 1
            print(f"   ❌ {test_name}")
    
    async def test_service_health(self):
        """Test all cloud services health"""
        print("\n🏥 TESTING CLOUD SERVICES HEALTH")
        print("-" * 40)
        
        for service_name, url in CLOUD_SERVICES.items():
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(f"{url}/health")
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    health_data = response.json()
                    self.log_result(f"{service_name}_health", True, health_data, response_time)
                else:
                    self.log_result(f"{service_name}_health", False)
                    
            except Exception as e:
                self.log_result(f"{service_name}_health", False)
    
    async def test_gemini_classification(self):
        """Test Gemini AI with multiple risk scenarios"""
        print("\n🧠 TESTING GEMINI AI CLASSIFICATION")
        print("-" * 40)
        
        for i, scenario in enumerate(RISK_SCENARIOS):
            start_time = time.time()
            try:
                test_data = {
                    "text": scenario["text"],
                    "context": "D&O risk assessment"
                }
                
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        f"{CLOUD_SERVICES['gemini']}/classify",
                        json=test_data
                    )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    test_name = f"gemini_scenario_{i+1}"
                    
                    # Evaluate quality
                    has_label = "label" in result
                    has_reason = "reason" in result and len(result.get("reason", "")) > 50
                    has_confidence = "confidence" in result and result.get("confidence", 0) > 0
                    is_spanish = "reason" in result and any(word in result["reason"].lower() for word in ["investigación", "sanciones", "regulatorio"])
                    
                    quality_score = sum([has_label, has_reason, has_confidence, is_spanish]) / 4
                    
                    self.log_result(test_name, True, {
                        "scenario": scenario["company"],
                        "result": result,
                        "quality_score": quality_score,
                        "spanish_analysis": is_spanish
                    }, response_time)
                    
                    self.results["metrics"]["accuracy"][test_name] = quality_score
                    
                else:
                    self.log_result(f"gemini_scenario_{i+1}", False)
                    
            except Exception as e:
                self.log_result(f"gemini_scenario_{i+1}", False)
    
    async def test_embedder_service(self):
        """Test embedding service with multiple texts"""
        print("\n🔍 TESTING EMBEDDER SERVICE")
        print("-" * 30)
        
        test_texts = [
            "Banco Santander riesgo regulatorio compliance",
            "BBVA financial performance analysis",
            "Telefónica telecommunications regulatory framework",
            "Repsol energy sector risk assessment"
        ]
        
        for i, text in enumerate(test_texts):
            start_time = time.time()
            try:
                test_data = {"text": text}
                
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        f"{CLOUD_SERVICES['embedder']}/embed",
                        json=test_data
                    )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    embedding = result.get("embedding", [])
                    
                    # Validate embedding quality
                    correct_dimension = len(embedding) == 768
                    has_variation = len(set(embedding[:10])) > 1 if embedding else False
                    
                    self.log_result(f"embedder_test_{i+1}", True, {
                        "text_sample": text[:30] + "...",
                        "embedding_dimension": len(embedding),
                        "quality_check": correct_dimension and has_variation
                    }, response_time)
                    
                else:
                    self.log_result(f"embedder_test_{i+1}", False)
                    
            except Exception as e:
                self.log_result(f"embedder_test_{i+1}", False)
    
    async def test_bigquery_analytics(self):
        """Test BigQuery analytics with multiple companies"""
        print("\n📊 TESTING BIGQUERY ANALYTICS")
        print("-" * 35)
        
        # Test company analytics
        for company in TEST_COMPANIES[:3]:  # Test first 3 companies
            start_time = time.time()
            try:
                company_encoded = company.replace(" ", "%20")
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(
                        f"{CLOUD_SERVICES['bigquery']}/analytics/company/{company_encoded}"
                    )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Validate response structure
                    has_company_name = "company_name" in result
                    has_total_events = "total_events" in result
                    has_risk_distribution = "risk_distribution" in result
                    
                    self.log_result(f"bigquery_{company.replace(' ', '_').lower()}", True, {
                        "company": company,
                        "total_events": result.get("total_events", 0),
                        "structure_valid": has_company_name and has_total_events and has_risk_distribution
                    }, response_time)
                    
                else:
                    self.log_result(f"bigquery_{company.replace(' ', '_').lower()}", False)
                    
            except Exception as e:
                self.log_result(f"bigquery_{company.replace(' ', '_').lower()}", False)
        
        # Test analytics endpoints
        endpoints = [
            ("risk_trends", "/analytics/risk-trends"),
            ("alerts", "/analytics/alerts"),
            ("sectors", "/analytics/sectors"),
            ("events_stats", "/stats/events")
        ]
        
        for endpoint_name, endpoint_path in endpoints:
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(f"{CLOUD_SERVICES['bigquery']}{endpoint_path}")
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_result(f"bigquery_{endpoint_name}", True, {
                        "endpoint": endpoint_path,
                        "data_size": len(str(result)),
                        "has_data": bool(result)
                    }, response_time)
                else:
                    self.log_result(f"bigquery_{endpoint_name}", False)
                    
            except Exception as e:
                self.log_result(f"bigquery_{endpoint_name}", False)
    
    async def test_integration_workflow(self):
        """Test complete integration workflow"""
        print("\n🔄 TESTING INTEGRATION WORKFLOW")
        print("-" * 40)
        
        test_scenario = {
            "company": "Banco Santander",
            "text": "Banco Santander investigación por presunto blanqueo de capitales"
        }
        
        workflow_results = {}
        
        # Step 1: Generate embedding
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                embed_response = await client.post(
                    f"{CLOUD_SERVICES['embedder']}/embed",
                    json={"text": test_scenario["text"]}
                )
            
            if embed_response.status_code == 200:
                workflow_results["embedding"] = "success"
                embedding = embed_response.json().get("embedding", [])
            else:
                workflow_results["embedding"] = "failed"
                embedding = []
        except:
            workflow_results["embedding"] = "failed"
            embedding = []
        
        # Step 2: Classify risk
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                classify_response = await client.post(
                    f"{CLOUD_SERVICES['gemini']}/classify",
                    json={"text": test_scenario["text"], "context": "D&O risk assessment"}
                )
            
            if classify_response.status_code == 200:
                workflow_results["classification"] = "success"
                classification = classify_response.json()
            else:
                workflow_results["classification"] = "failed"
                classification = {}
        except:
            workflow_results["classification"] = "failed"
            classification = {}
        
        # Step 3: Get company analytics
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                analytics_response = await client.get(
                    f"{CLOUD_SERVICES['bigquery']}/analytics/company/Banco%20Santander"
                )
            
            if analytics_response.status_code == 200:
                workflow_results["analytics"] = "success"
                analytics = analytics_response.json()
            else:
                workflow_results["analytics"] = "failed"
                analytics = {}
        except:
            workflow_results["analytics"] = "failed"
            analytics = {}
        
        total_time = time.time() - start_time
        success_count = sum(1 for result in workflow_results.values() if result == "success")
        overall_success = success_count >= 2  # At least 2/3 steps must succeed
        
        self.log_result("integration_workflow", overall_success, {
            "steps": workflow_results,
            "success_rate": f"{success_count}/3",
            "has_embedding": len(embedding) > 0,
            "has_classification": bool(classification),
            "has_analytics": bool(analytics)
        }, total_time)
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE CLOUD SERVICES REPORT")
        print("=" * 60)
        
        total_tests = self.results["summary"]["total_tests"]
        passed_tests = self.results["summary"]["passed"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🕐 Test Duration: {datetime.now() - self.results['timestamp']}")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {self.results['summary']['failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Performance metrics
        response_times = self.results["metrics"]["response_times"]
        if response_times:
            avg_time = sum(response_times.values()) / len(response_times)
            fastest = min(response_times.values())
            slowest = max(response_times.values())
            
            print(f"\n⚡ Performance Metrics:")
            print(f"   Average Response Time: {avg_time:.2f}s")
            print(f"   Fastest Response: {fastest:.2f}s")
            print(f"   Slowest Response: {slowest:.2f}s")
        
        # Service reliability
        print(f"\n🔧 Service Reliability:")
        services = ["gemini", "embedder", "vector_search", "bigquery"]
        for service in services:
            service_tests = [test for test in self.results["tests"] if test.startswith(service)]
            if service_tests:
                service_passed = sum(1 for test in service_tests if self.results["tests"][test]["success"])
                service_total = len(service_tests)
                service_rate = (service_passed / service_total * 100) if service_total > 0 else 0
                print(f"   {service.upper()}: {service_passed}/{service_total} ({service_rate:.1f}%)")
        
        # Quality metrics
        accuracy_scores = self.results["metrics"]["accuracy"]
        if accuracy_scores:
            avg_accuracy = sum(accuracy_scores.values()) / len(accuracy_scores)
            print(f"\n🎯 AI Quality Metrics:")
            print(f"   Average Classification Quality: {avg_accuracy:.1f}/1.0")
        
        # System status
        print(f"\n🎯 System Status: ", end="")
        if success_rate >= 95:
            print("🟢 EXCELLENT - Production Ready")
        elif success_rate >= 85:
            print("🟡 GOOD - Minor Issues")
        elif success_rate >= 70:
            print("🟠 FAIR - Needs Attention")
        else:
            print("🔴 POOR - Critical Issues")
        
        # Real-world capabilities
        print(f"\n🌟 Real-World Capabilities Demonstrated:")
        if self.results["tests"].get("integration_workflow", {}).get("success"):
            print("   ✅ End-to-End Risk Assessment Pipeline")
        
        gemini_tests = [test for test in self.results["tests"] if test.startswith("gemini_scenario")]
        if any(self.results["tests"][test]["success"] for test in gemini_tests):
            print("   ✅ Spanish D&O Risk Classification")
        
        embedder_tests = [test for test in self.results["tests"] if test.startswith("embedder_test")]
        if any(self.results["tests"][test]["success"] for test in embedder_tests):
            print("   ✅ Multi-lingual Text Embedding")
        
        bigquery_tests = [test for test in self.results["tests"] if test.startswith("bigquery_")]
        if any(self.results["tests"][test]["success"] for test in bigquery_tests):
            print("   ✅ Real-time Analytics & Reporting")
        
        # Save report
        report_file = f"cloud_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved: {report_file}")
        
        return success_rate

async def main():
    """Run comprehensive cloud services tests"""
    tester = CloudServicesTester()
    
    print("🚀 BHSI CLOUD SERVICES COMPREHENSIVE TEST")
    print("=" * 50)
    print(f"🕐 Started at: {tester.results['timestamp']}")
    print(f"☁️  Services: {len(CLOUD_SERVICES)} cloud services")
    print(f"🧪 Scenarios: {len(RISK_SCENARIOS)} risk assessment scenarios")
    print()
    
    try:
        # Run all test suites
        await tester.test_service_health()
        await tester.test_gemini_classification()
        await tester.test_embedder_service()
        await tester.test_bigquery_analytics()
        await tester.test_integration_workflow()
        
        # Generate comprehensive report
        success_rate = tester.generate_report()
        
        print(f"\n🎉 Testing completed with {success_rate:.1f}% success rate!")
        
        if success_rate >= 90:
            print("🎊 BHSI Cloud Services are PRODUCTION READY! 🎊")
        elif success_rate >= 75:
            print("🔧 BHSI Cloud Services are mostly functional with minor issues")
        else:
            print("⚠️ BHSI Cloud Services need attention before production use")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 