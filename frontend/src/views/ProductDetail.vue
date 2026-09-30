<template>
  <router-link class="btn" to="/">← Back</router-link>
  <div v-if="loading" class="skeleton" style="margin-top:14px" />
  <div v-else-if="error" class="alert error" style="margin-top:14px">{{ error }}</div>
  <div v-else-if="product" class="card" style="margin-top:14px">
    <h1 class="page-title">{{ product.title }}</h1>
    <div class="muted">{{ product.sku }}</div>
    <p>{{ product.description }}</p>
    <div class="price">₹{{ Number(product.price).toFixed(2) }}</div>
    <div class="row">
      <input class="input" style="width:90px" type="number" min="1" v-model.number="qty" />
      <button class="btn primary" @click="addToCart(product, qty); $router.push('/cart')">Add to cart</button>
    </div>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { productsApi } from '../services/api.js'
import { addToCart } from '../services/store.js'

const route = useRoute()
const product = ref(null)
const loading = ref(true)
const error = ref('')
const qty = ref(1)

onMounted(async () => {
  try {
    product.value = await productsApi.get(route.params.id)
  } catch {
    error.value = 'Product not found.'
  } finally {
    loading.value = false
  }
})
</script>
