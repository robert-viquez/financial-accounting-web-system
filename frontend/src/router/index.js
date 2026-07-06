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
      },
      {
      path: "clientes",
      component: () => import("@/modules/clientes/pages/ClientesView.vue"),
      },
      {
      path: "proveedores",
      component: () => import("@/modules/proveedores/pages/ProveedoresView.vue"),
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