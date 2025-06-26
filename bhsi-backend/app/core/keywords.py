from typing import Dict, List, Set
import re

class KeywordManager:
    """Manages keyword detection for risk assessment"""
    
    def __init__(self):
        # Initialize keyword categories
        self.categories = {
            "corruption": {
                "es": {
                    "corrupción", "soborno", "fraude", "malversación", "cohecho",
                    "comisión ilícita", "conducta indebida", "extorsión", "colusión",
                    "abuso", "estafa", "engaño", "apropiación indebida", "amiguismo",
                    "pago ilícito", "lavado", "chantaje", "manipulación", "ética"
                },
                "en": {
                    "corruption", "bribery", "fraud", "embezzlement", "graft",
                    "kickback", "misconduct", "extortion", "collusion", "abuse",
                    "scam", "deception", "misappropriation", "cronyism", "payoff",
                    "laundering", "blackmail", "rigging", "ethics"
                }
            },
            "bankruptcy": {
                "es": {
                    "quiebra", "insolvencia", "concurso de acreedores", "liquidación",
                    "deuda", "incumplimiento", "deudor", "reestructuración",
                    "procedimiento concursal", "moratoria", "dificultad financiera"
                },
                "en": {
                    "bankruptcy", "insolvency", "creditors' meeting", "liquidation",
                    "debt", "default", "debtor", "restructuring", "bankruptcy proceedings",
                    "moratorium", "financial distress"
                }
            },
            "shareholding": {
                "es": {
                    "cambio de accionistas", "transferencia de acciones",
                    "tenencia de acciones", "compra de participaciones"
                },
                "en": {
                    "change shareholders", "share transfer", "shareholding",
                    "share purchase"
                }
            },
            "dismissal": {
                "es": {
                    "despido colectivo", "despido", "regulación de empleo",
                    "reducción de plantilla"
                },
                "en": {
                    "collective dismissal", "layoff", "employment regulation",
                    "workforce reduction"
                }
            },
            "environmental": {
                "es": {
                    "contaminación", "sostenibilidad", "emisiones",
                    "gestión de residuos", "impacto ambiental", "greenwashing"
                },
                "en": {
                    "pollution", "sustainability", "emissions", "waste management",
                    "environmental impact", "greenwashing"
                }
            }
        }
        
        # Compile regex patterns for each category
        self.patterns = {}
        for category, languages in self.categories.items():
            self.patterns[category] = {}
            for lang, keywords in languages.items():
                # Create pattern that matches whole words only
                pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
                self.patterns[category][lang] = re.compile(pattern, re.IGNORECASE | re.UNICODE)
    
    def detect_keywords(self, text: str, category: str = None, language: str = "es") -> Dict[str, List[str]]:
        """
        Detect keywords in text for specified category and language
        
        Args:
            text: Text to analyze
            category: Specific category to check (None for all)
            language: Language code ("es" or "en")
            
        Returns:
            Dict mapping categories to lists of found keywords
        """
        if not text:
            return {}
            
        results = {}
        categories_to_check = [category] if category else self.categories.keys()
        
        for cat in categories_to_check:
            if cat not in self.patterns:
                continue
                
            pattern = self.patterns[cat][language]
            matches = pattern.findall(text)
            
            if matches:
                results[cat] = list(set(matches))  # Remove duplicates
                
        return results
    
    def get_risk_level(self, text: str, language: str = "es") -> tuple[str, float]:
        """
        Determine risk level based on keyword matches
        
        Returns:
            Tuple of (risk_level, confidence)
        """
        matches = self.detect_keywords(text, language=language)
        
        # Count matches by category
        match_counts = {cat: len(keywords) for cat, keywords in matches.items()}
        
        # Risk scoring logic
        if "corruption" in match_counts and match_counts["corruption"] >= 2:
            return "High-Legal", 0.9
        elif "bankruptcy" in match_counts and match_counts["bankruptcy"] >= 2:
            return "High-Legal", 0.85
        elif "dismissal" in match_counts and match_counts["dismissal"] >= 2:
            return "Medium-Reg", 0.8
        elif "environmental" in match_counts and match_counts["environmental"] >= 2:
            return "Medium-Reg", 0.75
        elif any(count >= 1 for count in match_counts.values()):
            return "Low-Other", 0.6
            
        return "Low-Other", 0.5 