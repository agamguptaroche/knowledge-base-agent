import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "";

const api = axios.create({ baseURL: API_BASE });

// Admin
export const uploadDocument = (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/api/admin/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: onProgress,
  });
};

export const listDocuments = () => api.get("/api/admin/documents");

export const deleteDocument = (docId) =>
  api.delete(`/api/admin/documents/${docId}`);

// User
export const queryKnowledgeBase = (question) =>
  api.post("/api/query", { question });

// Health
export const getHealth = () => api.get("/api/health");

export default api;
