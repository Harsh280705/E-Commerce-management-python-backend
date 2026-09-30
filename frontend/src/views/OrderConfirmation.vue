<template>
  <div class="card" style="text-align:center;padding:40px">
    <div style="font-size:44px">✓</div>
    <h1 class="page-title">Order confirmed</h1>
    <p class="muted">Order <strong>#{{ $route.params.id }}</strong> is saved in PostgreSQL. Search sync follows shortly.</p>
    <div class="row" style="justify-content:center;margin-top:14px">
      <router-link class="btn primary" :to="`/orders/${$route.params.id}`">View order</router-link>
      <router-link class="btn" to="/">Continue shopping</router-link>
    </div>
  </div>
</template>
