// ~/composables/useWebSocket.js
import {ref, onBeforeUnmount} from 'vue';

export function useWebSocket(url) {
  const messages = ref([]);
  let socket;

  const connect = () => {
    socket = new WebSocket(url);

    // Handle incoming messages
    socket.onmessage = (event) => {
      messages.value.push(event.data);
    };

    // Handle errors
    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      socket.close();
    };

    // Auto-reconnect on close
    socket.onclose = () => {
      console.log("WebSocket closed. Reconnecting in 5 seconds...");
      setTimeout(connect, 5000); // Reconnect after 5 seconds
    };
  };

  // Initialize WebSocket connection
  connect();

  // Close WebSocket when the component using it is destroyed
  onBeforeUnmount(() => {
    if (socket) socket.close();
  });

  // Method to send messages to the WebSocket server
  const sendMessage = (message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(message);
    }
  };

  return {messages, sendMessage};
}
