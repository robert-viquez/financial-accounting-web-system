<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { createInitialAdmin } from "../setupService";
import { applyLocale } from "@/i18n";

const router = useRouter();
const { locale, t } = useI18n();
const username = ref("");
const email = ref("");
const password = ref("");
const passwordConfirm = ref("");
const showPassword = ref(false);
const error = ref("");
const loading = ref(false);

function errorMessage(err) {
  const data = err.response?.data;
  if (!data || typeof data !== "object") return t("setup.error");
  const first = Object.values(data).flat()[0];
  return typeof first === "string" ? first : t("setup.error");
}

async function handleSetup() {
  error.value = "";
  if (password.value !== passwordConfirm.value) {
    error.value = t("setup.passwordMismatch");
    return;
  }
  loading.value = true;
  try {
    await createInitialAdmin({
      username: username.value,
      email: email.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
    });
    await router.replace("/login");
  } catch (err) {
    error.value = errorMessage(err);
  } finally {
    loading.value = false;
  }
}

function changeLanguage(value) {
  applyLocale(value);
  locale.value = value;
}
</script>

<template>
  <main class="setup-page">
    <section class="setup-card">
      <div class="language-selector" role="group" :aria-label="$t('language.label')">
        <button type="button" :class="{ selected: locale === 'es' }" @click="changeLanguage('es')">Español</button>
        <span aria-hidden="true">|</span>
        <button type="button" :class="{ selected: locale === 'en' }" @click="changeLanguage('en')">English</button>
      </div>
      <h1>{{ $t("setup.title") }}</h1>
      <p class="setup-subtitle">{{ $t("setup.subtitle") }}</p>

      <form @submit.prevent="handleSetup">
        <label for="setup-username">{{ $t("auth.username") }}</label>
        <input id="setup-username" v-model="username" type="text" autocomplete="username" required />

        <label for="setup-email">{{ $t("common.email") }}</label>
        <input id="setup-email" v-model="email" type="email" autocomplete="email" />

        <label for="setup-password">{{ $t("auth.password") }}</label>
        <div class="password-field">
          <input id="setup-password" v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="new-password" required />
          <button class="password-toggle" type="button" :aria-label="showPassword ? $t('auth.hidePassword') : $t('auth.showPassword')" :aria-pressed="showPassword" @click="showPassword = !showPassword">
            <span aria-hidden="true">{{ showPassword ? "◉" : "○" }}</span>
          </button>
        </div>

        <label for="setup-password-confirm">{{ $t("setup.confirmPassword") }}</label>
        <input id="setup-password-confirm" v-model="passwordConfirm" :type="showPassword ? 'text' : 'password'" autocomplete="new-password" required />

        <button class="submit" type="submit" :disabled="loading">
          {{ loading ? $t("setup.creating") : $t("setup.create") }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </section>
  </main>
</template>

<style scoped>
.setup-page { align-items: center; background: #e8edf3; display: flex; justify-content: center; min-height: 100vh; padding: 16px; }
.setup-card { background: #fff; border: 1px solid #cbd5e1; border-radius: 8px; box-shadow: 0 8px 30px rgba(0,0,0,.08); padding: 24px; width: min(100%, 420px); }
.language-selector { align-items: center; display: flex; gap: 8px; justify-content: flex-end; margin-bottom: 8px; }
.language-selector button, .password-toggle { background: transparent; border: 0; color: #334155; cursor: pointer; }
.language-selector button.selected { color: #1d4ed8; font-weight: 700; text-decoration: underline; }
h1, .setup-subtitle { text-align: center; }
h1 { color: #111827; margin-bottom: 6px; }
.setup-subtitle { color: #4b5563; margin-bottom: 24px; }
form { display: flex; flex-direction: column; gap: 12px; }
label { color: #1f2937; font-weight: 600; }
input { background: #fff; border: 1px solid #64748b; border-radius: 8px; color: #111827; font: inherit; min-height: 44px; padding: 10px 12px; width: 100%; }
input:focus { border-color: #1d4ed8; box-shadow: 0 0 0 3px rgba(29,78,216,.2); outline: none; }
.password-field { position: relative; }
.password-field input { padding-right: 48px; }
.password-toggle { height: 40px; position: absolute; right: 3px; top: 2px; width: 40px; }
.submit { background: #1f2937; border: 0; border-radius: 8px; color: #fff; cursor: pointer; margin-top: 12px; padding: 11px; }
.submit:disabled { opacity: .7; }
.error { color: #b91c1c; font-weight: 600; margin-bottom: 0; }
@media (min-width: 600px) { .setup-page { padding: 24px; } .setup-card { padding: 32px; } }
</style>
