import axios from "axios";

export const getApiBase = () => {
  // Always use the production backend — works from both local dev and production
  if (typeof window === "undefined") return "https://ai-rag-project-llm-based.onrender.com";
  return "https://ai-rag-project-llm-based.onrender.com";
};

export const api = axios.create({
  baseURL: getApiBase(),
});

// Interceptor to add Authorization header automatically if token exists in localStorage
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});
