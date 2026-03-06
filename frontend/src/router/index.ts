import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: () => import("@/views/GenerateView.vue"),
    },
    {
      path: "/archive",
      component: () => import("@/views/ArchiveView.vue"),
    },
  ],
});

export default router;
