import { rest } from "msw";

// Mock data generators
const generateMockSearchResults = (companyName: string) => {
  const spanishCompanies = [
    "Banco Santander",
    "BBVA",
    "CaixaBank",
    "Banco Sabadell",
    "Bankia",
    "Iberdrola",
    "Telefónica",
    "Repsol",
    "Inditex",
    "Ferrovial",
    "ACS",
    "Abertis",
    "Endesa",
    "Gas Natural",
    "Mapfre",
  ];

  const riskKeywords = [
    "multa",
    "sanción",
    "investigación",
    "irregularidad",
    "fraude",
    "quiebra",
    "concurso",
    "liquidación",
    "auditoría",
    "inspección",
  ];

  const sources = [
    "BOE",
    "News",
    "El País",
    "Expansión",
    "El Mundo",
    "ABC",
    "La Vanguardia",
  ];

  const results = [];

  // Generate 5-15 results
  const numResults = Math.floor(Math.random() * 11) + 5;

  for (let i = 0; i < numResults; i++) {
    const source = sources[Math.floor(Math.random() * sources.length)];
    const riskKeyword =
      riskKeywords[Math.floor(Math.random() * riskKeywords.length)];
    const randomCompany =
      spanishCompanies[Math.floor(Math.random() * spanishCompanies.length)];

    const result = {
      source: source,
      date: new Date(
        Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000
      ).toISOString(),
      title: `${randomCompany} enfrenta ${riskKeyword} regulatorio`,
      summary: `La empresa ${randomCompany} se enfrenta a un nuevo desafío regulatorio relacionado con ${riskKeyword}. Los analistas consideran que esto podría afectar su valoración en el mercado.`,
      risk_level:
        Math.random() > 0.7
          ? "High-Legal"
          : Math.random() > 0.4
          ? "Medium-Reg"
          : "Low-Other",
      confidence: Math.random() * 0.5 + 0.5, // 0.5 to 1.0
      url: `https://example.com/article-${i + 1}`,
      author: ["Redacción", "Agencias", "Carlos López", "María García"][
        Math.floor(Math.random() * 4)
      ],
      source_name: source,
      category: ["Economía", "Empresas", "Mercados", "Regulación"][
        Math.floor(Math.random() * 4)
      ],
    };

    // Add BOE-specific fields
    if (source === "BOE") {
      result.identificador = `BOE-A-2024-${
        Math.floor(Math.random() * 9000) + 1000
      }`;
      result.seccion = ["I", "II", "III", "IV", "V"][
        Math.floor(Math.random() * 5)
      ];
      result.seccion_nombre = "Disposiciones Generales";
    }

    results.push(result);
  }

  return results;
};

const generateMockAnalytics = (companyName: string) => {
  return {
    company_name: companyName,
    risk_assessment: {
      turnover:
        Math.random() > 0.6 ? "green" : Math.random() > 0.3 ? "orange" : "red",
      shareholding:
        Math.random() > 0.6 ? "green" : Math.random() > 0.3 ? "orange" : "red",
      bankruptcy:
        Math.random() > 0.7 ? "green" : Math.random() > 0.4 ? "orange" : "red",
      legal:
        Math.random() > 0.5 ? "green" : Math.random() > 0.2 ? "orange" : "red",
      corruption:
        Math.random() > 0.8 ? "green" : Math.random() > 0.5 ? "orange" : "red",
      overall:
        Math.random() > 0.6 ? "green" : Math.random() > 0.3 ? "orange" : "red",
    },
    analysis_summary: `Análisis completo de ${companyName} realizado con datos de múltiples fuentes. Se han identificado varios factores de riesgo que requieren atención.`,
    trends: {
      risk_trend: "increasing",
      recent_events: Math.floor(Math.random() * 10) + 1,
      high_risk_events: Math.floor(Math.random() * 5),
    },
  };
};

export const handlers = [
  // Legacy score endpoint
  rest.get("/api/v1/score", (req, res, ctx) => {
    const query = req.url.searchParams.get("query");

    return res(
      ctx.delay(800),
      ctx.json({
        company:
          query && query.toUpperCase().includes("ACME")
            ? "ACME S.A."
            : `${query} S.A.`,
        vat:
          query && query.toUpperCase().includes("ESX") ? query : "ESX1234567",
        overall: "orange",
        blocks: {
          turnover: "green",
          shareholding: "orange",
          bankruptcy: "green",
          legal: "red",
        },
      })
    );
  }),

  // Main search endpoint
  rest.post("/api/v1/search", async (req, res, ctx) => {
    const body = await req.json();
    const { company_name } = body;

    const results = generateMockSearchResults(company_name);

    return res(
      ctx.delay(1500),
      ctx.json({
        company_name: company_name,
        search_date: new Date().toISOString(),
        date_range: {
          start: body.start_date || null,
          end: body.end_date || null,
          days_back: body.days_back || 7,
        },
        results: results,
        metadata: {
          total_results: results.length,
          boe_results: results.filter((r) => r.source === "BOE").length,
          news_results: results.filter((r) => r.source === "News").length,
          elpais_results: results.filter((r) => r.source === "El País").length,
          expansion_results: results.filter((r) => r.source === "Expansión")
            .length,
          elmundo_results: results.filter((r) => r.source === "El Mundo")
            .length,
          abc_results: results.filter((r) => r.source === "ABC").length,
          lavanguardia_results: results.filter(
            (r) => r.source === "La Vanguardia"
          ).length,
          elconfidencial_results: results.filter(
            (r) => r.source === "El Confidencial"
          ).length,
          high_risk_results: results.filter(
            (r) => r.risk_level === "High-Legal"
          ).length,
          sources_searched: body.include_boe ? ["boe"] : [],
        },
        performance: {
          total_time_seconds: "2.45",
          search_time_seconds: "1.23",
          classification_time_seconds: "1.22",
          keyword_efficiency: "95.7%",
          llm_usage: "4.3%",
        },
      })
    );
  }),

  // Streamlined search endpoint
  rest.post("/api/v1/streamlined/search", async (req, res, ctx) => {
    const body = await req.json();
    const { company_name } = body;

    const results = generateMockSearchResults(company_name);

    return res(
      ctx.delay(1200),
      ctx.json({
        company_name: company_name,
        search_date: new Date().toISOString(),
        date_range: {
          start: body.start_date || null,
          end: body.end_date || null,
          days_back: body.days_back || 7,
        },
        results: results,
        metadata: {
          total_results: results.length,
          boe_results: results.filter((r) => r.source === "BOE").length,
          news_results: results.filter((r) => r.source === "News").length,
          rss_results: results.filter((r) => r.source.startsWith("RSS-"))
            .length,
          high_risk_results: results.filter(
            (r) => r.risk_level === "High-Legal"
          ).length,
          sources_searched: body.include_boe ? ["boe"] : [],
        },
        performance: {
          total_time_seconds: "1.85",
          search_time_seconds: "0.95",
          classification_time_seconds: "0.90",
          keyword_efficiency: "97.2%",
          llm_usage: "2.8%",
          optimization: "Streamlined search + optimized hybrid classifier",
        },
      })
    );
  }),

  // Company analytics endpoint
  rest.get("/api/v1/companies/:companyName/analytics", (req, res, ctx) => {
    const { companyName } = req.params;
    const analytics = generateMockAnalytics(companyName as string);

    return res(
      ctx.delay(1000),
      ctx.json({
        company_name: companyName,
        risk_assessment: analytics.risk_assessment,
        analysis_summary: analytics.analysis_summary,
        trends: analytics.trends,
        processed_results: {
          google_results: "[]",
          bing_results: "[]",
          gov_results: "[]",
          news_results: "[]",
        },
      })
    );
  }),

  // Company analysis endpoint
  rest.post("/api/v1/companies/analyze", async (req, res, ctx) => {
    const body = await req.json();
    const { name } = body;
    const analytics = generateMockAnalytics(name);

    return res(
      ctx.delay(2000),
      ctx.json({
        company_name: name,
        risk_assessment: analytics.risk_assessment,
        analysis_summary: analytics.analysis_summary,
        trends: analytics.trends,
        processed_results: {
          google_results: "[]",
          bing_results: "[]",
          gov_results: "[]",
          news_results: "[]",
        },
      })
    );
  }),

  // Search health endpoint
  rest.get("/api/v1/search/health", (req, res, ctx) => {
    return res(
      ctx.delay(300),
      ctx.json({
        status: "healthy",
        message: "Search services operational",
        orchestrator_type: "MockSearchOrchestrator",
        classifier_type: "OptimizedHybridClassifier",
        features: [
          "Ultra-fast search across multiple sources",
          "Optimized hybrid classification",
          "Intelligent rate limit handling",
          "Performance monitoring",
        ],
        sources_available: [
          "BOE (Spanish Official Gazette)",
          "NewsAPI (International news)",
          "RSS feeds (Spanish news sources)",
        ],
      })
    );
  }),

  // Search performance endpoint
  rest.get("/api/v1/search/performance", (req, res, ctx) => {
    return res(
      ctx.delay(200),
      ctx.json({
        status: "success",
        message:
          "Performance statistics for OPTIMIZED STREAMLINED search system",
        architecture: {
          search_stage: "Streamlined agents - Fast data fetching only",
          classification_stage_1:
            "Optimized keyword gate (µ-seconds) - 90%+ efficiency",
          classification_stage_2:
            "Smart LLM routing (only for truly ambiguous cases)",
          optimization: "Removed classification loops + optimized patterns",
        },
        statistics: {
          keyword_efficiency: "95.7%",
          llm_usage: "4.3%",
          avg_processing_time_ms: 45,
          total_documents_processed: 1250,
        },
        improvements: {
          search_optimization: "No classification during search loops",
          keyword_patterns: "Enhanced patterns for Spanish D&O risks",
          smart_routing: "Only legal-looking ambiguous content sent to LLM",
          expected_performance: "90%+ improvement over previous system",
        },
      })
    );
  }),

  // Analytics health endpoint
  rest.get("/api/v1/companies/analytics/health", (req, res, ctx) => {
    return res(
      ctx.delay(300),
      ctx.json({
        status: "healthy",
        services: {
          analytics_engine: "operational",
          data_processing: "operational",
          risk_assessment: "operational",
        },
        uptime: "99.8%",
        last_check: new Date().toISOString(),
      })
    );
  }),

  // System status endpoint
  rest.get("/api/v1/companies/system/status", (req, res, ctx) => {
    return res(
      ctx.delay(400),
      ctx.json({
        status: "operational",
        system_type: "BHSI Risk Assessment System",
        performance: {
          response_time_avg: "1.2s",
          throughput: "150 requests/min",
          error_rate: "0.1%",
        },
        components: {
          search_engine: "healthy",
          classification_engine: "healthy",
          analytics_engine: "healthy",
          database: "healthy",
        },
      })
    );
  }),

  // Risk trends endpoint
  rest.get("/api/v1/companies/analytics/trends", (req, res, ctx) => {
    return res(
      ctx.delay(800),
      ctx.json({
        trends: {
          overall_risk_trend: "increasing",
          high_risk_companies: 15,
          medium_risk_companies: 42,
          low_risk_companies: 128,
          total_companies_assessed: 185,
        },
        recent_events: [
          {
            company: "Banco Santander",
            event_type: "regulatory_investigation",
            risk_level: "high",
            date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          },
          {
            company: "BBVA",
            event_type: "legal_proceeding",
            risk_level: "medium",
            date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          },
        ],
        sector_analysis: {
          banking: { risk_level: "high", trend: "increasing" },
          energy: { risk_level: "medium", trend: "stable" },
          telecommunications: { risk_level: "low", trend: "decreasing" },
        },
      })
    );
  }),

  // Company comparison endpoint
  rest.get("/api/v1/companies/analytics/comparison", (req, res, ctx) => {
    const companies = req.url.searchParams.get("companies")?.split(",") || [];

    const comparison_data = companies.map((company) => ({
      company_name: company.trim(),
      risk_assessment: {
        turnover:
          Math.random() > 0.6
            ? "green"
            : Math.random() > 0.3
            ? "orange"
            : "red",
        shareholding:
          Math.random() > 0.6
            ? "green"
            : Math.random() > 0.3
            ? "orange"
            : "red",
        bankruptcy:
          Math.random() > 0.7
            ? "green"
            : Math.random() > 0.4
            ? "orange"
            : "red",
        legal:
          Math.random() > 0.5
            ? "green"
            : Math.random() > 0.2
            ? "orange"
            : "red",
        overall:
          Math.random() > 0.6
            ? "green"
            : Math.random() > 0.3
            ? "orange"
            : "red",
      },
      recent_events: Math.floor(Math.random() * 10) + 1,
      risk_score: Math.floor(Math.random() * 100),
    }));

    return res(
      ctx.delay(1200),
      ctx.json({
        comparison_data: comparison_data,
        summary: {
          highest_risk: comparison_data.reduce((max, curr) =>
            curr.risk_score > max.risk_score ? curr : max
          ),
          lowest_risk: comparison_data.reduce((min, curr) =>
            curr.risk_score < min.risk_score ? curr : min
          ),
          average_risk_score:
            comparison_data.reduce((sum, curr) => sum + curr.risk_score, 0) /
            comparison_data.length,
        },
      })
    );
  }),

  // Management summary endpoint
  rest.post("/api/v1/analysis/management-summary", async (req, res, ctx) => {
    const body = await req.json();
    const { company_name } = body;

    // Add a mock classification_results array
    const classification_results = [
      {
        title: "Investigación regulatoria",
        summary: "La empresa está bajo investigación por la CNMV.",
        risk_level: "High-Legal",
        confidence: 0.92,
        method: "keyword_high_legal",
        date: new Date().toISOString(),
        source: "BOE",
      },
      // ...add more mock results as needed
    ];

    return res(
      ctx.delay(2500),
      ctx.json({
        company_name: company_name,
        classification_results, // <-- required field
        summary: {
          executive_summary: `Análisis ejecutivo completo de ${company_name}. Se han identificado varios factores de riesgo que requieren atención inmediata del consejo de administración.`,
          key_risks: [
            "Riesgo regulatorio alto debido a investigaciones en curso",
            "Exposición a litigios por prácticas comerciales",
            "Vulnerabilidades en gobernanza corporativa",
          ],
          recommendations: [
            "Reforzar el departamento de compliance",
            "Revisar políticas de gobernanza",
            "Implementar auditorías internas adicionales",
          ],
          risk_score: Math.floor(Math.random() * 100),
          confidence_level: "85%",
        },
        detailed_analysis: {
          regulatory_risks: "Alto",
          legal_risks: "Medio",
          operational_risks: "Bajo",
          financial_risks: "Medio",
        },
      })
    );
  }),
];
