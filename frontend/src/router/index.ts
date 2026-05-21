import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/callback",
      name: "callback",
      component: () => import("@/views/Callback.vue"),
    },
    {
      path: "/",
      component: () => import("@/components/AppLayout.vue"),
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          name: "dashboard",
          component: () => import("@/views/Dashboard.vue"),
        },
        {
          path: "applications",
          name: "my-applications",
          component: () => import("@/views/MyApplications.vue"),
        },
        {
          path: "applications/new",
          name: "create-application",
          component: () => import("@/views/CreateApplication.vue"),
        },
        {
          path: "applications/:id",
          name: "application-detail",
          component: () => import("@/views/ApplicationDetail.vue"),
        },
        {
          path: "approvals",
          name: "pending-approvals",
          component: () => import("@/views/PendingApprovals.vue"),
        },
        {
          path: "audit",
          name: "audit",
          component: () => import("@/views/AuditPage.vue"),
        },
      ],
    },
  ],
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();

  if (to.name === "callback") {
    return true;
  }

  if (authStore.loading) {
    await authStore.checkAuth();
  }

  if (to.meta.requiresAuth && !authStore.user) {
    authStore.login();
    return false;
  }

  return true;
});

export default router;