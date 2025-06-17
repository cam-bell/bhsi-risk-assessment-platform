from typing import List, Dict, Any
import google.generativeai as genai
from app.core.config import settings
from ..search.base_agent import BaseSearchAgent
from google.cloud import aiplatform
from config.gcp_config import VERTEX_AI_LOCATION, GEMINI_ENDPOINT_ID, PROJECT_ID


class GeminiAgent:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location=VERTEX_AI_LOCATION)
        
        # Get the endpoint
        self.endpoint = aiplatform.Endpoint(
            endpoint_name=f"projects/{PROJECT_ID}/locations/{VERTEX_AI_LOCATION}/endpoints/{GEMINI_ENDPOINT_ID}"
        )
        
        # Define risk assessment criteria
        self.risk_criteria = {
            "turnover": {
                "green": "Strong financial performance, consistent growth, positive revenue trends",
                "orange": "Moderate performance, some fluctuations, stable but not growing",
                "red": "Declining revenue, financial difficulties, poor performance"
            },
            "shareholding": {
                "green": "Stable ownership structure, transparent holdings, reputable shareholders",
                "orange": "Recent changes in ownership, some complexity in structure",
                "red": "Frequent ownership changes, complex/opaque structure, concerning shareholders"
            },
            "bankruptcy": {
                "green": "No bankruptcy history, strong financial position",
                "orange": "Past bankruptcy issues resolved, current stability",
                "red": "Recent bankruptcy, ongoing financial difficulties"
            },
            "legal": {
                "green": "Clean legal record, no significant cases",
                "orange": "Minor legal issues, resolved cases",
                "red": "Major ongoing legal cases, regulatory violations"
            },
            "corruption": {
                "green": "No corruption indicators, clean reputation",
                "orange": "Minor allegations, no convictions",
                "red": "Major corruption allegations or convictions"
            }
        }
    
    async def analyze_text(self, text: str, category: str) -> str:
        """
        Analyze text for a specific risk category using Gemini
        """
        if not self.api_key:
            raise ValueError("Gemini API key must be configured")
        
        prompt = f"""
        Analyze the following text for {category} risk assessment.
        Consider these criteria:
        {self.risk_criteria[category]}
        
        Text to analyze:
        {text}
        
        Based on the criteria, classify the risk level as either 'green', 'orange', or 'red'.
        Provide a brief explanation for your classification.
        """
        
        try:
            response = await self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error in Gemini analysis: {str(e)}")
            return "orange"  # Default to orange in case of errors
    
    async def analyze_search_results(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """
        Analyze search results for all risk categories
        """
        # Combine all search results into a single text
        combined_text = ""
        for agent_results in results.values():
            for result in agent_results:
                combined_text += f"Title: {result['title']}\n"
                combined_text += f"Snippet: {result['snippet']}\n"
                combined_text += f"Source: {result['source']}\n"
                combined_text += "---\n"
        
        # Analyze each category
        risk_scores = {}
        for category in self.risk_criteria.keys():
            risk_scores[category] = await self.analyze_text(combined_text, category)
        
        return risk_scores
    
    def determine_overall_risk(self, category_scores: Dict[str, str]) -> str:
        """
        Determine overall risk level based on individual category scores
        """
        # Count risk levels
        risk_counts = {"red": 0, "orange": 0, "green": 0}
        for score in category_scores.values():
            risk_counts[score] += 1
        
        # Determine overall risk
        if risk_counts["red"] >= 2:
            return "red"
        elif risk_counts["red"] == 1 or risk_counts["orange"] >= 2:
            return "orange"
        else:
            return "green" 