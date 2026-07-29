import axios from "axios";
import { useUiStore } from "@/stores/ui";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/",
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

let refreshPromise = null;

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        const refreshToken = localStorage.getItem("refresh_token");

        if (
            error.response?.status !== 401 ||
            originalRequest?._retry ||
            !refreshToken ||
            originalRequest?.url === "token/refresh/"
        ) {
            return Promise.reject(error);
        }

        originalRequest._retry = true;

        try {
            refreshPromise ||= api
                .post("token/refresh/", { refresh: refreshToken })
                .then((response) => response.data.access)
                .finally(() => {
                    refreshPromise = null;
                });

            const accessToken = await refreshPromise;
            localStorage.setItem("access_token", accessToken);
            originalRequest.headers.Authorization = `Bearer ${accessToken}`;
            return api(originalRequest);
        } catch (refreshError) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            if (window.location.pathname !== "/login") {
                window.location.assign("/login");
            }
            return Promise.reject(refreshError);
        }
    },
);

export default api;
