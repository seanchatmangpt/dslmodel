// nuxtbe/app/composables/useSSE.js
import {ref, onBeforeUnmount} from 'vue'
import {useRuntimeConfig} from '#app' // Import to access runtime config

export function useSSE(route) {
  const config = useRuntimeConfig() // Access the runtime config
  const url = `${config.public.FASTAPI_URL}${route}` // Construct the full URL

  const messages = ref([]) // Array to store received messages
  const loading = ref(false) // Loading state
  let eventSource = null // Variable to hold EventSource instance

  const start = () => {
    loading.value = true // Set loading to true
    messages.value = [] // Clear previous messages

    // Create a new EventSource connection
    eventSource = new EventSource(url)

    // Handle incoming messages
    eventSource.onmessage = (event) => {
      messages.value.push(event.data) // Add new message
    }

    // Handle errors
    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error)
      loading.value = false // Stop loading on error
      eventSource.close() // Close the connection
    }

    // Set loading to false when connection opens
    eventSource.onopen = () => {
      loading.value = false // Stop loading when the connection opens
    }
  }

  // Cleanup when the component is destroyed
  onBeforeUnmount(() => {
    if (eventSource) {
      eventSource.close() // Close connection on component unmount
    }
  })

  return {
    messages,
    loading,
    start
  }
}
