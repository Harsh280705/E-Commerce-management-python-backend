<template>
  <router-link class="btn" to="/orders">← Orders</router-link>
  <div v-if="loading" class="skeleton" style="margin-top:14px" />
  <div v-else-if="error" class="alert error" style="margin-top:14px">{{ error }}</div>
  <div v-else-if="order" style="margin-top:14px">
    <h1 class="page-title">Order #{{ order.id }}</h1>
    <p class="muted">Canonical details from PostgreSQL · {{ fmtDate(order.created_at) }}</p>
    <div class="row"><StatusBadge :status="order.status" /><span class="muted">{{ order.customer_name }}</span></div>
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
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ordersApi } from '../services/api.js'
import StatusBadge from '../components/StatusBadge.vue'

const route = useRoute()
const order = ref(null)
const loading = ref(true)
const error = ref('')

function fmtDate(d) {
  return d ? new Date(d).toLocaleString() : '—'
}

onMounted(async () => {
  try {
    order.value = await ordersApi.get(route.params.id)
  } catch {
    error.value = 'Order not found.'
  } finally {
    loading.value = false
  }
})
</script>
