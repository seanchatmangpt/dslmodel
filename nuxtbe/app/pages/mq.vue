<!-- pages/index.vue -->
<template>
  <div class="container">
    <h1>Nuxt.js Socket.IO and HTTP Client</h1>
    <PublishMessage/>
    <ReceiveMessages/>
  </div>
</template>

<script setup>
import PublishMessage from '~/components/PublishMessage.vue'
import ReceiveMessages from '~/components/ReceiveMessages.vue'
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px;
}

h1 {
  text-align: center;
  margin-bottom: 40px;
}
</style>
