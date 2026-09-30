<template>
  <h1 class="page-title">Checkout</h1>
  <div v-if="!store.cart.length" class="alert info">Your cart is empty.</div>
  <div v-else class="card" style="max-width:560px">
    <div v-if="error" class="alert error">{{ error }}</div>
    <label class="muted">Ordering as</label>
    <select class="input" v-model="userId">
      <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }} — {{ u.email }}</option>
    </select>
    <p class="muted" style="margin-top:12px">{{ store.cart.length }} line(s) · Total <strong>₹{{ cartTotal.toFixed(2) }}</strong></p>
    <button class="btn primary" :disabled="placing" @click="placeOrder">
      {{ placing ? 'Placing order…' : 'Place order' }}
    </button>
    <p class="muted" style="font-size:13px;margin-top:10px">
      The order commits to PostgreSQL first; search sync happens in the background via RabbitMQ + Celery.
    </p>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ordersApi, usersApi } from '../services/api.js'
import { store, cartTotal, clearCart } from '../services/store.js'

const router = useRouter()
const users = ref([])
const userId = ref(store.user?.id ?? null)
const placing = ref(false)
const error = ref('')

onMounted(async () => {
  users.value = await usersApi.list().catch(() => [])
  if (!userId.value && users.value.length) userId.value = users.value[0].id
})

async function placeOrder() {
  if (!userId.value) {
    error.value = 'Select a customer first.'
    return
  }
  placing.value = true
  error.value = ''
  try {
    const order = await ordersApi.create({
      user_id: userId.value,
      items: store.cart.map(l => ({ product_id: l.product.id, quantity: l.qty }))
    })
    clearCart()
    router.push(`/confirmation/${order.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Order failed. Check the API and try again.'
  } finally {
    placing.value = false
  }
}
</script>
