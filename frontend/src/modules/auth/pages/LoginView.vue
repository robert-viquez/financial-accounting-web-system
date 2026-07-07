<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { login } from "../authService";

const router = useRouter();

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

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
      <h1>Queso Los Santos</h1>
      <p>Sistema financiero-contable</p>

      <form @submit.prevent="handleLogin">
        <label>Usuario</label>
        <input v-model="username" type="text" required />

        <label>Contraseña</label>
        <input v-model="password" type="password" required />

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
  background: #f5f6f8;
  display: flex;
  justify-content: center;
  min-height: 100vh;
  padding: 16px;
}

.login-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  padding: 24px;
  width: min(100%, 420px);
}

h1 {
  margin-bottom: 4px;
}

p {
  color: #666;
  margin-bottom: 24px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

input {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px 12px;
  width: 100%;
}

button {
  background: #1f2937;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  margin-top: 12px;
  padding: 11px;
  width: 100%;
}

button:disabled {
  opacity: 0.7;
}

.error {
  color: #b91c1c;
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
