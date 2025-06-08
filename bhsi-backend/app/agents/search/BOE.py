import re, requests, sqlite3, datetime, lxml.etree as ET
import json

# Load spaCy with error handling
try:
    import spacy
    nlp = spacy.load("es_core_news_lg")
except ImportError:
    print("Warning: spaCy not installed. Entity extraction will be disabled.")
    print("To install: pip install spacy && python -m spacy download es_core_news_lg")
    nlp = None
except OSError:
    print("Warning: Spanish spaCy model 'es_core_news_lg' not found.")
    print("To install: python -m spacy download es_core_news_lg")
    nlp = None

BANKRUPTCY = re.compile(r"concurso|insolven", re.I)
SEVERE_SECTIONS = {"JUS", "CNMC", "AEPD"}      # extend as needed

def fetch_boe_summary(date_str):
    """Fetch BOE summary for a given date"""
    url = f"https://boe.es/datosabiertos/api/boe/sumario/{date_str}"
    r = requests.get(url, headers={"Accept": "application/json"})
    r.raise_for_status()
    return r.json()["data"]["sumario"]

def iter_items(summary):
    """Iterate through all items in the BOE summary structure"""
    if isinstance(summary, dict):
        # Handle different possible structures in BOE API response
        if "diario" in summary:
            diario = summary["diario"]
            
            if isinstance(diario, dict) and "seccion" in diario:
                secciones = diario["seccion"]
                if isinstance(secciones, list):
                    for seccion in secciones:
                        yield from iter_items(seccion)
                else:
                    yield from iter_items(secciones)
            elif isinstance(diario, list):
                for item in diario:
                    yield from iter_items(item)
        
        elif "seccion" in summary:
            seccion = summary["seccion"]
            if isinstance(seccion, list):
                for item in seccion:
                    yield from iter_items(item)
            else:
                yield from iter_items(seccion)
        
        elif "departamento" in summary:
            departamentos = summary["departamento"]
            if isinstance(departamentos, list):
                for dept in departamentos:
                    yield from iter_items(dept)
            else:
                yield from iter_items(departamentos)
        
        elif "epigrafe" in summary:
            epigrafes = summary["epigrafe"]
            if isinstance(epigrafes, list):
                for epi in epigrafes:
                    yield from iter_items(epi)
            else:
                yield from iter_items(epigrafes)
        
        elif "item" in summary:
            items = summary["item"]
            if isinstance(items, list):
                for item in items:
                    yield item
            else:
                yield items
        
        else:
            # If it's an individual item with required fields
            if "titulo" in summary and ("url_xml" in summary or "identificador" in summary):
                yield summary
    
    elif isinstance(summary, list):
        for item in summary:
            yield from iter_items(item)

def tag_risk(item):
    # fast triage using section and title
    s = item.get("seccion_codigo", "")
    t = item.get("titulo", "")
    if s in SEVERE_SECTIONS or BANKRUPTCY.search(t):
        return "High-Legal"
    return "Low"

def full_text(item):
    if "url_xml" not in item:
        return item.get("texto", "")
    
    xml = requests.get(item["url_xml"]).content
    root = ET.fromstring(xml)
    return " ".join(root.itertext())

def entities(text):
    if nlp:
        return [ent.text for ent in nlp(text).ents if ent.label_ in {"ORG","PER"}]
    else:
        return []

def search_boe_for_company(company_name, date_str=None):
    """Search BOE for mentions of a specific company"""
    if date_str is None:
        date_str = datetime.date.today().strftime("%Y%m%d")
    
    try:
        summary = fetch_boe_summary(date_str)
        results = []
        
        for item in iter_items(summary):
            # Check if company name appears in title or text
            title = item.get("titulo", "").lower()
            if company_name.lower() in title:
                risk = tag_risk(item)
                text = full_text(item)
                ents = entities(text)
                
                results.append({
                    "identificador": item.get("identificador", "Unknown"),
                    "titulo": item.get("titulo", ""),
                    "risk_level": risk,
                    "entities": ents[:10],  # Top 10 entities
                    "url": item.get("url_html", ""),
                    "seccion": item.get("seccion_codigo", "")
                })
        
        return results
    
    except Exception as e:
        print(f"Error searching BOE for {company_name}: {e}")
        return []

# Main execution for testing
if __name__ == "__main__":
    try:
        date = datetime.date.today().strftime("%Y%m%d")
        print(f"Processing BOE summary for {date}")
        
        summary = fetch_boe_summary(date)
        
        processed_count = 0
        high_risk_count = 0
        
        for itm in iter_items(summary):
            processed_count += 1
            risk = tag_risk(itm)
            if risk != "Low":
                high_risk_count += 1
                try:
                    text = full_text(itm)
                    ents = entities(text)
                    print(f"{itm.get('identificador', 'Unknown')}: {risk} - Entities: {ents[:5]}")
                except Exception as e:
                    print(f"Error processing {itm.get('identificador', 'Unknown')}: {e}")
        
        print(f"Processed {processed_count} items total, {high_risk_count} high-risk items found")
        
    except Exception as e:
        print(f"Error fetching or processing BOE data: {e}")
        import traceback
        traceback.print_exc()
