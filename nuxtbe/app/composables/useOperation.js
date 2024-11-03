// composables/useOperation.js
import { camelize } from 'inflection'
import { Subject } from 'rxjs'
import { useNuxtApp } from '#app'

export function useOperation(eventName) {
  const { $socket } = useNuxtApp()
  const sendMethod = `send${camelize(eventName)}`
  const receiveMethod = `receive${camelize(eventName)}`
  const receiveObservableMethod = `observe${camelize(eventName)}`

  console.log('Generated method names:', { sendMethod, receiveMethod, receiveObservableMethod })

  // Send function for emitting events
  const send = (data) => {
    console.log(`Sending data on event ${eventName}:`, data)
    return new Promise((resolve, reject) => {
      $socket.emit(eventName, data, (response) => {
        console.log(`Acknowledgment received for ${eventName}:`, response)
        if (response && response.error) {
          reject(response.error)
        } else {
          resolve(response)
        }
      })
    })
  }

  // Callback-based receive function for simple cases
  const receive = (callback) => {
    const listener = (data) => {
      console.log(`Data received on event ${eventName}_ack:`, data)
      callback(data)
    }
    console.log(`Setting up listener for ${eventName}_ack`)
    $socket.on(`${eventName}_ack`, listener)

    // Return an unsubscribe function
    return () => {
      console.log(`Removing listener for ${eventName}_ack`)
      $socket.off(`${eventName}_ack`, listener)
    }
  }

  // RxJS-based observable receive function
  const receiveObservable = () => {
    const subject = new Subject()

    const listener = (data) => {
      console.log(`Data received on event ${eventName}_ack (observable):`, data)
      subject.next(data)
    }

    console.log(`Setting up RxJS listener for ${eventName}_ack`)
    $socket.on(`${eventName}_ack`, listener)

    // Return the observable and an unsubscribe function
    const observable = subject.asObservable()
    const unsubscribe = () => {
      console.log(`Removing RxJS listener for ${eventName}_ack`)
      $socket.off(`${eventName}_ack`, listener)
      subject.complete() // Complete the subject to clean up resources
    }

    return { observable, unsubscribe }
  }

  return {
    [sendMethod]: send,
    [receiveMethod]: receive,
    [receiveObservableMethod]: receiveObservable
  }
}
