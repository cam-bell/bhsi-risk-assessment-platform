import { createApi } from "@reduxjs/toolkit/query/react";
import { axiosBaseQuery } from "./axiosBaseQuery";

// Types for analytics API
export interface CompanyAnalyticsRequest {
  company_name: string;
  include_trends?: boolean;
  include_sectors?: boolean;
}

export interface CompanyAnalyticsResponse {
  company_name: string;
  risk_profile: {
    overall: "green" | "orange" | "red";
    legal: "green" | "orange" | "red";
    bankruptcy: "green" | "orange" | "red";
    corruption: "green" | "orange" | "red";
  };
  trends: {
    risk_trend: "increasing" | "decreasing" | "stable";
    recent_events: number;
    historical_comparison: {
      current_period: number;
      previous_period: number;
      change_percentage: number;
    };
  };
  sector_analysis?: {
    sector: string;
    sector_risk: "green" | "orange" | "red";
    company_rank: number;
    total_companies: number;
  };
  recent_events: Array<{
    date: string;
    type: string;
    description: string;
    risk_level: "green" | "orange" | "red";
  }>;
}

export interface RiskTrendsResponse {
  system_wide_trends: {
    overall_risk_distribution: {
      green: number;
      orange: number;
      red: number;
    };
    risk_trends_over_time: Array<{
      date: string;
      green_count: number;
      orange_count: number;
      red_count: number;
    }>;
    top_risk_factors: Array<{
      factor: string;
      frequency: number;
      percentage: number;
    }>;
  };
  sector_insights: Array<{
    sector: string;
    average_risk: "green" | "orange" | "red";
    risk_distribution: {
      green: number;
      orange: number;
      red: number;
    };
  }>;
}

export interface CompanyComparisonRequest {
  companies: string[];
}

export interface CompanyComparisonResponse {
  comparison_data: Array<{
    company_name: string;
    risk_profile: {
      overall: "green" | "orange" | "red";
      legal: "green" | "orange" | "red";
      bankruptcy: "green" | "orange" | "red";
      corruption: "green" | "orange" | "red";
    };
    risk_score: number;
    recent_events: number;
    trend: "increasing" | "decreasing" | "stable";
  }>;
  comparative_analysis: {
    highest_risk: string;
    lowest_risk: string;
    most_volatile: string;
    risk_correlation: number;
  };
}

export interface ManagementSummaryRequest {
  company_name: string;
  classification_results?: any[]; // Allow sending classified results
  language?: string; // Add language toggle support
}

export interface ManagementSummaryResponse {
  company_name: string;
  overall_risk: string;
  executive_summary: string;
  risk_breakdown: Record<
    string,
    {
      level: string;
      reasoning: string;
      evidence: string[];
      confidence: number;
    }
  >;
  key_findings: string[];
  recommendations: string[];
  generated_at: string;
  method: string;
  key_risks: Array<{
    risk_type: string;
    description: string;
    severity: "low" | "medium" | "high";
    recommendations: string[];
  }>;
  financial_health: {
    status: "healthy" | "concerning" | "critical";
    indicators: Array<{
      indicator: string;
      value: string;
      status: "positive" | "neutral" | "negative";
    }>;
  };
  compliance_status: {
    overall: "compliant" | "partial" | "non_compliant";
    areas: Array<{
      area: string;
      status: "compliant" | "partial" | "non_compliant";
      details: string;
    }>;
  };
}

export interface AnalyticsHealthResponse {
  status: "healthy" | "unhealthy";
  services: {
    bigquery: "healthy" | "unhealthy";
    analytics_service: "healthy" | "unhealthy";
    cache: "healthy" | "unhealthy";
  };
  timestamp: string;
  error?: string;
}

// RAG Chatbot Types
export interface RAGQueryRequest {
  question: string;
  max_documents?: number;
  company_filter?: string;
  language?: string;
}

export interface RAGDocumentSource {
  id: string;
  score: number;
  title: string;
  company: string;
  date: string;
  source: string;
  text_preview: string;
}

export interface RAGAnalysisResponse {
  question: string;
  answer: string;
  sources: RAGDocumentSource[];
  confidence: number;
  methodology: string;
  response_time_ms: number;
  timestamp: string;
}

export interface RAGExamplesResponse {
  spanish_examples: string[];
  english_examples: string[];
  tips: string[];
}

export interface RAGHealthResponse {
  rag_orchestrator: string;
  vector_search_service: string;
  gemini_service: string;
  status: string;
  timestamp: string;
}

// Define the analytics API slice
export const analyticsApi = createApi({
  reducerPath: "analyticsApi",
  baseQuery: axiosBaseQuery({
    baseUrl: "https://bhsi-backend-485249399569.europe-west1.run.app/api/v1",
  }),
  tagTypes: [
    "Analytics",
    "ManagementSummary",
    "RiskTrends",
    "CompanyComparison",
    "RAG",
  ],
  endpoints: (builder) => ({
    // Get management summary for a company
    getManagementSummary: builder.mutation<
      ManagementSummaryResponse,
      ManagementSummaryRequest
    >({
      query: (body) => ({
        url: "/analysis/management-summary",
        method: "POST",
        data: body,
      }),
      invalidatesTags: ["ManagementSummary"],
    }),

    // Get system-wide risk trends
    getRiskTrends: builder.query<RiskTrendsResponse, void>({
      query: () => ({
        url: "/companies/analytics/trends",
        method: "GET",
      }),
      providesTags: ["RiskTrends"],
    }),

    // Compare multiple companies
    compareCompanies: builder.query<
      CompanyComparisonResponse,
      CompanyComparisonRequest
    >({
      query: ({ companies }) => ({
        url: "/companies/analytics/comparison",
        method: "GET",
        params: { companies: companies.join(",") },
      }),
      providesTags: ["CompanyComparison"],
    }),

    // Health check for analytics services
    getAnalyticsHealth: builder.query<AnalyticsHealthResponse, void>({
      query: () => ({
        url: "/companies/analytics/health",
        method: "GET",
      }),
      providesTags: ["Analytics"],
    }),

    // Get system status
    getSystemStatus: builder.query<any, void>({
      query: () => ({
        url: "/companies/system/status",
        method: "GET",
      }),
      providesTags: ["Analytics"],
    }),

    // RAG Chatbot endpoints
    askRAGQuestion: builder.mutation<RAGAnalysisResponse, RAGQueryRequest>({
      query: (body) => ({
        url: "/analysis/nlp/ask",
        method: "POST",
        data: body,
      }),
      invalidatesTags: ["RAG"],
    }),

    getRAGExamples: builder.query<RAGExamplesResponse, void>({
      query: () => ({
        url: "/analysis/nlp/examples",
        method: "GET",
      }),
      providesTags: ["RAG"],
    }),

    getRAGHealth: builder.query<RAGHealthResponse, void>({
      query: () => ({
        url: "/analysis/nlp/health",
        method: "GET",
      }),
      providesTags: ["RAG"],
    }),
  }),
});

// Export hooks for usage in functional components
export const {
  useGetManagementSummaryMutation,
  useGetRiskTrendsQuery,
  useCompareCompaniesQuery,
  useGetAnalyticsHealthQuery,
  useGetSystemStatusQuery,
  useAskRAGQuestionMutation,
  useGetRAGExamplesQuery,
  useGetRAGHealthQuery,
} = analyticsApi;
