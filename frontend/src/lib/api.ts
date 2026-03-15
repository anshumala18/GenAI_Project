import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 300000, // 5 minutes (for long analysis tasks)
});

// Request interceptor: Add JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("docai_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle unauthorized access
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login if unauthorized
      localStorage.removeItem("docai_token");
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
