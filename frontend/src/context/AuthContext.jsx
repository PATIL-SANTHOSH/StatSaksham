import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const defaultAuth = {
  user: null,
  loading: true,
  login: async () => ({ success: false }),
  quickLogin: async () => ({ success: false }),
  logout: () => {}
};

const AuthContext = createContext(defaultAuth);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('statsaksham_token');
      const savedUser = localStorage.getItem('statsaksham_user');
      
      if (token && savedUser) {
        try {
          setUser(JSON.parse(savedUser));
        } catch (e) {
          localStorage.removeItem('statsaksham_token');
          localStorage.removeItem('statsaksham_user');
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (employee_id, password) => {
    try {
      const res = await authAPI.login(employee_id, password);
      const data = res.data;
      
      const userData = {
        employee_id: data.employee_id,
        role: data.role,
        name: data.name,
        designation: data.designation,
        department: data.department
      };

      localStorage.setItem('statsaksham_token', data.access_token);
      localStorage.setItem('statsaksham_user', JSON.stringify(userData));
      setUser(userData);
      return { success: true, role: data.role };
    } catch (error) {
      const msg = error.response?.data?.detail || 'Authentication failed. Please check your credentials.';
      return { success: false, error: msg };
    }
  };

  const quickLogin = async (employee_id) => {
    const password = employee_id.startsWith('ADMIN') ? 'admin123' : 'demo123';
    return await login(employee_id, password);
  };

  const logout = () => {
    localStorage.removeItem('statsaksham_token');
    localStorage.removeItem('statsaksham_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, quickLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
