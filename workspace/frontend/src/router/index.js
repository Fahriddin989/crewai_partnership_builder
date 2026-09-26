import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import OrganizationsView from '../views/OrganizationsView.vue'

const router = createRouter({ history: createWebHistory(), routes: [
  { path: '/login', component: LoginView, meta: { guest: true } },
  { path: '/organizations', component: OrganizationsView, meta: { requiresAuth: true } },
  { path: '/', redirect: '/organizations' },
]})
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.authenticated) return '/login'
  if (to.meta.guest && auth.authenticated) return '/organizations'
})
export default router
