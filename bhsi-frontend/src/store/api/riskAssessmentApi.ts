import { createApi } from "@reduxjs/toolkit/query/react";
import { axiosBaseQuery } from "./axiosBaseQuery";

// Types for the actual API specification
export interface SearchRequest {
  company_name: string; // (required) The company to search for
  start_date?: string; // (optional, format: YYYY-MM-DD)
  end_date?: string; // (optional, format: YYYY-MM-DD)
  days_back?: number; // (optional, default: 7) If no dates, search last N days
  include_boe?: boolean; // (optional, default: true) Include BOE results
  include_news?: boolean; // (optional, default: true) Include NewsAPI results
}

export interface SearchResult {
  source: "News" | "BOE"; // "News" or "BOE"
  date: string; // Publication date (ISO format)
  title: string; // Article/document title
  summary: string | null; // Article summary/description (can be null)
  risk_level: string; // LLM or keyword-based risk label
  confidence: number; // Confidence score (0-1)
  url: string; // Link to the article or BOE document
  // BOE results may have additional fields like section, identificador, etc.
  section?: string; // BOE specific fields
  identificador?: string; // BOE specific fields
}

export interface SearchResponse {
  company_name: string; // Company name that was searched
  search_date: string; // ISO timestamp of the search
  date_range: {
    start: string | null; // Start date used for the search
    end: string | null; // End date used for the search
    days_back: number; // Days back used if no explicit dates
  };
  results: SearchResult[]; // Array of search results
}

// Legacy types for backward compatibility (can be removed later)
export interface RiskAssessmentRequest extends SearchRequest {
  companyName: string;
  vatNumber?: string;
  dataSource: "BOE" | "NewsAPI" | "both";
  dateRange?: {
    type: "preset" | "custom";
    daysBack?: number;
    startDate?: string;
    endDate?: string;
  };
}

export interface RiskAssessmentResponse {
  company: string;
  vat: string;
  overall: "green" | "orange" | "red";
  blocks: {
    turnover: "green" | "orange" | "red";
    shareholding: "green" | "orange" | "red";
    bankruptcy: "green" | "orange" | "red";
    legal: "green" | "orange" | "red";
  };
  dataSource?: "BOE" | "NewsAPI" | "both";
  dateRange?: {
    type: "preset" | "custom";
    daysBack?: number;
    startDate?: string;
    endDate?: string;
  };
  sources?: SearchResult[];
}

export interface BatchUploadRequest {
  companies: string[];
  dataSource: "BOE" | "NewsAPI" | "both";
  dateRange?: {
    type: "preset" | "custom";
    daysBack?: number;
    startDate?: string;
    endDate?: string;
  };
}

export interface BatchUploadResponse {
  results: RiskAssessmentResponse[];
  processed: number;
  failed: number;
  errors?: string[];
}

// Define the API slice
export const riskAssessmentApi = createApi({
  reducerPath: "riskAssessmentApi",
  baseQuery: axiosBaseQuery({
    baseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  }),
  tagTypes: ["Search", "SavedResults"],
  endpoints: (builder) => ({
    // Main search endpoint matching the actual API specification
    searchCompany: builder.mutation<SearchResponse, SearchRequest>({
      query: (data) => ({
        url: "/api/v1/search",
        method: "POST",
        data,
      }),
      invalidatesTags: ["Search"],
    }),

    // Helper mutation to convert old format to new format
    getRiskAssessment: builder.mutation<
      SearchResponse,
      {
        companyName: string;
        dataSource: "BOE" | "NewsAPI" | "both";
        dateRange?: {
          type: "preset" | "custom";
          daysBack?: number;
          startDate?: string;
          endDate?: string;
        };
      }
    >({
      query: ({ companyName, dataSource, dateRange }) => {
        // Convert old format to new API format
        const searchData: SearchRequest = {
          company_name: companyName,
          include_boe: dataSource === "BOE" || dataSource === "both",
          include_news: dataSource === "NewsAPI" || dataSource === "both",
        };

        // Handle date range conversion
        if (dateRange) {
          if (dateRange.type === "preset" && dateRange.daysBack) {
            searchData.days_back = dateRange.daysBack;
          } else if (dateRange.type === "custom") {
            searchData.start_date = dateRange.startDate;
            searchData.end_date = dateRange.endDate;
          }
        }

        return {
          url: "/api/v1/search",
          method: "POST",
          data: searchData,
        };
      },
      invalidatesTags: ["Search"],
    }),

    // Get saved results (if this endpoint exists)
    getSavedResults: builder.query<SearchResponse[], void>({
      query: () => ({
        url: "/api/v1/saved-results",
        method: "GET",
      }),
      providesTags: ["SavedResults"],
    }),

    // Save a result (if this endpoint exists)
    saveResult: builder.mutation<{ success: boolean }, SearchResponse>({
      query: (data) => ({
        url: "/api/v1/saved-results",
        method: "POST",
        data,
      }),
      invalidatesTags: ["SavedResults"],
    }),

    // Delete a saved result (if this endpoint exists)
    deleteSavedResult: builder.mutation<{ success: boolean }, string>({
      query: (id) => ({
        url: `/api/v1/saved-results/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["SavedResults"],
    }),
  }),
});

// Export hooks for usage in functional components
export const {
  useSearchCompanyMutation,
  useGetRiskAssessmentMutation,
  useGetSavedResultsQuery,
  useSaveResultMutation,
  useDeleteSavedResultMutation,
} = riskAssessmentApi;
