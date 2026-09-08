import { createI18n } from "vue-i18n";
import es from "./locales/es.json";
import en from "./locales/en.json";
import { LOCALE_STORAGE_KEY, resolveLocale } from "./locale";
export { LOCALE_STORAGE_KEY } from "./locale";

const initialLocale = resolveLocale({
  userLocale: localStorage.getItem(LOCALE_STORAGE_KEY),
  browserLocale: navigator.language,
});

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: "es",
  messages: { es, en },
  missingWarn: import.meta.env.DEV,
  fallbackWarn: import.meta.env.DEV,
});

export function applyLocale(locale, { persist = true } = {}) {
  i18n.global.locale.value = locale;
  document.documentElement.lang = locale;
  if (persist) localStorage.setItem(LOCALE_STORAGE_KEY, locale);
}

export function clearLocalLocale() {
  localStorage.removeItem(LOCALE_STORAGE_KEY);
}

applyLocale(initialLocale, { persist: false });

export default i18n;
