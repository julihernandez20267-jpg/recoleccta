import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

const apiClient = axios.create({
  baseURL: "http://10.157.28.110:8001/api",
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  try {
    const { useAuthStore } = require('@/store/useAuthStore');
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (error) {
    console.warn('Error fetching token dynamically in apiClient interceptor:', error);
  }
  return config;
});

export default apiClient;
