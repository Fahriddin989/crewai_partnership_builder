import axios from 'axios'

const client = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000' })
let refreshPromise = null

client.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

function clearAuthentication() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  window.dispatchEvent(new Event('auth:logout'))
}

client.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    const refreshToken = localStorage.getItem('refresh_token')
    const url = originalRequest?.url || ''
    const isAuthRequest = url.includes('/api/auth/token/')
    const isRefreshRequest = url.includes('/api/auth/token/refresh/')

    if (error.response?.status !== 401 || !originalRequest || originalRequest._retry || !refreshToken || isAuthRequest || isRefreshRequest) {
      return Promise.reject(error)
    }

    originalRequest._retry = true
    try {
      refreshPromise ||= client.post('/api/auth/token/refresh/', { refresh: refreshToken })
      const { data } = await refreshPromise
      refreshPromise = null
      localStorage.setItem('access_token', data.access)
      originalRequest.headers.Authorization = `Bearer ${data.access}`
      return client(originalRequest)
    } catch (refreshError) {
      refreshPromise = null
      clearAuthentication()
      window.location.assign('/login')
      return Promise.reject(refreshError)
    }
  },
)

export default client
