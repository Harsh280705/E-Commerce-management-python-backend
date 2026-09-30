<template>
  <h1 class="page-title">Admin dashboard</h1>
  <div v-if="health" class="alert" :class="health.elasticsearch === 'up' ? 'ok' : 'error'">
    Elasticsearch: {{ health.elasticsearch }}
    <span v-if="health.indexed_orders !== null && health.indexed_orders !== undefined"> · {{ health.indexed_orders }} orders indexed</span>
    <span v-else> · search may lag while the worker catches up (eventual consistency)</span>
  </div>
  <div class="grid">
    <div class="card"><div class="muted">Total orders (PG)</div><h2>{{ stats.orders }}</h2></div>
    <div class="card"><div class="muted">Products</div><h2>{{ stats.products }}</h2></div>
    <div class="card"><div class="muted">Revenue</div><h2>₹{{ stats.revenue.toFixed(2) }}</h2></div>
  </div>
  <div class="card" style="margin-top:16px">
    <h3>Architecture reminder</h3>
    <p class="muted" style="font-size:14px">
      PostgreSQL is the source of truth. Writes commit first, then a sync task goes to RabbitMQ;
      Celery re-reads PostgreSQL and upserts Elasticsearch (doc id = order id). Search reads ES;
      order details always read PostgreSQL.
    </p>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { ordersApi, productsApi, searchApi } from '../services/api.js'

const stats = ref({ orders: 0, products: 0, revenue: 0 })
const health = ref(null)

onMounted(async () => {
  health.value = await searchApi.health().catch(() => ({ elasticsearch: 'down' }))
  const [orders, products] = await Promise.all([
    ordersApi.list({ size: 100 }).catch(() => []),
    productsApi.list({}).catch(() => [])
  ])
  stats.value = {
    orders: orders.length,
    products: products.length,
    revenue: orders.reduce((s, o) => s + Number(o.total || 0), 0)
  }
})
</script>
