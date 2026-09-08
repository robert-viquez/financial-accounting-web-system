import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify';
import i18n, { applyLocale, LOCALE_STORAGE_KEY } from './i18n';
import { resolveLocale } from './i18n/locale';
import { isAuthenticated } from './modules/auth/authService';
import { getIdentidadEmpresa, getPerfil } from './modules/configuracion/api/configuracionService';

async function initializeLocale() {
  let defaultLocale = "auto";
  let userLocale = "";
  try {
    defaultLocale = (await getIdentidadEmpresa()).locale_predeterminado || "auto";
    if (isAuthenticated()) userLocale = (await getPerfil()).locale || "";
  } catch {
    // Locale resolution remains available when the API is temporarily unavailable.
  }
  const localLocale = localStorage.getItem(LOCALE_STORAGE_KEY) || "";
  applyLocale(resolveLocale({
    userLocale: userLocale || localLocale,
    defaultLocale,
    browserLocale: navigator.language,
  }), { persist: false });
  vuetify.locale.current.value = i18n.global.locale.value;
}

await initializeLocale();

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(i18n)
app.mount('#app')
