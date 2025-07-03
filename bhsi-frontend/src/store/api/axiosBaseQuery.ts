import type { BaseQueryFn } from "@reduxjs/toolkit/query";
import axios from "axios";
import type { AxiosRequestConfig, AxiosError } from "axios";

// Create axios instance with default configuration
const axiosInstance = axios.create({
  timeout: 120000, // 120 seconds timeout for long-running analytics requests
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
axiosInstance.interceptors.request.use(
  (config) => {
    // Get auth token from localStorage if available
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle 401 - Unauthorized
    if (error.response?.status === 401) {
      // Clear auth token and redirect to login
      localStorage.removeItem("authToken");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }

    // Handle 403 - Forbidden
    if (error.response?.status === 403) {
      console.error("Access forbidden:", error.response.data);
    }

    // Handle 500 - Server Error
    if (error.response?.status === 500) {
      console.error("Server error:", error.response.data);
    }

    return Promise.reject(error);
  }
);

// Base query function for RTK Query
export const axiosBaseQuery =
  (
    { baseUrl }: { baseUrl: string } = { baseUrl: "" }
  ): BaseQueryFn<
    {
      url: string;
      method?: AxiosRequestConfig["method"];
      data?: AxiosRequestConfig["data"];
      params?: AxiosRequestConfig["params"];
      headers?: AxiosRequestConfig["headers"];
    },
    unknown,
    unknown
  > =>
  async ({ url, method = "get", data, params, headers }) => {
    try {
      const result = await axiosInstance({
        url: baseUrl + url,
        method,
        data,
        params,
        headers,
      });
      return { data: result.data };
    } catch (axiosError) {
      const err = axiosError as AxiosError;
      return {
        error: {
          status: err.response?.status,
          data: err.response?.data || err.message,
        },
      };
    }
  };

// Export axios instance for direct use if needed
export { axiosInstance };
