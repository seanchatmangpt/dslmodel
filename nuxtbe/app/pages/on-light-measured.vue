<template>
  <div>
    <button @click="handleOnLightMeasured">
      Send OnLightMeasured
    </button>
    <div v-if="receivedData">
      Callback Data:
    </div>
    <div v-if="observedData">
      Observable Data:
    </div>
  </div>
</template>

<script setup>
import { useOperation } from '@/composables/useOperation'

const { sendOnLightMeasured, receiveOnLightMeasured, observeOnLightMeasured } = useOperation('onLightMeasured')

const receivedData = ref(null)
const observedData = ref(null)

// Callback-based receive example
const unsubscribeCallback = receiveOnLightMeasured((data) => {
  receivedData.value = data
  console.log('Received data (callback):', data)
})

// Observable-based receive example
const { observable, unsubscribe: unsubscribeObservable } = observeOnLightMeasured()
const subscription = observable.subscribe((data) => {
  observedData.value = data
  console.log('Received data (observable):', data)
})

// Send data to server
const handleOnLightMeasured = async () => {
  try {
    const response = await sendOnLightMeasured({
      id: 'id',
      lumens: 'lumens',
      sentAt: 'sentAt'
    })
    console.log('Server acknowledgment:', response)
  } catch (error) {
    console.error('Error:', error)
  }
}

// Cleanup on component unmount
onUnmounted(() => {
  unsubscribeCallback()
  unsubscribeObservable()
  subscription.unsubscribe()
})
</script>
