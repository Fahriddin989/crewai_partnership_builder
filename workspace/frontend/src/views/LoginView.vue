<template><main class="login-page"><form class="login-card" @submit.prevent="submit"><h1>Partnership Management</h1><p>Sign in to continue</p><label>Username<input v-model="username" required autocomplete="username" /></label><label>Password<input v-model="password" type="password" required autocomplete="current-password" /></label><p v-if="error" class="error">{{ error }}</p><button class="primary" :disabled="loading">{{ loading ? 'Signing in…' : 'Sign in' }}</button></form></main></template>
<script setup>
import { ref } from 'vue'; import { useRouter } from 'vue-router'; import { useAuthStore } from '../stores/auth'
const username=ref(''), password=ref(''), error=ref(''), loading=ref(false); const router=useRouter(); const auth=useAuthStore()
async function submit(){ loading.value=true; error.value=''; try { await auth.login(username.value,password.value); router.push('/dashboard') } catch { error.value='Unable to sign in. Check your username and password.' } finally { loading.value=false } }
</script>
