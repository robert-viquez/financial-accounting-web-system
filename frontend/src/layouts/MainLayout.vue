<script setup>
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useDisplay } from "vuetify";
import { logout } from "@/modules/auth/authService";

const router = useRouter();
const display = useDisplay();
const drawer = ref(true);

const isMobile = computed(() => display.smAndDown.value);
const isDesktop = computed(() => display.mdAndUp.value);
const drawerWidth = computed(() => (display.lgAndUp.value ? 260 : 232));

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

watch(
  isMobile,
  (value) => {
    drawer.value = !value;
  },
  { immediate: true }
);
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

      <v-btn
        variant="text"
        :prepend-icon="isDesktop ? 'mdi-logout' : undefined"
        :icon="isMobile ? 'mdi-logout' : undefined"
        @click="handleLogout"
      >
        <span v-if="isDesktop">Cerrar sesión</span>
      </v-btn>
    </v-app-bar>

    <v-main class="bg-grey-lighten-4">
      <v-container fluid class="app-container">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
.app-container {
  padding: 16px;
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
