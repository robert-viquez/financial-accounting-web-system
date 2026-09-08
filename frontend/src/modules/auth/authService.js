import api from "@/api/axios";
import { applyLocale, LOCALE_STORAGE_KEY } from "@/i18n";

export async function login(username, password) {
  const response = await api.post("token/", {
    username,
    password,
  });

  localStorage.setItem("access_token", response.data.access);
  localStorage.setItem("refresh_token", response.data.refresh);

  try {
    const profile = (await api.get("mi-perfil/")).data;
    const localLocale = localStorage.getItem(LOCALE_STORAGE_KEY);
    if (profile.locale) {
      applyLocale(profile.locale);
    } else if (localLocale) {
      await api.patch("mi-perfil/", { locale: localLocale });
      applyLocale(localLocale);
    }
  } catch {
    // Authentication succeeds even if preferences cannot be synchronized.
  }

  return response.data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function isAuthenticated() {
  return !!localStorage.getItem("access_token");
}
