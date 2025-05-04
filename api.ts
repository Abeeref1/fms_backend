// src/lib/api.ts
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { refreshToken } from "@/services/authService"; // Import refreshToken function

// Point to the backend API
const API_BASE_URL = "https://fms-backend-ft1y.onrender.com/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Important for potential future cookie-based auth or CSRF
});

// --- Token Management --- 

const ACCESS_TOKEN_KEY = "fms_access_token";
const REFRESH_TOKEN_KEY = "fms_refresh_token";

export const storeTokens = (accessToken: string, refreshToken: string) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

export const getAccessToken = (): string | null => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  // Optionally remove user info from storage as well
};

// --- Axios Interceptors --- 

let isRefreshing = false;
let failedQueue: { resolve: (value: unknown) => void; reject: (reason?: any) => void; }[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request Interceptor: Inject Authorization header
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    // Only add token if it exists and the request is not for refreshing the token
    if (token && !config.url?.includes("/auth/refresh")) { 
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle token expiration and refresh
apiClient.interceptors.response.use(
  (response) => {
    return response; // Pass through successful responses
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Check if it's a 401 error, not from the refresh endpoint itself, and not already retried
    if (error.response?.status === 401 && originalRequest.url !== "/auth/refresh" && !originalRequest._retry) {
      
      if (isRefreshing) {
        // If already refreshing, queue the request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers!.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true; // Mark as retried
      isRefreshing = true;

      const currentRefreshToken = getRefreshToken();
      if (!currentRefreshToken) {
        console.error("No refresh token available for refresh attempt.");
        isRefreshing = false;
        clearTokens(); // Clear potentially invalid tokens
        // Redirect to login page
        window.location.href = '/login'; // Fixed redirect
        return Promise.reject(error);
      }

      try {
        console.log("Attempting token refresh...");
        const { access_token: newAccessToken } = await refreshToken(currentRefreshToken);
        console.log("Token refresh successful.");
        storeTokens(newAccessToken, currentRefreshToken); // Store new access token, keep old refresh token
        
        // Update the header for the original request and process the queue
        apiClient.defaults.headers.common["Authorization"] = `Bearer ${newAccessToken}`;
        originalRequest.headers!.Authorization = `Bearer ${newAccessToken}`;
        processQueue(null, newAccessToken);
        
        // Retry the original request with the new token
        return apiClient(originalRequest);
      } catch (refreshError: any) {
        console.error("Token refresh failed:", refreshError);
        processQueue(refreshError, null);
        clearTokens(); // Clear tokens on refresh failure
        // Redirect to login page
        window.location.href = '/login'; // Fixed redirect
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // For other errors, just reject
    return Promise.reject(error);
  }
);

export default apiClient;

