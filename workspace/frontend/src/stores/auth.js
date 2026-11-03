import { defineStore } from 'pinia'
import client from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({ accessToken: localStorage.getItem('access_token'), refreshToken: localStorage.getItem('refresh_token'), user: null }),
  getters: { authenticated: state => !!state.accessToken },
  actions: {
    async login(username, password) {
      const { data } = await client.post('/api/auth/token/', { username, password })
      this.accessToken = data.access
      this.refreshToken = data.refresh
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      await this.loadCurrentUser()
    },
    async loadCurrentUser() {
      if (!this.accessToken) return null
      const { data } = await client.get('/api/auth/me/')
      this.user = data
      return data
    },
    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
  },
})
