/**
 * SmartMed API Client
 * Robust, production-ready communication with FastAPI Backend
 */

// Dynamically determine the backend API URL
function getApiBaseUrl() {
  const customUrl = localStorage.getItem("SMARTMED_API_URL");
  if (customUrl) return customUrl.replace(/\/+$/, "");

  // If running on localhost or same host
  const { protocol, hostname, port } = window.location;
  if (port === "8000" || port === "") {
    return `${protocol}//${hostname}${port ? ":" + port : ""}`;
  }
  // Default to standard FastAPI port when frontend is served via Live Server or static server
  return "http://localhost:8000";
}

const API_BASE_URL = getApiBaseUrl();

// Token & User session helpers
const AuthStorage = {
  getToken: () => localStorage.getItem("smartmed_token"),
  setToken: (token) => localStorage.setItem("smartmed_token", token),
  removeToken: () => localStorage.removeItem("smartmed_token"),
  getUser: () => {
    try {
      const u = localStorage.getItem("smartmed_user");
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },
  setUser: (user) => localStorage.setItem("smartmed_user", JSON.stringify(user)),
  removeUser: () => localStorage.removeItem("smartmed_user"),
  clear: () => {
    localStorage.removeItem("smartmed_token");
    localStorage.removeItem("smartmed_user");
  }
};

// Toast notification helper
function showToast(message, type = "info", duration = 4000) {
  let container = document.getElementById("smartmed-toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "smartmed-toast-container";
    document.body.appendChild(container);
  }

  const icons = {
    success: "fa-circle-check",
    error: "fa-circle-exclamation",
    warning: "fa-triangle-exclamation",
    info: "fa-circle-info"
  };

  const toast = document.createElement("div");
  toast.className = `smart-toast ${type}`;
  toast.innerHTML = `
    <i class="fa-solid ${icons[type] || icons.info}" style="margin-top:2px;"></i>
    <div style="flex:1;">${message}</div>
    <button style="background:none;border:none;cursor:pointer;color:inherit;opacity:0.6;" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }
  }, duration);
}

// Unified fetch wrapper
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = options.headers || {};

  // Add Auth Token if available
  const token = AuthStorage.getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Check if body is FormData (e.g. file upload); do not set Content-Type in that case
  const isFormData = options.body instanceof FormData;
  if (!isFormData && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const config = {
    ...options,
    headers
  };

  try {
    const res = await fetch(url, config);

    // Handle 401 Unauthorized
    if (res.status === 401) {
      // If we are on an authenticated page, redirect to login
      const isPublicPage = window.location.pathname.includes("login.html") || 
                           window.location.pathname.includes("register.html") || 
                           window.location.pathname.endsWith("index.html") || 
                           window.location.pathname === "/" ||
                           window.location.pathname.includes("about.html") ||
                           window.location.pathname.includes("contact.html");
      if (!isPublicPage) {
        AuthStorage.clear();
        showToast("Your session has expired. Please log in again.", "warning");
        setTimeout(() => {
          window.location.href = "login.html";
        }, 1200);
      }
      const errorJson = await res.json().catch(() => ({}));
      throw new Error(errorJson.detail || "Authentication required");
    }

    if (!res.ok) {
      const errorJson = await res.json().catch(() => ({}));
      const message = errorJson.detail || `Request failed with status ${res.status}`;
      throw new Error(message);
    }

    // 204 No Content
    if (res.status === 204) return null;

    return await res.json();
  } catch (err) {
    console.error(`API Error on [${options.method || "GET"} ${endpoint}]:`, err);
    throw err;
  }
}

// SmartMed API Object
const SmartMedAPI = {
  // Authentication
  auth: {
    register: (userData) => fetchAPI("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(userData)
    }),
    login: (email, password) => fetchAPI("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),
    me: () => fetchAPI("/api/auth/me"),
    logout: () => {
      AuthStorage.clear();
      window.location.href = "login.html";
    }
  },

  // Users & Profile
  users: {
    updateProfile: (data) => fetchAPI("/api/users/profile", {
      method: "PUT",
      body: JSON.stringify(data)
    }),
    changePassword: (old_password, new_password) => fetchAPI("/api/users/change-password", {
      method: "PUT",
      body: JSON.stringify({ old_password, new_password })
    })
  },

  // Medicines (User's Prescriptions)
  medicines: {
    list: (status = null, search = null) => {
      let query = [];
      if (status) query.push(`status=${encodeURIComponent(status)}`);
      if (search) query.push(`search=${encodeURIComponent(search)}`);
      const qStr = query.length ? `?${query.join("&")}` : "";
      return fetchAPI(`/api/medicines${qStr}`);
    },
    get: (id) => fetchAPI(`/api/medicines/${id}`),
    create: (data) => fetchAPI("/api/medicines", {
      method: "POST",
      body: JSON.stringify(data)
    }),
    update: (id, data) => fetchAPI(`/api/medicines/${id}`, {
      method: "PUT",
      body: JSON.stringify(data)
    }),
    delete: (id) => fetchAPI(`/api/medicines/${id}`, {
      method: "DELETE"
    })
  },

  // Educational Medicine Library
  medicineInfo: {
    search: (search = "", category = "") => {
      let query = [];
      if (search) query.push(`search=${encodeURIComponent(search)}`);
      if (category && category !== "all") query.push(`category=${encodeURIComponent(category)}`);
      const qStr = query.length ? `?${query.join("&")}` : "";
      return fetchAPI(`/api/medicine-info${qStr}`);
    },
    categories: () => fetchAPI("/api/medicine-info/categories"),
    get: (id) => fetchAPI(`/api/medicine-info/${id}`),
    related: (id) => fetchAPI(`/api/medicine-info/${id}/related`)
  },

  // Schedules
  schedules: {
    list: () => fetchAPI("/api/schedules"),
    create: (data) => fetchAPI("/api/schedules", {
      method: "POST",
      body: JSON.stringify(data)
    }),
    update: (id, data) => fetchAPI(`/api/schedules/${id}`, {
      method: "PUT",
      body: JSON.stringify(data)
    }),
    delete: (id) => fetchAPI(`/api/schedules/${id}`, {
      method: "DELETE"
    }),
    today: () => fetchAPI("/api/schedules/today"),
    upcoming: () => fetchAPI("/api/schedules/upcoming")
  },

  // Logs & Dose Tracking
  logs: {
    list: (params = {}) => {
      let query = [];
      if (params.status) query.push(`status=${encodeURIComponent(params.status)}`);
      if (params.date_from) query.push(`date_from=${encodeURIComponent(params.date_from)}`);
      if (params.date_to) query.push(`date_to=${encodeURIComponent(params.date_to)}`);
      if (params.medicine_id) query.push(`medicine_id=${encodeURIComponent(params.medicine_id)}`);
      if (params.limit) query.push(`limit=${encodeURIComponent(params.limit)}`);
      const qStr = query.length ? `?${query.join("&")}` : "";
      return fetchAPI(`/api/logs${qStr}`);
    },
    updateStatus: (id, status, notes = null) => fetchAPI(`/api/logs/${id}/status`, {
      method: "PUT",
      body: JSON.stringify({ status, notes })
    }),
    snooze: (id, snooze_minutes = 15) => fetchAPI(`/api/logs/${id}/snooze`, {
      method: "POST",
      body: JSON.stringify({ snooze_minutes })
    })
  },

  // Notifications
  notifications: {
    list: (limit = 50) => fetchAPI(`/api/notifications?limit=${limit}`),
    unreadCount: () => fetchAPI("/api/notifications/unread-count"),
    markRead: (id) => fetchAPI(`/api/notifications/${id}/read`, { method: "PUT" }),
    markAllRead: () => fetchAPI("/api/notifications/read-all", { method: "PUT" }),
    delete: (id) => fetchAPI(`/api/notifications/${id}`, { method: "DELETE" }),
    clearAll: () => fetchAPI("/api/notifications/clear-all", { method: "DELETE" })
  },

  // Prescriptions
  prescriptions: {
    list: () => fetchAPI("/api/prescriptions"),
    upload: (formData) => fetchAPI("/api/prescriptions/upload", {
      method: "POST",
      body: formData
    }),
    delete: (id) => fetchAPI(`/api/prescriptions/${id}`, { method: "DELETE" })
  },

  // Reports
  reports: {
    adherence: (period = "week") => fetchAPI(`/api/reports/adherence?period=${period}`),
    dashboardSummary: () => fetchAPI("/api/reports/dashboard-summary")
  },

  // Settings
  settings: {
    get: () => fetchAPI("/api/settings"),
    update: (data) => fetchAPI("/api/settings", {
      method: "PUT",
      body: JSON.stringify(data)
    })
  }
};
