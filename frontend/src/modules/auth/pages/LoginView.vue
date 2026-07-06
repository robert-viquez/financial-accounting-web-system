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
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f6f8;
}

.login-card {
  width: 360px;
  padding: 32px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

h1 {
  margin-bottom: 4px;
}

p {
  margin-bottom: 24px;
  color: #666;
}

form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

input {
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

button {
  margin-top: 12px;
  padding: 11px;
  border: none;
  border-radius: 8px;
  background: #1f2937;
  color: white;
  cursor: pointer;
}

button:disabled {
  opacity: 0.7;
}

.error {
  color: #b91c1c;
  margin-top: 8px;
}
</style>