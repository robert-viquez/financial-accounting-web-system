<script setup>
import { useRouter } from "vue-router";
import { logout } from "@/modules/auth/authService";

const router = useRouter();

const menuItems = [
  { title: "Dashboard", icon: "mdi-view-dashboard", to: "/dashboard" },
  { title: "Clientes", icon: "mdi-account-group", to: "/clientes" },
  { title: "Proveedores", icon: "mdi-truck", to: "/proveedores" },
  { title: "Inventario", icon: "mdi-package-variant", to: "/inventario" },
  { title: "Compras", icon: "mdi-cart-arrow-down", to: "/compras" },
  { title: "Ventas", icon: "mdi-cash-register", to: "/ventas" },
  { title: "CxC", icon: "mdi-cash-clock", to: "/cuentas-cobrar" },
  { title: "CxP", icon: "mdi-credit-card-clock", to: "/cuentas-pagar" },
  { title: "Reportes", icon: "mdi-chart-box", to: "/reportes" },
];

function handleLogout() {
  logout();
  router.push("/login");
}
</script>

<template>
  <v-app>
    <v-navigation-drawer permanent width="260">
      <div class="pa-5">
        <h2 class="text-h6 font-weight-bold">Queso Los Santos</h2>
        <p class="text-caption text-medium-emphasis">Sistema financiero-contable</p>
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
        />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar elevation="1">
      <v-app-bar-title>Sistema Web Financiero-Contable</v-app-bar-title>

      <v-spacer />

      <v-btn variant="text" prepend-icon="mdi-logout" @click="handleLogout">
        Cerrar sesión
      </v-btn>
    </v-app-bar>

    <v-main class="bg-grey-lighten-4">
      <v-container fluid class="pa-6">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>