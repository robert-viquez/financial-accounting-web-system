import { createRouter, createWebHistory } from "vue-router";
import { isAuthenticated } from "@/modules/auth/authService";

import LoginView from "@/modules/auth/pages/LoginView.vue";
import SetupView from "@/modules/auth/pages/SetupView.vue";
import { getSetupRequired } from "@/modules/auth/setupService";
import { resolveSetupNavigation } from "@/modules/auth/setupFlow";
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
    path: "/setup",
    component: SetupView,
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
        meta: { titleKey: "navigation.home" },
      },
      {
        path: "clientes",
        component: () => import("@/modules/clientes/pages/ClientesView.vue"),
        meta: { titleKey: "navigation.customers" },
      },
      {
        path: "proveedores",
        component: () =>
          import("@/modules/proveedores/pages/ProveedoresView.vue"),
        meta: { titleKey: "navigation.suppliers" },
      },
      {
        path: "inventario",
        component: () => import("@/modules/inventario/pages/ProductosView.vue"),
        meta: { titleKey: "navigation.inventory" },
      },
      {
        path: "movimientos-inventario",
        component: () =>
          import("@/modules/inventario/pages/MovimientosView.vue"),
        meta: { titleKey: "navigation.movements" },
      },
      {
        path: "categorias",
        component: () => import("@/modules/inventario/pages/CategoriasView.vue"),
        meta: { titleKey: "navigation.categories" },
      },
      {
        path: "compras",
        component: () => import("@/modules/compras/pages/ComprasView.vue"),
        meta: { titleKey: "navigation.purchases" },
      },
      {
        path: "ventas",
        component: () => import("@/modules/ventas/pages/VentasView.vue"),
        meta: { titleKey: "navigation.sales" },
      },
      {
        path: "cuentas-cobrar",
        component: () =>
          import("@/modules/finanzas/pages/CuentasPorCobrarView.vue"),
        meta: { titleKey: "navigation.receivables" },
      },
      {
        path: "cuentas-pagar",
        component: () =>
          import("@/modules/finanzas/pages/CuentasPorPagarView.vue"),
        meta: { titleKey: "navigation.payables" },
      },
      {
        path: "contabilidad",
        component: () =>
          import("@/modules/contabilidad/pages/ContabilidadView.vue"),
        meta: { titleKey: "navigation.accounting" },
      },
      {
        path: "reportes",
        component: () => import("@/modules/reportes/pages/ReportesView.vue"),
        meta: { titleKey: "navigation.reports" },
      },
      {
        path: "configuracion",
        component: () =>
          import("@/modules/configuracion/pages/ConfiguracionView.vue"),
        meta: { titleKey: "navigation.settings" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  try {
    const setupRedirect = resolveSetupNavigation({
      setupRequired: await getSetupRequired(),
      path: to.path,
      authenticated: isAuthenticated(),
    });
    if (setupRedirect) return setupRedirect;
  } catch {
    // Preserve the existing login flow when setup status cannot be reached.
  }

  if (to.meta.requiresAuth && !isAuthenticated()) {
    return "/login";
  }

  if (to.path === "/login" && isAuthenticated()) {
    return "/dashboard";
  }
});

export default router;
