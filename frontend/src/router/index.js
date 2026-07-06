import { createRouter, createWebHistory } from "vue-router";
import { isAuthenticated } from "@/modules/auth/authService";

import LoginView from "@/modules/auth/pages/LoginView.vue";
import DashboardView from "@/modules/dashboard/pages/DashboardView.vue";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    component: LoginView,
  },
  {
    path: "/dashboard",
    component: DashboardView,
    meta: {
      requiresAuth: true,
    },
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
});

export default router;