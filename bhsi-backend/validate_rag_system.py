#!/usr/bin/env python3
"""
BHSI RAG System Validation Script

Quick validation of the complete RAG system for thesis demonstration.
Validates all components and provides a go/no-go assessment.
"""

import requests
import json
import time
from datetime import datetime

class RAGSystemValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        self.results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        return passed
    
    def authenticate(self):
        """Test authentication"""
        print("\n🔐 Testing Authentication...")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": "admin@bhsi.com", "password": "admin123"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                return self.log_test("Authentication", True, f"Token received ({len(self.token)} chars)")
            else:
                return self.log_test("Authentication", False, f"Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Authentication", False, f"Error: {str(e)}")
    
    def test_rag_health(self):
        """Test RAG health endpoint"""
        print("\n🏥 Testing RAG Health...")
        
        if not self.token:
            return self.log_test("RAG Health", False, "No authentication token")
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/analysis/nlp/health",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                vector_status = data.get("vector_search_service", "unknown")
                gemini_status = data.get("gemini_service", "unknown")
                
                details = f"Overall: {status}, Vector: {vector_status}, Gemini: {gemini_status}"
                return self.log_test("RAG Health", status == "healthy", details)
            else:
                return self.log_test("RAG Health", False, f"Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("RAG Health", False, f"Error: {str(e)}")
    
    def test_rag_query(self):
        """Test actual RAG query"""
        print("\n🧠 Testing RAG Query...")
        
        if not self.token:
            return self.log_test("RAG Query", False, "No authentication token")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            query_data = {
                "question": "¿Cuáles son los principales riesgos regulatorios para los bancos españoles?",
                "max_documents": 5,
                "language": "es"
            }
            
            print("   Executing RAG query (may take 10-15 seconds)...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/v1/analysis/nlp/ask",
                json=query_data,
                headers=headers,
                timeout=60
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                sources = data.get("sources", [])
                confidence = data.get("confidence", 0)
                answer_length = len(data.get("answer", ""))
                
                details = f"{len(sources)} sources, {confidence}% confidence, {answer_length} chars, {duration:.1f}s"
                
                # Consider successful if we get sources and reasonable confidence
                success = len(sources) > 0 and confidence > 50
                return self.log_test("RAG Query", success, details)
            else:
                return self.log_test("RAG Query", False, f"Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("RAG Query", False, f"Error: {str(e)}")
    
    def test_cloud_services(self):
        """Test cloud service connectivity"""
        print("\n☁️ Testing Cloud Services...")
        
        services = {
            "Vector Search": "https://vector-search-185303190462.europe-west1.run.app/health",
            "Gemini Service": "https://gemini-service-185303190462.europe-west1.run.app/health",
            "Embedder Service": "https://embedder-service-185303190462.europe-west1.run.app/health"
        }
        
        all_healthy = True
        
        for service_name, health_url in services.items():
            try:
                response = requests.get(health_url, timeout=15)
                if response.status_code == 200:
                    self.log_test(f"{service_name} Health", True, "Service responding")
                else:
                    self.log_test(f"{service_name} Health", False, f"Status: {response.status_code}")
                    all_healthy = False
            except Exception as e:
                self.log_test(f"{service_name} Health", False, f"Error: {str(e)}")
                all_healthy = False
        
        return all_healthy
    
    def test_vector_storage(self):
        """Test vector storage status"""
        print("\n📊 Testing Vector Storage...")
        
        try:
            # Test vector search service stats
            response = requests.get(
                "https://vector-search-185303190462.europe-west1.run.app/stats",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                vector_count = data.get("vectors", {}).get("total", 0)
                company_count = data.get("vectors", {}).get("companies", 0)
                
                details = f"{vector_count} vectors, {company_count} companies"
                success = vector_count > 0
                return self.log_test("Vector Storage", success, details)
            else:
                return self.log_test("Vector Storage", False, f"Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Vector Storage", False, f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate final validation report"""
        print("\n" + "="*60)
        print("🎯 BHSI RAG SYSTEM VALIDATION REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["passed"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 SYSTEM STATUS:")
        if failed_tests == 0:
            print("✅ ALL SYSTEMS OPERATIONAL")
            print("✅ RAG system ready for thesis demonstration")
            print("✅ Cloud services healthy")
            print("✅ Vector storage active")
            print("✅ AI analysis working")
            print("\n🎉 SYSTEM READY FOR DEMONSTRATION!")
            
        elif failed_tests <= 2:
            print("⚠️  MOSTLY OPERATIONAL")
            print("⚠️  Minor issues detected")
            print("⚠️  May need attention before demo")
            
        else:
            print("❌ SYSTEM ISSUES DETECTED")
            print("❌ Multiple components failing")
            print("❌ Requires immediate attention")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "test_results": self.results
        }
        
        with open("rag_validation_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: rag_validation_report.json")
        print(f"⏰ Validation completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return failed_tests == 0

def main():
    """Main validation runner"""
    print("🚀 BHSI RAG SYSTEM VALIDATION")
    print("="*50)
    print("Testing all components for thesis demonstration readiness...")
    print()
    
    validator = RAGSystemValidator()
    
    # Run all validation tests
    tests = [
        validator.authenticate,
        validator.test_rag_health,
        validator.test_cloud_services,
        validator.test_vector_storage,
        validator.test_rag_query
    ]
    
    # Execute tests sequentially
    for test in tests:
        test()
    
    # Generate final report
    success = validator.generate_report()
    
    if success:
        print("\n🎊 CONGRATULATIONS!")
        print("Your RAG system is fully operational and ready for thesis demonstration!")
        return 0
    else:
        print("\n⚠️  Please address the failing components before demonstration.")
        return 1

if __name__ == "__main__":
    exit(main()) 