import axios from 'axios';

const apiClient = axios.create({
  baseURL: "https://recoleccta-app.onrender.com/api",
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
