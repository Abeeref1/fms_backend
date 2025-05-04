// src/services/authService.ts
import apiClient from "@/lib/api";

// Interface for the user object returned from backend (based on Stakeholder.to_dict)
export interface User {
  id: number;
  name: string;
  role: string;
  contact_email: string;
  contact_phone: string | null;
  school_id: number | null;
  is_active: boolean;
}

// Interface for the login response
interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

// Interface for the refresh response
interface RefreshResponse {
  access_token: string;
}

// Interface for the /me response
interface MeResponse {
  user: User;
}

// Login function
export const login = async (email: string, password: string): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>("/auth/login", { email, password });
  return response.data;
};

// Refresh token function
export const refreshToken = async (refreshTok: string): Promise<RefreshResponse> => {
  // We need to send the refresh token in the Authorization header for this specific request
  const response = await apiClient.post<RefreshResponse>("/auth/refresh", null, {
    headers: {
      Authorization: `Bearer ${refreshTok}`
    }
  });
  return response.data;
};

// Get current user function (requires access token to be set in apiClient interceptor)
export const getCurrentUser = async (): Promise<MeResponse> => {
  const response = await apiClient.get<MeResponse>("/auth/me");
  return response.data;
};

