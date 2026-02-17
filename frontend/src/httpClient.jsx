import axios from "axios";

const instance = axios.create({ withCredentials: true });

instance.interceptors.request.use((config) => {
  const base = import.meta.env.VITE_API_BASE || "http://localhost:5000";
  if (config.url && !config.url.startsWith("http")) {
    config.url = `${base}${config.url}`;
  }
  return config;
});

export default instance;
