<template>
  <span class="badge" :class="status">{{ status }}</span>
</template>
<script setup>
defineProps({ status: String })
</script>
