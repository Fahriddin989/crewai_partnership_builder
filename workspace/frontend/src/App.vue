<template><AppLayout v-if="auth.authenticated" /><router-view v-else /></template>
<script setup>
import AppLayout from './layouts/AppLayout.vue'
import { useAuthStore } from './stores/auth'
const auth = useAuthStore()
</script>
