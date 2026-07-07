import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";

import { createVuetify } from "vuetify";

const vuetify = createVuetify({
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        dark: false,
        colors: {
          primary: "#2563eb",
          secondary: "#475569",
          success: "#16a34a",
          warning: "#d97706",
          error: "#dc2626",
          info: "#0891b2",
          background: "#f8fafc",
          surface: "#ffffff",
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: "#60a5fa",
          secondary: "#94a3b8",
          success: "#4ade80",
          warning: "#fbbf24",
          error: "#f87171",
          info: "#22d3ee",
          background: "#0f172a",
          surface: "#1e293b",
        },
      },
    },
  },
});

export default vuetify;
