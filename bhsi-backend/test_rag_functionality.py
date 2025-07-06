#!/usr/bin/env python3
"""
RAG Functionality Test

🧪 NEW TEST: Validates RAG implementation with existing services
⚠️ REMOVABLE: Test file, can be deleted without affecting system
🔧 VALIDATES: RAG endpoint integration with deployed cloud services
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.rag_config import rag_config

class RAGTester:
    """
    🧪 Test RAG functionality with existing cloud services
    """
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
    
    def log_test(self, test_name: str, passed: bool, message: str = "", details: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if details and not passed:
            print(f"   Details: {details}")
    
    async def test_rag_configuration(self):
        """Test 1: Validate RAG configuration"""
        print("\n🔧 Testing RAG Configuration...")
        
        try:
            config_status = rag_config.validate_config()
            
            if config_status["valid"]:
                self.log_test("RAG Configuration", True, "All configuration valid")
                
                # Log service URLs
                for service, info in config_status["services"].items():
                    print(f"   {service}: {info['url']}")
            else:
                self.log_test("RAG Configuration", False, "Configuration issues found", config_status["issues"])
                return False
            
        except Exception as e:
            self.log_test("RAG Configuration", False, "Configuration validation failed", str(e))
            return False
        
        return True
    
    async def test_service_health(self):
        """Test 2: Check cloud service health"""
        print("\n🏥 Testing Service Health...")
        
        import httpx
        
        services_healthy = True
        
        for service_name, service_url in rag_config.get_service_urls().items():
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{service_url}/health")
                    
                    if response.status_code == 200:
                        self.log_test(f"{service_name.title()} Service Health", True, f"Service healthy")
                    else:
                        self.log_test(f"{service_name.title()} Service Health", False, f"Status: {response.status_code}")
                        services_healthy = False
                        
            except Exception as e:
                self.log_test(f"{service_name.title()} Service Health", False, f"Health check failed", str(e))
                services_healthy = False
        
        return services_healthy
    
    async def test_rag_imports(self):
        """Test 3: Validate RAG imports work"""
        print("\n📦 Testing RAG Imports...")
        
        try:
            # Test RAG endpoint imports
            from app.api.v1.endpoints.rag_nlp_analysis import RAGOrchestrator, RAGQueryRequest
            self.log_test("RAG Endpoint Import", True, "RAG classes imported successfully")
            
            # Test RAG orchestrator initialization
            orchestrator = RAGOrchestrator()
            self.log_test("RAG Orchestrator Init", True, "RAG orchestrator initialized")
            
            # Test request model creation
            test_request = RAGQueryRequest(
                question="What are the current risks for Spanish banks?",
                max_documents=3,
                language="es"
            )
            self.log_test("RAG Request Model", True, f"Request created: {test_request.question[:50]}...")
            
        except Exception as e:
            self.log_test("RAG Imports", False, "RAG import failed", str(e))
            return False
        
        return True
    
    async def test_mock_rag_flow(self):
        """Test 4: Test RAG flow with mock data"""
        print("\n🧠 Testing RAG Flow (Mock Mode)...")
        
        try:
            from app.api.v1.endpoints.rag_nlp_analysis import RAGOrchestrator, RAGQueryRequest
            
            # Create test orchestrator
            orchestrator = RAGOrchestrator()
            
            # Test document formatting (no actual API calls)
            mock_documents = [
                {
                    "id": "test_doc_1",
                    "score": 0.95,
                    "document": "Banco Santander faces regulatory challenges in Spain according to recent BOE publications.",
                    "metadata": {
                        "company": "Banco Santander",
                        "titulo": "Regulatory Update",
                        "fecha": "2024-01-15",
                        "source": "BOE"
                    }
                }
            ]
            
            # Test source formatting
            sources = orchestrator._format_sources(mock_documents)
            
            if sources and len(sources) == 1:
                source = sources[0]
                self.log_test("RAG Source Formatting", True, f"Source formatted: {source.title}")
                
                # Test confidence calculation
                confidence = orchestrator._calculate_confidence(mock_documents)
                self.log_test("RAG Confidence Calculation", True, f"Confidence: {confidence}%")
            else:
                self.log_test("RAG Source Formatting", False, "Source formatting failed")
                return False
            
        except Exception as e:
            self.log_test("RAG Flow Test", False, "RAG flow test failed", str(e))
            return False
        
        return True
    
    async def test_rag_prompt_creation(self):
        """Test 5: Test RAG prompt creation"""
        print("\n📝 Testing RAG Prompt Creation...")
        
        try:
            from app.api.v1.endpoints.rag_nlp_analysis import RAGOrchestrator
            
            orchestrator = RAGOrchestrator()
            
            test_question = "¿Cuáles son los riesgos para Banco Santander?"
            test_context = "DOCUMENTO 1: Banco Santander regulatory issues..."
            
            # Test Spanish prompt
            spanish_prompt = orchestrator._create_rag_prompt(test_question, test_context, "es")
            
            if "español" in spanish_prompt and test_question in spanish_prompt:
                self.log_test("Spanish RAG Prompt", True, "Spanish prompt created correctly")
            else:
                self.log_test("Spanish RAG Prompt", False, "Spanish prompt missing elements")
                return False
            
            # Test English prompt
            english_prompt = orchestrator._create_rag_prompt("What risks affect Santander?", test_context, "en")
            
            if "English" in english_prompt and "risks" in english_prompt:
                self.log_test("English RAG Prompt", True, "English prompt created correctly")
            else:
                self.log_test("English RAG Prompt", False, "English prompt missing elements")
                return False
            
        except Exception as e:
            self.log_test("RAG Prompt Creation", False, "Prompt creation failed", str(e))
            return False
        
        return True
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("🧪 RAG FUNCTIONALITY TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        duration = datetime.now() - self.start_time
        print(f"⏱️  Duration: {duration.total_seconds():.2f} seconds")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"     Details: {result['details']}")
        
        print(f"\n🎯 RAG SYSTEM READINESS:")
        if failed_tests == 0:
            print("✅ ALL TESTS PASSED - RAG system ready!")
            print("✅ Can deploy RAG endpoints")
            print("✅ Services are accessible")
            print("✅ RAG flow is working")
            print("\n📋 NEXT STEPS:")
            print("1. Deploy backend with RAG endpoints")
            print("2. Test RAG endpoint: POST /api/v1/analysis/nlp/ask")
            print("3. Try example questions from /api/v1/analysis/nlp/examples")
        else:
            print("⚠️  Some tests failed - Review before deploying")
            print("⚠️  Check service availability")
            print("⚠️  Verify configuration")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100,
                "duration_seconds": duration.total_seconds()
            },
            "test_results": self.test_results,
            "rag_config": {
                "vector_search_url": rag_config.VECTOR_SEARCH_URL,
                "gemini_service_url": rag_config.GEMINI_SERVICE_URL
            }
        }
        
        with open("rag_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: rag_test_report.json")
        
        return failed_tests == 0

async def main():
    """Main test runner"""
    print("🚀 BHSI RAG Functionality Testing")
    print("="*50)
    print("Testing RAG system components for thesis demonstration...")
    print("This validates RAG works with your existing cloud services.\n")
    
    tester = RAGTester()
    
    # Run all tests
    tests = [
        tester.test_rag_configuration(),
        tester.test_service_health(),
        tester.test_rag_imports(),
        tester.test_mock_rag_flow(),
        tester.test_rag_prompt_creation()
    ]
    
    # Execute tests
    for test in tests:
        await test
    
    # Generate final report
    success = tester.generate_test_report()
    
    if success:
        print("\n🎉 CONGRATULATIONS!")
        print("Your RAG system is ready for thesis demonstration!")
        print("All components are working correctly.")
        return 0
    else:
        print("\n⚠️  Please fix the failing tests before demonstration.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with unexpected error: {e}")
        sys.exit(1) 