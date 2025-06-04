from typing import List, Dict, Any
import json
from datetime import datetime
from app.models.company import RiskLevel


class DataProcessor:
    def __init__(self):
        self.keywords = {
            "turnover": {
                "green": ["growth", "increase", "profit", "revenue", "success", "positive"],
                "orange": ["stable", "maintain", "moderate", "consistent"],
                "red": ["decline", "loss", "decrease", "negative", "struggle", "difficulty"]
            },
            "shareholding": {
                "green": ["stable", "transparent", "reputable", "established"],
                "orange": ["change", "restructure", "reorganize"],
                "red": ["complex", "opaque", "controversial", "questionable"]
            },
            "bankruptcy": {
                "green": ["solvent", "profitable", "healthy"],
                "orange": ["recovery", "restructure", "rebound"],
                "red": ["bankruptcy", "insolvent", "liquidation", "default"]
            },
            "legal": {
                "green": ["compliance", "clean", "approved"],
                "orange": ["investigation", "review", "pending"],
                "red": ["lawsuit", "violation", "penalty", "sanction"]
            },
            "corruption": {
                "green": ["transparent", "ethical", "compliance"],
                "orange": ["allegation", "investigation", "review"],
                "red": ["corruption", "bribery", "fraud", "conviction"]
            }
        }
    
    def process_search_results(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Process and classify search results
        """
        processed_results = {
            "raw_results": results,
            "classified_results": self._classify_results(results),
            "summary": self._generate_summary(results),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return processed_results
    
    def _classify_results(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Classify results by risk category
        """
        classified = {
            "turnover": [],
            "shareholding": [],
            "bankruptcy": [],
            "legal": [],
            "corruption": []
        }
        
        for agent_name, agent_results in results.items():
            for result in agent_results:
                # Combine title and snippet for analysis
                text = f"{result['title']} {result['snippet']}".lower()
                
                # Classify by category
                for category in classified.keys():
                    if self._matches_category(text, category):
                        classified[category].append(result)
        
        return classified
    
    def _matches_category(self, text: str, category: str) -> bool:
        """
        Check if text matches any keywords in a category
        """
        for risk_level, keywords in self.keywords[category].items():
            if any(keyword in text for keyword in keywords):
                return True
        return False
    
    def _generate_summary(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Generate a summary of the search results
        """
        summary = {
            "total_results": sum(len(agent_results) for agent_results in results.values()),
            "sources": list(results.keys()),
            "date_range": self._get_date_range(results),
            "key_findings": self._extract_key_findings(results)
        }
        
        return summary
    
    def _get_date_range(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """
        Get the date range of the results
        """
        dates = []
        for agent_results in results.values():
            for result in agent_results:
                if result.get("timestamp"):
                    try:
                        dates.append(datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00")))
                    except (ValueError, TypeError):
                        continue
        
        if dates:
            return {
                "start": min(dates).isoformat(),
                "end": max(dates).isoformat()
            }
        return {"start": None, "end": None}
    
    def _extract_key_findings(self, results: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """
        Extract key findings from the results
        """
        findings = []
        for agent_results in results.values():
            for result in agent_results:
                # Add significant findings based on content
                if any(keyword in result["title"].lower() for keyword in ["bankruptcy", "lawsuit", "corruption", "fraud"]):
                    findings.append(f"Significant finding: {result['title']}")
        
        return findings[:5]  # Return top 5 findings
    
    def format_for_storage(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format results for database storage
        """
        return {
            "google_results": json.dumps(processed_results["raw_results"].get("GoogleSearchAgent", [])),
            "bing_results": json.dumps(processed_results["raw_results"].get("BingSearchAgent", [])),
            "gov_results": json.dumps(processed_results["raw_results"].get("SpanishGovAgent", [])),
            "news_results": json.dumps(processed_results["raw_results"].get("NewsAgencyAgent", [])),
            "analysis_summary": json.dumps(processed_results["summary"])
        } 