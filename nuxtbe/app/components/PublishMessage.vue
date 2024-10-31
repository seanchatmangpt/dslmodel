<!-- components/PublishMessage.vue -->
<template>
  <div>
    <h2>Publish Message</h2>
    <input v-model="content" placeholder="Enter message content"/>
    <button @click="publishToHealth">Publish to Health Topic</button>
    <button @click="publishToEmailChannel">Publish to Email Channel</button>
  </div>
</template>

<script setup>
import {ref} from 'vue'
import {useTopic} from '~/composables/useTopic'
import {useChannel} from '~/composables/useChannel'

const content = ref('')

// Initialize composables
const {sendMessage: sendToHealth} = useTopic('health')
const {sendMessage: sendToEmailChannel} = useChannel('notification/email')

// Functions to publish messages
const publishToHealth = () => {
  if (content.value.trim() === '') {
    alert('Please enter a message content.')
    return
  }
  sendToHealth(content.value)
  content.value = ''
}

const publishToEmailChannel = () => {
  if (content.value.trim() === '') {
    alert('Please enter a message content.')
    return
  }
  sendToEmailChannel(content.value)
  content.value = ''
}
</script>

<style scoped>
input {
  padding: 8px;
  margin-right: 8px;
  width: 300px;
}

button {
  padding: 8px 16px;
  margin-right: 8px;
}
</style>
