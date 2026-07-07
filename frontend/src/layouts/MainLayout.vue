<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useDisplay, useTheme } from "vuetify";
import { storeToRefs } from "pinia";
import { logout } from "@/modules/auth/authService";
import { useUiStore } from "@/stores/ui";

const router = useRouter();
const route = useRoute();
const display = useDisplay();
const theme = useTheme();
const uiStore = useUiStore();
const { isDark } = storeToRefs(uiStore);
const drawer = ref(true);

const isMobile = computed(() => display.smAndDown.value);
const isDesktop = computed(() => display.mdAndUp.value);
const drawerWidth = computed(() => (display.lgAndUp.value ? 260 : 232));
const breadcrumbs = computed(() => [
  { title: "Inicio", to: "/dashboard", disabled: route.path === "/dashboard" },
  {
    title: route.meta.title || "Página",
    disabled: true,
  },
]);

const menuItems = [
  { title: "Dashboard", icon: "mdi-view-dashboard", to: "/dashboard" },
  { title: "Clientes", icon: "mdi-account-group", to: "/clientes" },
  { title: "Proveedores", icon: "mdi-truck", to: "/proveedores" },
  { title: "Inventario", icon: "mdi-package-variant", to: "/inventario" },
  { title: "Movimientos", icon: "mdi-swap-horizontal", to: "/movimientos-inventario" },
  { title: "Categorías", icon: "mdi-shape", to: "/categorias" },
  { title: "Compras", icon: "mdi-cart-arrow-down", to: "/compras" },
  { title: "Ventas", icon: "mdi-cash-register", to: "/ventas" },
  { title: "CxC", icon: "mdi-cash-clock", to: "/cuentas-cobrar" },
  { title: "CxP", icon: "mdi-credit-card-clock", to: "/cuentas-pagar" },
  { title: "Reportes", icon: "mdi-chart-box", to: "/reportes" },
  { title: "Configuración", icon: "mdi-cog", to: "/configuracion" },
];

function handleLogout() {
  logout();
  router.push("/login");
}

function toggleTheme() {
  uiStore.toggleTheme();
}

function handleShortcut(event) {
  const key = event.key.toLowerCase();

  if (event.ctrlKey && key === "b") {
    event.preventDefault();
    drawer.value = !drawer.value;
  }

  if (event.ctrlKey && key === "d") {
    event.preventDefault();
    toggleTheme();
  }

  if (key === "/" && !["INPUT", "TEXTAREA"].includes(event.target.tagName)) {
    const searchInput = document.querySelector(
      "input[type='text'], input[aria-label*='Buscar']"
    );

    if (searchInput) {
      event.preventDefault();
      searchInput.focus();
    }
  }
}

watch(
  isMobile,
  (value) => {
    drawer.value = !value;
  },
  { immediate: true }
);

watch(
  () => uiStore.theme,
  (value) => {
    theme.global.name.value = value;
  },
  { immediate: true }
);

onMounted(() => {
  window.addEventListener("keydown", handleShortcut);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleShortcut);
});
</script>

<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      :permanent="!isMobile"
      :temporary="isMobile"
      :width="drawerWidth"
    >
      <div class="pa-4 pa-lg-5">
        <h2 class="text-subtitle-1 text-lg-h6 font-weight-bold">
          Queso Los Santos
        </h2>
        <p class="text-caption text-medium-emphasis mb-0">
          Sistema financiero-contable
        </p>
      </div>

      <v-divider />

      <v-list nav density="comfortable">
        <v-list-item
          v-for="item in menuItems"
          :key="item.to"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          rounded="lg"
          @click="isMobile && (drawer = false)"
        />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar elevation="1">
      <v-app-bar-nav-icon v-if="isMobile" @click="drawer = !drawer" />

      <v-app-bar-title class="app-title">
        Sistema Web Financiero-Contable
      </v-app-bar-title>

      <v-spacer />

      <v-tooltip text="Cambiar tema (Ctrl+D)">
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            :icon="isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
            variant="text"
            @click="toggleTheme"
          />
        </template>
      </v-tooltip>

      <v-btn
        variant="text"
        :prepend-icon="isDesktop ? 'mdi-logout' : undefined"
        :icon="isMobile ? 'mdi-logout' : undefined"
        @click="handleLogout"
      >
        <span v-if="isDesktop">Cerrar sesión</span>
      </v-btn>
    </v-app-bar>

    <v-main class="app-main">
      <v-container fluid class="app-container">
        <v-breadcrumbs
          class="px-0 pt-0 pb-3"
          density="compact"
          :items="breadcrumbs"
        />
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
.app-container {
  padding: 16px;
}

.app-main {
  background: rgb(var(--v-theme-background));
}

.app-title {
  font-size: 0.98rem;
  min-width: 0;
}

@media (min-width: 600px) {
  .app-container {
    padding: 20px;
  }
}

@media (min-width: 960px) {
  .app-container {
    padding: 24px;
  }

  .app-title {
    font-size: 1.05rem;
  }
}
</style>
