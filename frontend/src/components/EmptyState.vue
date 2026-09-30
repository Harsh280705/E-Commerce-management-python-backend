<template>
  <div class="card" style="text-align:center;padding:36px">
    <h3 style="margin-bottom:6px">{{ title }}</h3>
    <p class="muted">{{ message }}</p>
    <slot />
  </div>
</template>
<script setup>
defineProps({ title: { type: String, default: 'Nothing here yet' }, message: { type: String, default: '' } })
</script>
