import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import OrganizationsView from '../views/OrganizationsView.vue'
import OrganizationDetailView from '../views/OrganizationDetailView.vue'
import AgreementDetailView from '../views/AgreementDetailView.vue'

const router = createRouter({ history: createWebHistory(), routes: [
  { path: '/login', component: LoginView, meta: { guest: true } },
  { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
  { path: '/organizations', component: OrganizationsView, meta: { requiresAuth: true } },
  { path: '/organizations/:id', component: OrganizationDetailView, meta: { requiresAuth: true } },
  { path: '/agreements/:id', component: AgreementDetailView, meta: { requiresAuth: true } },
  { path: '/', redirect: '/dashboard' },
]})
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.authenticated) return '/login'
  if (to.meta.guest && auth.authenticated) return '/dashboard'
})
export default router
