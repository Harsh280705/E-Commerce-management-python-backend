<template>
  <h1 class="page-title">Cart</h1>
  <div v-if="!store.cart.length">
    <EmptyState title="Your cart is empty" message="Add some products to get started.">
      <div style="margin-top:12px"><router-link class="btn primary" to="/">Browse products</router-link></div>
    </EmptyState>
  </div>
  <div v-else class="card">
    <table class="tbl">
      <thead><tr><th>Product</th><th>Price</th><th>Qty</th><th>Total</th><th /></tr></thead>
      <tbody>
        <tr v-for="l in store.cart" :key="l.product.id">
          <td>{{ l.product.title }}</td>
          <td>₹{{ Number(l.product.price).toFixed(2) }}</td>
          <td><input class="input" style="width:70px" type="number" min="1" :value="l.qty" @change="setQty(l.product.id, Number($event.target.value))" /></td>
          <td>₹{{ (Number(l.product.price) * l.qty).toFixed(2) }}</td>
          <td><button class="btn danger" @click="removeFromCart(l.product.id)">Remove</button></td>
        </tr>
      </tbody>
    </table>
    <div class="row" style="justify-content:space-between;margin-top:14px">
      <strong>Total: ₹{{ cartTotal.toFixed(2) }}</strong>
      <router-link class="btn primary" to="/checkout">Proceed to checkout</router-link>
    </div>
  </div>
</template>
<script setup>
import { store, cartTotal, removeFromCart, setQty } from '../services/store.js'
import EmptyState from '../components/EmptyState.vue'
</script>
