import { createRouter, createWebHistory } from "vue-router";
import { isAuthenticated } from "@/modules/auth/authService";

import LoginView from "@/modules/auth/pages/LoginView.vue";
import MainLayout from "@/layouts/MainLayout.vue";
import DashboardView from "@/modules/dashboard/pages/DashboardView.vue";

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    component: LoginView,
  },
  {
    path: "/",
    component: MainLayout,
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: "dashboard",
        component: DashboardView,
        meta: { title: "Dashboard" },
      },
      {
        path: "clientes",
        component: () => import("@/modules/clientes/pages/ClientesView.vue"),
        meta: { title: "Clientes" },
      },
      {
        path: "proveedores",
        component: () =>
          import("@/modules/proveedores/pages/ProveedoresView.vue"),
        meta: { title: "Proveedores" },
      },
      {
        path: "inventario",
        component: () => import("@/modules/inventario/pages/ProductosView.vue"),
        meta: { title: "Inventario" },
      },
      {
        path: "movimientos-inventario",
        component: () =>
          import("@/modules/inventario/pages/MovimientosView.vue"),
        meta: { title: "Movimientos de inventario" },
      },
      {
        path: "categorias",
        component: () => import("@/modules/inventario/pages/CategoriasView.vue"),
        meta: { title: "Categorías" },
      },
      {
        path: "compras",
        component: () => import("@/modules/compras/pages/ComprasView.vue"),
        meta: { title: "Compras" },
      },
      {
        path: "ventas",
        component: () => import("@/modules/ventas/pages/VentasView.vue"),
        meta: { title: "Ventas" },
      },
      {
        path: "cuentas-cobrar",
        component: () =>
          import("@/modules/finanzas/pages/CuentasPorCobrarView.vue"),
        meta: { title: "Cuentas por cobrar" },
      },
      {
        path: "cuentas-pagar",
        component: () =>
          import("@/modules/finanzas/pages/CuentasPorPagarView.vue"),
        meta: { title: "Cuentas por pagar" },
      },
      {
        path: "reportes",
        component: () => import("@/modules/reportes/pages/ReportesView.vue"),
        meta: { title: "Reportes" },
      },
      {
        path: "configuracion",
        component: () =>
          import("@/modules/configuracion/pages/ConfiguracionView.vue"),
        meta: { title: "Configuración" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return "/login";
  }

  if (to.path === "/login" && isAuthenticated()) {
    return "/dashboard";
  }
});

export default router;
