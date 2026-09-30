<template>
  <h1 class="page-title">Products</h1>
  <div v-if="error" class="alert error">{{ error }}</div>
  <div v-if="ok" class="alert ok">{{ ok }}</div>
  <div class="card" style="margin-bottom:16px">
    <h3>{{ editing ? 'Edit product' : 'New product' }}</h3>
    <div class="row">
      <input class="input" v-model="form.sku" placeholder="SKU" :disabled="editing" style="max-width:160px" />
      <input class="input" v-model="form.title" placeholder="Title" style="max-width:260px" />
      <input class="input" v-model.number="form.price" type="number" min="0.01" step="0.01" placeholder="Price" style="max-width:140px" />
    </div>
    <input class="input" v-model="form.description" placeholder="Description" style="margin-top:10px" />
    <div class="row" style="margin-top:10px">
      <button class="btn primary" @click="save">{{ editing ? 'Update' : 'Create' }}</button>
      <button v-if="editing" class="btn" @click="reset">Cancel</button>
    </div>
  </div>
  <div class="card" style="padding:0">
    <table class="tbl">
      <thead><tr><th>SKU</th><th>Title</th><th>Price</th><th /></tr></thead>
      <tbody>
        <tr v-for="p in products" :key="p.id">
          <td class="muted">{{ p.sku }}</td>
          <td>{{ p.title }}</td>
          <td>₹{{ Number(p.price).toFixed(2) }}</td>
          <td class="row">
            <button class="btn" @click="edit(p)">Edit</button>
            <button class="btn danger" @click="remove(p)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { productsApi } from '../services/api.js'

const products = ref([])
const error = ref('')
const ok = ref('')
const editing = ref(null)
const form = ref({ sku: '', title: '', description: '', price: 0 })

async function load() {
  products.value = await productsApi.list({}).catch(() => [])
}

function edit(p) {
  editing.value = p.id
  form.value = { sku: p.sku, title: p.title, description: p.description, price: p.price }
}

function reset() {
  editing.value = null
  form.value = { sku: '', title: '', description: '', price: 0 }
}

async function save() {
  error.value = ''
  ok.value = ''
  try {
    if (editing.value) {
      await productsApi.update(editing.value, { title: form.value.title, description: form.value.description, price: Number(form.value.price) })
      ok.value = 'Product updated.'
    } else {
      await productsApi.create({ ...form.value, price: Number(form.value.price) })
      ok.value = 'Product created.'
    }
    reset()
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Save failed.'
  }
}

async function remove(p) {
  if (!confirm(`Delete "${p.title}"?`)) return
  error.value = ''
  try {
    await productsApi.remove(p.id)
    ok.value = 'Product deleted.'
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Delete failed.'
  }
}

onMounted(load)
</script>
