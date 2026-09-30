<template>
  <h1 class="page-title">Orders & search</h1>
  <p class="muted">Powered by Elasticsearch. Open an order for canonical PostgreSQL details.</p>
  <div class="toolbar">
    <input class="input" v-model="q" placeholder='Search: "harsh", "ORD-1024", "delivered"…' @input="debounced" />
    <select class="input" v-model="status" @change="run">
      <option value="">All statuses</option>
      <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
    </select>
    <input class="input" v-model="customer" placeholder="Customer filter" @input="debounced" />
    <select class="input" v-model="sort" @change="run">
      <option value="newest">Newest</option>
      <option value="oldest">Oldest</option>
      <option value="total_desc">Total ↓</option>
      <option value="total_asc">Total ↑</option>
    </select>
  </div>
  <div v-if="error" class="alert error">{{ error }}</div>
  <div v-else-if="searched && !results.length"><EmptyState title="No matches" message="Try a different term or clear filters." /></div>
  <div v-else-if="results.length" class="card" style="padding:0">
    <table class="tbl">
      <thead><tr><th>Order</th><th>Customer</th><th>Status</th><th>Total</th><th>Items</th><th /></tr></thead>
      <tbody>
        <tr v-for="r in results" :key="r.order_id">
          <td>#{{ r.order_id }}</td>
          <td>{{ r.customer_name }}</td>
          <td><StatusBadge :status="r.status" /></td>
          <td>₹{{ Number(r.total_amount).toFixed(2) }}</td>
          <td class="muted">{{ (r.items || []).map(i => `${i.title}×${i.quantity}`).join(', ') }}</td>
          <td><router-link class="btn" :to="`/admin/orders/${r.order_id}`">Open</router-link></td>
        </tr>
      </tbody>
    </table>
    <div class="row" style="padding:12px">
      <span class="muted">{{ total }} result(s)</span>
    </div>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { searchApi } from '../services/api.js'
import StatusBadge from '../components/StatusBadge.vue'
import EmptyState from '../components/EmptyState.vue'

const statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
const q = ref('')
const status = ref('')
const customer = ref('')
const sort = ref('newest')
const results = ref([])
const total = ref(0)
const searched = ref(false)
const error = ref('')

let timer
function debounced() {
  clearTimeout(timer)
  timer = setTimeout(run, 300)
}

async function run() {
  error.value = ''
  try {
    const params = { sort: sort.value }
    if (q.value) params.q = q.value
    if (status.value) params.status = status.value
    if (customer.value) params.customer = customer.value
    const data = await searchApi.orders(params)
    results.value = data.results
    total.value = data.total
    searched.value = true
  } catch (e) {
    error.value = e.response?.status === 503
      ? 'Search is unavailable (Elasticsearch down). Orders in PostgreSQL are safe; the worker will catch up.'
      : 'Search failed.'
  }
}

onMounted(run)
</script>
