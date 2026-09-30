<template>
  <router-link class="btn" to="/admin/orders">← Search</router-link>
  <div v-if="loading" class="skeleton" style="margin-top:14px" />
  <div v-else-if="error" class="alert error" style="margin-top:14px">{{ error }}</div>
  <div v-else-if="order" style="margin-top:14px">
    <h1 class="page-title">Order #{{ order.id }}</h1>
    <p class="muted">Canonical details from PostgreSQL.</p>
    <div v-if="ok" class="alert ok">{{ ok }}</div>
    <div class="row">
      <StatusBadge :status="order.status" />
      <select class="input" style="max-width:200px" v-model="nextStatus">
        <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
      </select>
      <button class="btn primary" :disabled="saving" @click="saveStatus">
        {{ saving ? 'Saving…' : 'Update status' }}
      </button>
    </div>
    <div class="card" style="margin-top:14px;padding:0">
      <table class="tbl">
        <thead><tr><th>Product</th><th>Qty</th><th>Unit price</th><th>Line total</th></tr></thead>
        <tbody>
          <tr v-for="it in order.items" :key="it.id">
            <td>{{ it.product_title }}</td>
            <td>{{ it.quantity }}</td>
            <td>₹{{ Number(it.price).toFixed(2) }}</td>
            <td>₹{{ (Number(it.price) * it.quantity).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <h3>Total: ₹{{ Number(order.total).toFixed(2) }}</h3>
    <p class="muted" style="font-size:13px">Status commits to PostgreSQL first, then re-syncs to Elasticsearch.</p>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ordersApi } from '../services/api.js'
import StatusBadge from '../components/StatusBadge.vue'

const statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
const route = useRoute()
const order = ref(null)
const nextStatus = ref('')
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const ok = ref('')

async function load() {
  loading.value = true
  try {
    order.value = await ordersApi.get(route.params.id)
    nextStatus.value = order.value.status
  } catch {
    error.value = 'Order not found.'
  } finally {
    loading.value = false
  }
}

async function saveStatus() {
  saving.value = true
  error.value = ''
  ok.value = ''
  try {
    order.value = await ordersApi.updateStatus(order.value.id, nextStatus.value)
    ok.value = 'Status updated. Search index will catch up shortly.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Update failed.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
