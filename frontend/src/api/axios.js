import axios from "axios";
import { useUiStore } from "@/stores/ui";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000/api/",
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
    },
});

api.interceptors.request.use((config) => {
    const uiStore = useUiStore();
    const token = localStorage.getItem("access_token");

    uiStore.startLoading();

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

api.interceptors.response.use(
    (response) => {
        useUiStore().stopLoading();
        return response;
    },
    (error) => {
        useUiStore().stopLoading();
        return Promise.reject(error);
    },
);

export default api;
