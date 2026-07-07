import { defineStore } from "pinia";

const THEME_KEY = "ui_theme";

export const useUiStore = defineStore("ui", {
  state: () => ({
    pendingRequests: 0,
    theme: localStorage.getItem(THEME_KEY) || "light",
  }),
  getters: {
    isLoading: (state) => state.pendingRequests > 0,
    isDark: (state) => state.theme === "dark",
  },
  actions: {
    startLoading() {
      this.pendingRequests += 1;
    },
    stopLoading() {
      this.pendingRequests = Math.max(0, this.pendingRequests - 1);
    },
    setTheme(theme) {
      this.theme = theme;
      localStorage.setItem(THEME_KEY, theme);
    },
    toggleTheme() {
      this.setTheme(this.isDark ? "light" : "dark");
    },
  },
});
