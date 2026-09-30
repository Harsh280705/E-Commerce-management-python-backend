<template>
  <h1 class="page-title">Shop</h1>
  <p class="muted">Browse the catalog, search products, and place orders.</p>

  <div class="toolbar">
    <input class="input" v-model="q" placeholder="Search products…" @input="load" />
    <select class="input" v-model="userId" @change="persistUser">
      <option :value="null">Select customer</option>
      <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }} ({{ u.email }})</option>
    </select>
  </div>

  <div v-if="loading" class="grid"><div class="skeleton" v-for="i in 6" :key="i" /></div>
  <div v-else-if="error" class="alert error">{{ error }}</div>
  <div v-else-if="!products.length">
    <EmptyState title="No products" message="Try a different search term." />
  </div>
  <div v-else class="grid">
    <ProductCard v-for="p in products" :key="p.id" :product="p" @add="onAdd" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { productsApi, usersApi } from '../services/api.js'
import { addToCart, store } from '../services/store.js'
import ProductCard from '../components/ProductCard.vue'
import EmptyState from '../components/EmptyState.vue'

const q = ref('')
const products = ref([])
const users = ref([])
const userId = ref(store.user?.id ?? null)
const loading = ref(false)
const error = ref('')

let timer
async function load() {
  clearTimeout(timer)
  timer = setTimeout(async () => {
    loading.value = true
    error.value = ''
    try {
      products.value = await productsApi.list(q.value ? { q: q.value } : {})
    } catch (e) {
      error.value = 'Could not load products. Is the API running?'
    } finally {
      loading.value = false
    }
  }, 200)
}

function onAdd(p) {
  addToCart(p)
}

function persistUser() {
  const u = users.value.find(x => x.id === Number(userId.value))
  if (u) store.setUser(u)
}

onMounted(async () => {
  loading.value = true
  try {
    const [prods, us] = await Promise.all([productsApi.list({}), usersApi.list()])
    products.value = prods
    users.value = us
    if (!store.user && us.length) {
      store.setUser(us[0])
      userId.value = us[0].id
    }
  } catch (e) {
    error.value = 'Could not load store. Start FastAPI on :8000.'
  } finally {
    loading.value = false
  }
})
</script>
