<!-- components/ReceiveMessages.vue -->
<template>
  <div>
    <h2>Received Messages</h2>
    <div v-if="healthMessages.length">
      <h3>Health Topic Messages:</h3>
      <ul>
        <li v-for="(msg, index) in healthMessages" :key="index">{{ msg.content }}</li>
      </ul>
    </div>
    <div v-if="emailMessages.length">
      <h3>Email Channel Messages:</h3>
      <ul>
        <li v-for="(msg, index) in emailMessages" :key="index">{{ msg.content }}</li>
      </ul>
    </div>
    <div v-if="!healthMessages.length && !emailMessages.length">
      <p>No messages received yet.</p>
    </div>
  </div>
</template>

<script setup>
import {useTopic} from '~/composables/useTopic'
import {useChannel} from '~/composables/useChannel'

const {messages: healthMessages} = useTopic('health')
const {messages: emailMessages} = useChannel('notification/email')
</script>

<style scoped>
h3 {
  margin-top: 20px;
}

ul {
  list-style-type: disc;
  margin-left: 20px;
}
</style>
