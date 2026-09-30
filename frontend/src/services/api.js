import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001',
  timeout: 15000
})

export const usersApi = {
  list: () => api.get('/api/users').then(r => r.data),
  create: (payload) => api.post('/api/users', payload).then(r => r.data)
}

export const productsApi = {
  list: (params = {}) => api.get('/api/products', { params }).then(r => r.data),
  get: (id) => api.get(`/api/products/${id}`).then(r => r.data),
  create: (payload) => api.post('/api/products', payload).then(r => r.data),
  update: (id, payload) => api.put(`/api/products/${id}`, payload).then(r => r.data),
  remove: (id) => api.delete(`/api/products/${id}`).then(r => r.data)
}

export const ordersApi = {
  create: (payload) => api.post('/api/orders', payload).then(r => r.data),
  list: (params = {}) => api.get('/api/orders', { params }).then(r => r.data),
  get: (id) => api.get(`/api/orders/${id}`).then(r => r.data),
  updateStatus: (id, status) => api.put(`/api/orders/${id}/status`, { status }).then(r => r.data)
}

export const searchApi = {
  orders: (params = {}) => api.get('/api/search/orders', { params }).then(r => r.data),
  health: () => api.get('/api/search/health').then(r => r.data)
}

export default api
