import { createContext, useState, useEffect, ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

interface User {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: "admin" | "user";
  is_active: boolean;
  created_at: string;
  last_login?: string;
  // Computed field for display
  name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
}

// API base URL
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

// Helper function to transform user data from backend to frontend format
const transformUserData = (userData: any): User => {
  return {
    ...userData,
    name: `${userData.first_name} ${userData.last_name}`.trim(),
  };
};

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Check if token is valid on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      const storedToken = localStorage.getItem("authToken");
      const storedUser = localStorage.getItem("user");

      if (storedToken && storedUser) {
        try {
          // Verify token with backend
          const response = await axios.get(`${API_BASE_URL}/auth/me`, {
            headers: {
              Authorization: `Bearer ${storedToken}`,
            },
          });

          if (response.status === 200) {
            const userData = transformUserData(response.data);
            setToken(storedToken);
            setUser(userData);
            setIsAuthenticated(true);

            // Load user-specific saved results
            const savedResults = localStorage.getItem(
              `savedResults-${userData.email}`
            );
            if (savedResults) {
              localStorage.setItem("savedResults", savedResults);
            }

            if (location.pathname === "/login") {
              navigate("/", { replace: true });
            }
          } else {
            // Token is invalid, clear storage
            localStorage.removeItem("authToken");
            localStorage.removeItem("user");
            localStorage.removeItem("savedResults");
          }
        } catch (error) {
          console.error("Token validation failed:", error);
          // Token is invalid, clear storage
          localStorage.removeItem("authToken");
          localStorage.removeItem("user");
          localStorage.removeItem("savedResults");

          if (location.pathname !== "/login") {
            navigate("/login", { replace: true });
          }
        }
      } else if (location.pathname !== "/login") {
        navigate("/login", { replace: true });
      }

      setIsLoading(false);
    };

    checkAuthStatus();
  }, [navigate, location.pathname]);

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password,
      });

      if (response.status === 200) {
        const { access_token, user: userData } = response.data;
        const transformedUserData = transformUserData(userData);

        // Load user-specific saved results before setting them in localStorage
        const userSavedResults = localStorage.getItem(
          `savedResults-${userData.email}`
        );
        if (userSavedResults) {
          localStorage.setItem("savedResults", userSavedResults);
        } else {
          localStorage.removeItem("savedResults");
        }

        localStorage.setItem("authToken", access_token);
        localStorage.setItem("user", JSON.stringify(transformedUserData));

        setUser(transformedUserData);
        setToken(access_token);
        setIsAuthenticated(true);

        return true;
      }
    } catch (error: any) {
      console.error("Login failed:", error);
      if (error.response?.status === 401) {
        setError("Invalid email or password");
      } else if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError("Login failed. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }

    return false;
  };

  const logout = () => {
    if (user) {
      // Save current results to user-specific storage before clearing
      const currentResults = localStorage.getItem("savedResults");
      if (currentResults) {
        localStorage.setItem(`savedResults-${user.email}`, currentResults);
      }
    }

    localStorage.removeItem("authToken");
    localStorage.removeItem("user");
    localStorage.removeItem("savedResults");

    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    setError(null);

    navigate("/login", { replace: true });
  };

  if (isLoading) {
    return null;
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        login,
        logout,
        isLoading,
        error,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
