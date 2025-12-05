"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { extractApiErrorMessage } from "@/lib/error-helpers";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  org_id: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: any) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check for existing auth token
    const token = Cookies.get("auth_token");
    if (token) {
      // Verify token and get user info
      verifyToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (token: string) => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(response.data);
    } catch (error) {
      // Token invalid, clear it
      Cookies.remove("auth_token");
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/login-json`, {
        email,
        password,
      });

      const { access_token } = response.data;

      if (!access_token) {
        throw new Error("Login response did not include an access token");
      }

      Cookies.set("auth_token", access_token, { expires: 7 });

      const meResponse = await axios.get(`${API_URL}/api/v1/users/me`, {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      setUser(meResponse.data);
    } catch (error) {
      Cookies.remove("auth_token");
      throw new Error(extractApiErrorMessage(error, "Login failed"));
    }
  };

  const logout = () => {
    Cookies.remove("auth_token");
    setUser(null);
    router.push("/auth/login");
  };

  const register = async (data: any) => {
    try {
      await axios.post(`${API_URL}/api/v1/auth/register`, data);
      await login(data.email, data.password);
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, "Registration failed"));
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
