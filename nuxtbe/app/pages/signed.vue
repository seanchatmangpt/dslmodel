<template>
  <div>
    <button @click="handleSignUp">
      Send Sign Up
    </button>
    <div v-if="receivedData">
      Callback Data: {{ receivedData }}
    </div>
    <div v-if="observedData">
      Observable Data: {{ observedData }}
    </div>
  </div>
</template>

<script setup>
import { onUnmounted, ref } from 'vue'
import { useOperation } from '@/composables/useOperation'

const { sendUserSignedUp, receiveUserSignedUp, observeUserSignedUp } = useOperation('userSignedUp')

const receivedData = ref(null)
const observedData = ref(null)

// Callback-based receive example
const unsubscribeCallback = receiveUserSignedUp((data) => {
  receivedData.value = data
  console.log('Received additional data from server (callback):', data)
})

// Observable-based receive example
const { observable, unsubscribe: unsubscribeObservable } = observeUserSignedUp()
const subscription = observable.subscribe((data) => {
  observedData.value = data
  console.log('Received additional data from server (observable):', data)
})

// Send data to server
const handleSignUp = async () => {
  try {
    const response = await sendUserSignedUp({
      fullName: 'John Doe',
      email: 'john@example.com',
      age: 30
    })
    console.log('Server acknowledgment:', response)
  } catch (error) {
    console.error('Validation error:', error)
  }
}

// Cleanup on component unmount
onUnmounted(() => {
  unsubscribeCallback()
  unsubscribeObservable()
  subscription.unsubscribe()
})
</script>
