import axios from "axios";

export interface WikidataCompanyInfo {
  founded?: string;
  employees?: string;
  revenue?: string;
  headquarters?: string;
}

export async function fetchWikidataCompanyInfo(
  companyName: string
): Promise<WikidataCompanyInfo | null> {
  const endpoint = "https://query.wikidata.org/sparql";
  const query = `
    SELECT ?founded ?employees ?revenue ?hqLabel WHERE {
      ?company rdfs:label "${companyName}"@en;
              wdt:P31 wd:Q4830453.
      OPTIONAL { ?company wdt:P571 ?founded. }
      OPTIONAL { ?company wdt:P1128 ?employees. }
      OPTIONAL { ?company wdt:P2139 ?revenue. }
      OPTIONAL { ?company wdt:P159 ?hq. }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    LIMIT 1
  `;
  const url = `${endpoint}?query=${encodeURIComponent(query)}&format=json`;

  try {
    const res = await axios.get(url, {
      headers: { Accept: "application/sparql-results+json" },
    });
    const bindings = res.data.results.bindings[0];
    if (!bindings) return null;
    return {
      founded: bindings.founded?.value?.split("T")[0],
      employees: bindings.employees?.value,
      revenue: bindings.revenue?.value,
      headquarters: bindings.hqLabel?.value,
    };
  } catch (e) {
    console.error("Wikidata fetch error:", e);
    return null;
  }
}
