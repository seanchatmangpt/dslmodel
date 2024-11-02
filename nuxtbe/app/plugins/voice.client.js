import annyang from 'annyang'
import { defineNuxtPlugin } from '#app'

export default defineNuxtPlugin((nuxtApp) => {
  console.log('plugins/voice.client.js', 'annyang', annyang)
  nuxtApp.provide('annyang', annyang)
  window.annyang = annyang // Ensure annyang is available on the window object
})
