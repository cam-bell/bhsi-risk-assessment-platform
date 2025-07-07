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
            "financial": {
                "es": {
                    "quiebra", "insolvencia", "concurso de acreedores", "liquidación",
                    "deuda", "incumplimiento", "deudor", "reestructuración",
                    "procedimiento concursal", "moratoria", "dificultad financiera",
                    "pérdidas", "caída de beneficios", "reducción de ingresos",
                    "problemas de liquidez", "crisis financiera"
                },
                "en": {
                    "bankruptcy", "insolvency", "creditors' meeting", "liquidation",
                    "debt", "default", "debtor", "restructuring", "bankruptcy proceedings",
                    "moratorium", "financial distress", "losses", "profit decline",
                    "revenue reduction", "liquidity problems", "financial crisis"
                }
            },
            "shareholding": {
                "es": {
                    "cambio de accionistas", "transferencia de acciones",
                    "tenencia de acciones", "compra de participaciones",
                    "venta de participaciones", "nuevo accionista",
                    "modificación del capital social", "ampliación de capital"
                },
                "en": {
                    "change shareholders", "share transfer", "shareholding",
                    "share purchase", "share sale", "new shareholder",
                    "capital modification", "capital increase"
                }
            },
            "regulatory": {
                "es": {
                    "sanción", "multa", "expediente sancionador", "infracción",
                    "cnmv", "banco de españa", "cnmc", "aepd", "dgsfp",
                    "sepblac", "requerimiento", "advertencia", "apercibimiento",
                    "incumplimiento normativo", "violación regulatoria"
                },
                "en": {
                    "sanction", "fine", "penalty", "violation", "regulatory breach",
                    "compliance failure", "regulatory warning", "regulatory notice",
                    "regulatory investigation", "regulatory action"
                }
            },
            "dismissals": {
                "es": {
                    "despido colectivo", "despido", "regulación de empleo",
                    "reducción de plantilla", "expediente de regulación",
                    "ere", "despido disciplinario", "cese de empleados",
                    "reestructuración laboral", "despido improcedente"
                },
                "en": {
                    "collective dismissal", "layoff", "employment regulation",
                    "workforce reduction", "redundancy", "disciplinary dismissal",
                    "employee termination", "labor restructuring", "unfair dismissal"
                }
            },
            "environmental": {
                "es": {
                    "contaminación", "sostenibilidad", "emisiones",
                    "gestión de residuos", "impacto ambiental", "greenwashing",
                    "multa ambiental", "sanción ecológica", "daño ambiental",
                    "vertido", "emisiones co2", "cambio climático"
                },
                "en": {
                    "pollution", "sustainability", "emissions", "waste management",
                    "environmental impact", "greenwashing", "environmental fine",
                    "ecological sanction", "environmental damage", "spill",
                    "co2 emissions", "climate change"
                }
            },
            "operational": {
                "es": {
                    "nombramiento", "cese", "dimisión", "renuncia", "junta general",
                    "consejo de administración", "director", "gerente", "fusión",
                    "adquisición", "venta", "reestructuración", "cambio de sede",
                    "nuevo proyecto", "expansión", "cierre", "apertura"
                },
                "en": {
                    "appointment", "dismissal", "resignation", "board meeting",
                    "board of directors", "director", "manager", "merger",
                    "acquisition", "sale", "restructuring", "headquarters change",
                    "new project", "expansion", "closure", "opening"
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
        
        # Risk scoring logic with new categories
        if "corruption" in match_counts and match_counts["corruption"] >= 2:
            return "High-Legal", 0.9
        elif "financial" in match_counts and match_counts["financial"] >= 2:
            return "High-Financial", 0.85
        elif "regulatory" in match_counts and match_counts["regulatory"] >= 2:
            return "High-Regulatory", 0.85
        elif "dismissals" in match_counts and match_counts["dismissals"] >= 2:
            return "Medium-Operational", 0.8
        elif "environmental" in match_counts and match_counts["environmental"] >= 2:
            return "Medium-Operational", 0.75
        elif "operational" in match_counts and match_counts["operational"] >= 2:
            return "Low-Operational", 0.7
        elif any(count >= 1 for count in match_counts.values()):
            return "Low-Other", 0.6
            
        return "Low-Other", 0.5 