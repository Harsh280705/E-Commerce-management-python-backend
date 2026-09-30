<template>
  <div class="card">
    <h3>{{ product.title }}</h3>
    <div class="muted" style="font-size:13px">{{ product.sku }}</div>
    <p class="muted" style="font-size:14px">{{ product.description }}</p>
    <div class="price">₹{{ Number(product.price).toFixed(2) }}</div>
    <div class="row">
      <router-link class="btn" :to="`/products/${product.id}`">Details</router-link>
      <button class="btn primary" @click="$emit('add', product)">Add to cart</button>
    </div>
  </div>
</template>
<script setup>
defineProps({ product: Object })
defineEmits(['add'])
</script>
