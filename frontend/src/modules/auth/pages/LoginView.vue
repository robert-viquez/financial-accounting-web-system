<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { login } from "../authService";
import { getIdentidadEmpresa } from "@/modules/configuracion/api/configuracionService";
import defaultLogo from "@/assets/queso-los-santos-logo.png";

const router = useRouter();

const username = ref("");
const password = ref("");
const showPassword = ref(false);
const error = ref("");
const loading = ref(false);
const logoUrl = ref(defaultLogo);
const empresaNombre = ref("Queso Los Santos");

onMounted(async () => {
  try {
    const configuracion = await getIdentidadEmpresa();
    logoUrl.value = configuracion.logo || defaultLogo;
    empresaNombre.value = configuracion.nombre || empresaNombre.value;
  } catch {
    // La identidad predeterminada mantiene el login disponible sin conexión al API.
  }
});

async function handleLogin() {
  error.value = "";
  loading.value = true;

  try {
    await login(username.value, password.value);
    router.push("/dashboard");
  } catch (err) {
    console.error(err.response?.data || err.message);
    error.value = err.response?.data?.detail || "No se pudo iniciar sesión.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-card">
      <img class="login-logo" :src="logoUrl" :alt="`Logo de ${empresaNombre}`" />
      <h1>{{ empresaNombre }}</h1>
      <p class="login-subtitle">Sistema financiero-contable</p>

      <form @submit.prevent="handleLogin">
        <label for="username">Usuario</label>
        <input id="username" v-model="username" type="text" autocomplete="username" required />

        <label for="password">Contraseña</label>
        <div class="password-field">
          <input
            id="password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            required
          />
          <button
            class="password-toggle"
            type="button"
            :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            :aria-pressed="showPassword"
            @click="showPassword = !showPassword"
          >
            <svg v-if="showPassword" viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M12 5c5.5 0 9.5 5.5 9.5 7s-4 7-9.5 7-9.5-5.5-9.5-7S6.5 5 12 5Zm0 2c-3.8 0-6.8 3.4-7.4 5 .6 1.6 3.6 5 7.4 5s6.8-3.4 7.4-5c-.6-1.6-3.6-5-7.4-5Zm0 2.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5Z"
              />
            </svg>
            <svg v-else viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="m3.3 2 18.7 18.7-1.3 1.3-3.2-3.2A10.8 10.8 0 0 1 12 20c-5.5 0-9.5-5.5-9.5-7 0-.9 1.3-3 3.4-4.7L2 4.4 3.3 2Zm4 7.7C5.8 10.9 4.9 12.2 4.6 13c.6 1.6 3.6 5 7.4 5 1.4 0 2.7-.5 3.8-1.1l-1.6-1.6a4 4 0 0 1-5.5-5.5L7.3 9.7ZM12 6c5.5 0 9.5 5.5 9.5 7 0 .7-.8 2.2-2.3 3.7l-1.4-1.4c.8-.8 1.3-1.7 1.6-2.3-.6-1.6-3.6-5-7.4-5-.6 0-1.2.1-1.8.3L8.6 6.7A10.8 10.8 0 0 1 12 6Zm-.1 3a4 4 0 0 1 4.1 4.1L11.9 9Z"
              />
            </svg>
          </button>
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? "Ingresando..." : "Iniciar sesión" }}
        </button>

        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  align-items: center;
  background: #e8edf3;
  display: flex;
  justify-content: center;
  min-height: 100vh;
  padding: 16px;
}

.login-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  padding: 24px;
  width: min(100%, 420px);
}

.login-logo {
  border-radius: 12px;
  display: block;
  height: 150px;
  margin: 0 auto 20px;
  object-fit: contain;
  width: 100%;
}

h1,
.login-subtitle {
  text-align: center;
}

h1 {
  color: #111827;
  font-weight: 700;
  margin-bottom: 4px;
}

.login-subtitle {
  color: #4b5563;
  margin-bottom: 24px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

label {
  color: #1f2937;
  font-weight: 600;
}

input {
  background: #ffffff;
  border: 1px solid #64748b;
  border-radius: 8px;
  color: #111827;
  font: inherit;
  min-height: 44px;
  padding: 10px 12px;
  width: 100%;
}

input:focus {
  border-color: #1d4ed8;
  box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.2);
  outline: none;
}

.password-field {
  position: relative;
}

.password-field input {
  padding-right: 48px;
}

.password-toggle {
  align-items: center;
  background: transparent;
  border: 0;
  color: #334155;
  display: flex;
  height: 40px;
  justify-content: center;
  margin: 0;
  padding: 8px;
  position: absolute;
  right: 3px;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
}

.password-toggle:hover {
  background: #e2e8f0;
}

.password-toggle:focus-visible {
  box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.25);
  outline: 2px solid #1d4ed8;
  outline-offset: -2px;
}

.password-toggle svg {
  fill: currentColor;
  height: 22px;
  width: 22px;
}

button[type="submit"] {
  background: #1f2937;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  margin-top: 12px;
  padding: 11px;
  width: 100%;
}

button[type="submit"]:hover:not(:disabled) {
  background: #111827;
}

button[type="submit"]:focus-visible {
  outline: 3px solid #2563eb;
  outline-offset: 2px;
}

button[type="submit"]:disabled {
  opacity: 0.7;
}

.error {
  color: #b91c1c;
  font-weight: 600;
  margin-bottom: 0;
  margin-top: 8px;
}

@media (min-width: 600px) {
  .login-page {
    padding: 24px;
  }

  .login-card {
    padding: 32px;
  }
}
</style>
