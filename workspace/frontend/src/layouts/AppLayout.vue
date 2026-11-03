<template>
  <div class="app-shell">
    <aside class="sidebar"><div class="brand">Partnership Management</div><nav><RouterLink to="/dashboard">Dashboard</RouterLink><RouterLink to="/organizations">Organizations</RouterLink></nav></aside>
    <main class="main"><header><strong>Partnership Management</strong><div class="user-area"><span>{{ userName }}</span><button @click="logout">Logout</button></div></header><section class="content"><router-view /></section></main>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore(); const router = useRouter()
const userName = computed(() => auth.user?.name || auth.user?.username || 'User')
function logout() { auth.logout(); router.push('/login') }
</script>
