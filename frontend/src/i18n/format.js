import { i18n } from "@/i18n";

export function currentIntlLocale() {
  return i18n.global.locale.value === "en" ? "en-US" : "es-CR";
}

export function formatCurrency(value, currency = "CRC", options = {}) {
  return new Intl.NumberFormat(currentIntlLocale(), {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    ...options,
  }).format(Number(value || 0));
}

export function formatDate(value, options = {}) {
  return value ? new Intl.DateTimeFormat(currentIntlLocale(), options).format(new Date(value)) : "";
}
