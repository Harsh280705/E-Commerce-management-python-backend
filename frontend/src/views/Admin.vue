<template>
  <div class="layout-2">
    <aside class="side">
      <router-link to="/admin">Dashboard</router-link>
      <router-link to="/admin/products">Products</router-link>
      <router-link to="/admin/orders">Orders & Search</router-link>
    </aside>
    <section><router-view /></section>
  </div>
</template>
