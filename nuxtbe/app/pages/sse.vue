<template>
  <div>
    <h2>Server-Sent Events Content</h2>
    <button @click="start">Load SSE Content</button>
    <div v-if="loading" class="spinner">Loading...</div>
    <div class="sse-content">
      <div v-for="(message, index) in messages" :key="index">{{ message }}</div>
    </div>
  </div>
</template>

<script setup>
import {useSSE} from '@/composables/useSSE'; // Adjust the import path if necessary

const {messages, loading, start} = useSSE('/sse'); // Just pass the route
</script>

<style scoped>
.spinner {
  border: 2px solid transparent;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
