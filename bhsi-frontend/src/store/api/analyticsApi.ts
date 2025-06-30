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
}

export interface ManagementSummaryResponse {
  company_name: string;
  summary: {
    executive_summary: string;
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
  };
  generated_at: string;
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

// Define the analytics API slice
export const analyticsApi = createApi({
  reducerPath: "analyticsApi",
  baseQuery: axiosBaseQuery({
    baseUrl:
      import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  }),
  tagTypes: [
    "Analytics",
    "ManagementSummary",
    "RiskTrends",
    "CompanyComparison",
  ],
  endpoints: (builder) => ({
    // Get comprehensive analytics for a company
    getCompanyAnalytics: builder.query<
      CompanyAnalyticsResponse,
      CompanyAnalyticsRequest
    >({
      query: ({
        company_name,
        include_trends = true,
        include_sectors = false,
      }) => ({
        url: `/companies/${encodeURIComponent(company_name)}/analytics`,
        method: "GET",
        params: { include_trends, include_sectors },
      }),
      providesTags: (result, error, { company_name }) => [
        { type: "Analytics", id: company_name },
      ],
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
  }),
});

// Export hooks for usage in functional components
export const {
  useGetCompanyAnalyticsQuery,
  useGetRiskTrendsQuery,
  useCompareCompaniesQuery,
  useGetManagementSummaryMutation,
  useGetAnalyticsHealthQuery,
  useGetSystemStatusQuery,
} = analyticsApi;
