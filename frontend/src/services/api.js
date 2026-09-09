import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // 60 seconds request timeout for local LLM & RAG generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('statsaksham_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for auth expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token invalid / expired
      localStorage.removeItem('statsaksham_token');
      localStorage.removeItem('statsaksham_user');
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (employee_id, password) => api.post('/auth/login', { employee_id, password }),
  getMe: () => api.get('/auth/me'),
};

// Employees API
export const employeeAPI = {
  list: (params) => api.get('/employees', { params }),
  getById: (id) => api.get(`/employees/${id}`),
  update: (id, data) => api.put(`/employees/${id}`, data),
};

// Competencies & Skill Gaps API
export const competencyAPI = {
  listAll: () => api.get('/competencies'),
  listRequirements: () => api.get('/competencies/requirements'),
  getEmployeeCompetencies: (empId) => api.get(`/employees/${empId}/competencies`),
  getSkillGaps: (empId) => api.get(`/employees/${empId}/skill-gaps`),
};

// Assessments API
export const assessmentAPI = {
  list: () => api.get('/assessments'),
  getById: (id) => api.get(`/assessments/${id}`),
  submit: (id, data) => api.post(`/assessments/${id}/submit`, data),
};

// Recommendations API
export const recommendationAPI = {
  getForEmployee: (empId, refresh = false) => api.get(`/employees/${empId}/recommendations`, { params: { refresh } }),
  refresh: (empId) => api.post(`/employees/${empId}/recommendations/refresh`),
};

// Courses API
export const courseAPI = {
  getIGOT: (params) => api.get('/courses/igot', { params }),
  getNSSTA: (params) => api.get('/courses/nssta', { params }),
  getCatalogue: () => api.get('/courses/catalogue'),
  getDetails: (type, id) => api.get(`/courses/${type}/${id}`),
};

// Progress API
export const progressAPI = {
  getForEmployee: (empId) => api.get(`/employees/${empId}/progress`),
  enrollOrUpdate: (data) => api.post('/progress', data),
  updateDirect: (id, data) => api.put(`/progress/${id}`, data),
};

// AI Quiz & RAG API
export const quizAPI = {
  uploadDocument: (formData) => api.post('/quiz/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getDocuments: (empId) => api.get(`/quiz/documents/${empId}`),
  getDocumentStatus: (docId) => api.get(`/quiz/documents/${docId}/status`),
  searchRAG: (docId, query, topK = 4) => api.post('/quiz/search', null, { params: { document_id: docId, query, top_k: topK } }),
  generateQuiz: (data) => api.post('/quiz/generate', data),
  submitQuiz: (data) => api.post('/quiz/submit', data),
};

// AI Learning Assistant API
export const aiAPI = {
  getStatus: () => api.get('/ai/status'),
  getHealth: () => api.get('/ai/health'),
  chat: (data) => api.post('/ai/chat', data),
  getHistory: (empId) => api.get(`/ai/history/${empId}`),
};

// Admin API
export const adminAPI = {
  getAnalytics: () => api.get('/admin/analytics'),
};

export default api;
