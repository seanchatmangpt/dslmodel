<template>
  <div>
    <h1>Socket.IO with Nuxt and Python</h1>
    <button @click="sendMessage">Send Message</button>
    <p v-if="response">{{ response }}</p>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue';
import {useSocket} from 'nuxt-socket-io/composables';

const response = ref(null);
const {$io} = useSocket('main');

// Listen for incoming messages from the server
$io.on('message_from_server', (msg) => {
  response.value = `Received from server: ${msg}`;
});

// Function to send a message to the server
const sendMessage = () => {
  $io.emit('message_from_client', 'Hello from Nuxt!');
};
</script>
