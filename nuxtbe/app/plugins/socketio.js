// plugins/socketio.js

import {io} from 'socket.io-client'
import {defineNuxtPlugin, useRuntimeConfig} from '#app'

export default defineNuxtPlugin((nuxtApp) => {
  // Access runtime configuration if needed
  const config = useRuntimeConfig()
  const socketUrl = config.public.SOCKET_URL || 'http://localhost:8000' // Ensure it matches your server URL

  // Initialize Socket.IO client
  const socket = io(socketUrl, {
    autoConnect: false, // Prevent auto-connect; connect manually later
  })

  // Connect when the app is mounted
  nuxtApp.hook('app:mounted', () => {
    socket.connect()
  })

  // Disconnect when the app is unmounted
  nuxtApp.hook('app:beforeUnmount', () => {
    if (socket.connected) {
      socket.disconnect()
    }
  })

  // Provide the socket instance to the whole app
  nuxtApp.provide('socket', socket)

  // Example connection and error logging
  socket.on('connect', () => {
    console.log('Socket.IO connected:', socket.id)
  })

  socket.on('disconnect', () => {
    console.log('Socket.IO disconnected')
  })

  socket.on('connect_error', (error) => {
    console.error('Socket.IO connection error:', error)
  })
})
