export const SUPPORTED_LOCALES = ["es", "en"];
export const LOCALE_STORAGE_KEY = "faws_locale";

export function normalizeLocale(value) {
  const locale = String(value || "").trim().toLowerCase().split("-")[0];
  return SUPPORTED_LOCALES.includes(locale) ? locale : "es";
}

export function resolveLocale({ userLocale, defaultLocale = "auto", browserLocale } = {}) {
  if (SUPPORTED_LOCALES.includes(userLocale)) return userLocale;
  if (SUPPORTED_LOCALES.includes(defaultLocale)) return defaultLocale;
  return normalizeLocale(browserLocale);
}
