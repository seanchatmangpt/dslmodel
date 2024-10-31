// composables/useChannel.js

import {ref, onMounted, onBeforeUnmount} from 'vue'
import {useNuxtApp} from '#app'

export function useChannel(channelName) {
  const {$socket} = useNuxtApp()
  const messages = ref([])

  /**
   * Send a message to the specified channel.
   * @param {any} content - The content of the message.
   */
  const sendMessage = (content) => {
    if ($socket?.connected) {
      $socket.emit('publish', {content, channel: channelName})
    } else {
      console.warn('Socket not connected. Cannot send message.')
    }
  }

  /**
   * Handle incoming messages from the channel.
   * @param {Object} data - The message data.
   */
  const handleMessage = (data) => {
    messages.value.push(data)
  }

  onMounted(() => {
    if ($socket) {
      $socket.on(channelName, handleMessage)
    }
  })

  onBeforeUnmount(() => {
    if ($socket) {
      $socket.off(channelName, handleMessage)
    }
  })

  return {
    sendMessage,
    messages,
  }
}
