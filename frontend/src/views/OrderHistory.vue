<template>
  <h1 class="page-title">My orders</h1>
  <div class="toolbar">
    <select class="input" v-model="status" @change="load">
      <option value="">All statuses</option>
      <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
    </select>
  </div>
  <div v-if="loading" class="skeleton" />
  <div v-else-if="error" class="alert error">{{ error }}</div>
  <div v-else-if="!orders.length"><EmptyState title="No orders" message="Your orders will appear here." /></div>
  <div v-else class="card" style="padding:0">
    <table class="tbl">
      <thead><tr><th>Order</th><th>Date</th><th>Status</th><th>Total</th><th /></tr></thead>
      <tbody>
        <tr v-for="o in orders" :key="o.id">
          <td>#{{ o.id }}</td>
          <td class="muted">{{ fmtDate(o.created_at) }}</td>
          <td><StatusBadge :status="o.status" /></td>
          <td>₹{{ Number(o.total).toFixed(2) }}</td>
          <td><router-link class="btn" :to="`/orders/${o.id}`">Open</router-link></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { ordersApi } from '../services/api.js'
import { store } from '../services/store.js'
import StatusBadge from '../components/StatusBadge.vue'
import EmptyState from '../components/EmptyState.vue'

const statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
const orders = ref([])
const status = ref('')
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (store.user) params.user_id = store.user.id
    if (status.value) params.status = status.value
    orders.value = await ordersApi.list(params)
  } catch {
    error.value = 'Could not load orders.'
  } finally {
    loading.value = false
  }
}

function fmtDate(d) {
  return d ? new Date(d).toLocaleString() : '—'
}

onMounted(load)
</script>
