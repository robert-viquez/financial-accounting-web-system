<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useDisplay, useTheme } from "vuetify";
import { storeToRefs } from "pinia";
import { logout } from "@/modules/auth/authService";
import { useUiStore } from "@/stores/ui";
import { getConfiguracion } from "@/modules/configuracion/api/configuracionService";
import defaultLogo from "@/assets/queso-los-santos-logo.png";

const router = useRouter();
const route = useRoute();
const display = useDisplay();
const theme = useTheme();
const uiStore = useUiStore();
const { isDark } = storeToRefs(uiStore);
const drawer = ref(true);
const rail = ref(false);
const empresaNombre = ref("Sistema financiero-contable");
const logoUrl = ref(defaultLogo);

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

const menuGroups = [
  {
    title: "Operaciones",
    icon: "mdi-storefront-outline",
    items: [
      { title: "Ventas", icon: "mdi-cash-register", to: "/ventas" },
      { title: "Compras", icon: "mdi-cart-arrow-down", to: "/compras" },
      { title: "Clientes", icon: "mdi-account-group", to: "/clientes" },
      { title: "Proveedores", icon: "mdi-truck", to: "/proveedores" },
    ],
  },
  {
    title: "Inventario",
    icon: "mdi-package-variant",
    items: [
      { title: "Productos", icon: "mdi-package-variant", to: "/inventario" },
      { title: "Movimientos", icon: "mdi-swap-horizontal", to: "/movimientos-inventario" },
      { title: "Categorías", icon: "mdi-shape", to: "/categorias" },
    ],
  },
  {
    title: "Contabilidad",
    icon: "mdi-book-open-page-variant",
    items: [
      { title: "Resumen contable", icon: "mdi-book-open-page-variant", to: "/contabilidad" },
      { title: "Cuentas por cobrar", icon: "mdi-cash-clock", to: "/cuentas-cobrar" },
      { title: "Cuentas por pagar", icon: "mdi-credit-card-clock", to: "/cuentas-pagar" },
    ],
  },
];

const standaloneItems = [
  { title: "Inicio", icon: "mdi-view-dashboard", to: "/dashboard" },
  { title: "Reportes", icon: "mdi-chart-box", to: "/reportes" },
  { title: "Configuración", icon: "mdi-cog", to: "/configuracion" },
];

function toggleMenu() {
  if (isMobile.value) drawer.value = !drawer.value;
  else rail.value = !rail.value;
}

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
    toggleMenu();
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

onMounted(async () => {
  window.addEventListener("keydown", handleShortcut);
  try {
    const configuracion = await getConfiguracion();
    empresaNombre.value = configuracion.nombre || empresaNombre.value;
    logoUrl.value = configuracion.logo || defaultLogo;
  } catch {
    // La navegación sigue disponible aunque la configuración no responda.
  }
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
      :rail="rail && !isMobile"
      :width="drawerWidth"
      @click="rail && !isMobile && (rail = false)"
    >
      <div
        class="brand"
        :class="{ 'brand--rail': rail && !isMobile }"
        :style="{ backgroundImage: `url(${logoUrl})` }"
        role="img"
        :aria-label="`Logo de ${empresaNombre}`"
      >
        <div v-if="!rail || isMobile" class="brand-copy">
          <h2 class="text-subtitle-1 text-lg-h6 font-weight-bold">
            {{ empresaNombre }}
          </h2>
          <p class="text-caption mb-0">
            Sistema financiero-contable
          </p>
        </div>
      </div>

      <v-divider />

      <v-list nav density="comfortable" aria-label="Menú principal">
        <v-list-item
          v-for="item in standaloneItems.slice(0, 1)"
          :key="item.to"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          rounded="lg"
          @click="isMobile && (drawer = false)"
        />

        <v-list-group
          v-for="group in menuGroups"
          :key="group.title"
          :value="group.title"
        >
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              :prepend-icon="group.icon"
              :title="group.title"
              rounded="lg"
            />
          </template>
          <v-list-item
            v-for="item in group.items"
            :key="item.to"
            :to="item.to"
            :prepend-icon="item.icon"
            :title="item.title"
            rounded="lg"
            @click="isMobile && (drawer = false)"
          />
        </v-list-group>

        <v-list-item
          v-for="item in standaloneItems.slice(1)"
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
      <v-app-bar-nav-icon
        :aria-label="isMobile ? 'Abrir o cerrar menú' : 'Expandir o contraer menú'"
        @click="toggleMenu"
      />

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

.brand {
  align-items: center;
  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;
  display: flex;
  min-height: 118px;
  overflow: hidden;
  padding: 16px;
  position: relative;
}

.brand::before {
  background: linear-gradient(90deg, rgba(17, 24, 39, 0.86), rgba(17, 24, 39, 0.34));
  content: "";
  inset: 0;
  position: absolute;
}

.brand--rail {
  background-size: auto 100%;
  min-height: 88px;
  padding: 0;
}

.brand-copy {
  color: #fff;
  min-width: 0;
  position: relative;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.72);
  z-index: 1;
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
