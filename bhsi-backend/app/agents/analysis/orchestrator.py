from typing import Dict, Any, List
from .gemini_agent import GeminiAgent
from .processor import DataProcessor
from app.models.company import RiskLevel


class AnalysisOrchestrator:
    def __init__(self):
        self.gemini_agent = GeminiAgent()
        self.data_processor = DataProcessor()
    
    async def analyze_company(self, search_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Perform complete company analysis
        """
        # Process raw search results
        processed_results = self.data_processor.process_search_results(search_results)
        
        # Get Gemini's analysis
        gemini_scores = await self.gemini_agent.analyze_search_results(search_results)
        
        # Determine overall risk
        overall_risk = self.gemini_agent.determine_overall_risk(gemini_scores)
        
        # Combine results
        analysis = {
            "risk_scores": {
                "turnover": gemini_scores.get("turnover", "orange"),
                "shareholding": gemini_scores.get("shareholding", "orange"),
                "bankruptcy": gemini_scores.get("bankruptcy", "orange"),
                "legal": gemini_scores.get("legal", "orange"),
                "corruption": gemini_scores.get("corruption", "orange"),
                "overall": overall_risk
            },
            "processed_results": processed_results,
            "analysis_summary": {
                "total_sources": len(search_results),
                "total_findings": processed_results["summary"]["total_results"],
                "date_range": processed_results["summary"]["date_range"],
                "key_findings": processed_results["summary"]["key_findings"]
            }
        }
        
        return analysis
    
    def format_for_database(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format analysis results for database storage
        """
        # Format the processed results
        formatted_results = self.data_processor.format_for_storage(analysis["processed_results"])
        
        # Add risk scores
        formatted_results.update({
            "turnover": analysis["risk_scores"]["turnover"],
            "shareholding": analysis["risk_scores"]["shareholding"],
            "bankruptcy": analysis["risk_scores"]["bankruptcy"],
            "legal": analysis["risk_scores"]["legal"],
            "corruption": analysis["risk_scores"]["corruption"],
            "overall": analysis["risk_scores"]["overall"]
        })
        
        return formatted_results 