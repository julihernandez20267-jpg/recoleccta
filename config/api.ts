const apiBaseUrl =
  process.env.EXPO_PUBLIC_API_URL ?? 'https://recoleccta-app.onrender.com/api';

export const API_BASE_URL = apiBaseUrl.replace(/\/+$/, '');
