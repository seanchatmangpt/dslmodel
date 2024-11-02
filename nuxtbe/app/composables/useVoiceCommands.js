import { onMounted, onUnmounted, ref } from 'vue'

export function useVoiceCommands(customCommands = {}) {
  const isListening = ref(false)

  const startListening = () => {
    console.log(
      'composables/useVoiceCommands.js',
      'startListening',
      window.annyang
    )
    if (typeof window !== 'undefined' && window.annyang) {
      console.log('Starting annyang and setting up commands')
      console.log('customCommands', customCommands)
      window.annyang.addCommands(customCommands)
      window.annyang.start()
      isListening.value = true
      console.log('Annyang started')
    }
  }

  const stopListening = () => {
    if (typeof window !== 'undefined' && window.annyang) {
      window.annyang.abort()
      isListening.value = false
      console.log('Annyang stopped')
    }
  }

  onMounted(() => {
    startListening()
  })

  onUnmounted(() => {
    stopListening()
  })

  return {
    isListening,
    startListening,
    stopListening
  }
}
