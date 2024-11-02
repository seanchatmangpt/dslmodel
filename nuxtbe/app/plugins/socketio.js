// plugins/socketio.js
import { io } from 'socket.io-client'
import { Subject } from 'rxjs'
import { defineNuxtPlugin, useRuntimeConfig } from '#app'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const socketUrl = config.public.SOCKET_URL || 'http://localhost:8000'

  // Initialize Socket.IO client
  const socket = io(socketUrl, {
    autoConnect: false
  })

  // RxJS subjects to emit socket events as observables
  const connectSubject = new Subject()
  const disconnectSubject = new Subject()
  const messageSubject = new Subject()

  // Socket.IO connection events
  socket.on('connect', () => {
    console.log('Socket.IO connected:', socket.id)
    connectSubject.next(socket.id)
  })

  socket.on('disconnect', () => {
    console.log('Socket.IO disconnected')
    disconnectSubject.next()
  })

  // Generic message handler
  socket.on('message', (data) => {
    console.log('Message received:', data)
    messageSubject.next(data)
  })

  // Connect the socket when the app is mounted
  nuxtApp.hook('app:mounted', () => {
    socket.connect()
  })

  // Disconnect the socket when the app is unmounted
  nuxtApp.hook('app:beforeUnmount', () => {
    if (socket.connected) {
      socket.disconnect()
    }
  })

  // Provide socket and RxJS observables to the entire app
  nuxtApp.provide('socket', socket)
  nuxtApp.provide('socketObservables', {
    connect$: connectSubject.asObservable(),
    disconnect$: disconnectSubject.asObservable(),
    message$: messageSubject.asObservable()
  })
})
