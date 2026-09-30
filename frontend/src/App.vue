<template>
  <div>
    <header class="topbar">
      <div class="topbar-inner">
        <router-link class="logo" to="/">Northwind Store</router-link>
        <nav class="nav">
          <router-link to="/">Shop</router-link>
          <router-link to="/orders">My Orders</router-link>
          <router-link to="/admin">Admin</router-link>
        </nav>
        <div class="spacer" />
        <span v-if="store.user" class="muted" style="color:#c9d2ea;font-size:13px">{{ store.user.name }}</span>
        <router-link class="cart-pill" to="/cart">Cart · {{ cartCount }}</router-link>
      </div>
    </header>
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { store } from './services/store.js'
import { cartCount } from './services/store.js'
</script>
