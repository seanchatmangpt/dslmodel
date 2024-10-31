// composables/useTopic.js

import {ref, onMounted, onBeforeUnmount} from 'vue'
import {useNuxtApp} from '#app'

export function useTopic(topicName) {
  const {$socket} = useNuxtApp()
  const messages = ref([])

  /**
   * Send a message to the specified topic.
   * @param {any} content - The content of the message.
   */
  const sendMessage = (content) => {
    if ($socket?.connected) {
      $socket.emit('publish', {content, topic: topicName})
    } else {
      console.warn('Socket not connected. Cannot send message.')
    }
  }

  /**
   * Handle incoming messages from the topic.
   * @param {Object} data - The message data.
   */
  const handleMessage = (data) => {
    messages.value.push(data)
  }

  onMounted(() => {
    if ($socket) {
      $socket.on(topicName, handleMessage)
    }
  })

  onBeforeUnmount(() => {
    if ($socket) {
      $socket.off(topicName, handleMessage)
    }
  })

  return {
    sendMessage,
    messages,
  }
}
