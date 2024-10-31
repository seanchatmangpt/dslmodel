// // composables/useMessaging.js
// import {ref, onMounted, onUnmounted, inject} from "vue";
//
// export function useMessaging() {
//   const messages = ref([]); // Reactive array for messages
//   const socket = inject("socket"); // Inject the socket plugin
//
//   if (!socket) {
//     throw new Error("Socket plugin not available. Ensure the plugin is properly registered.");
//   }
//
//   // Function to handle incoming messages
//   const handleIncomingMessage = (topic, message) => {
//     messages.value.push({topic, ...message});
//     console.log(`Received message on '${topic}':`, message);
//   };
//
//   // Subscribe to topics
//   const subscribeToTopics = () => {
//     socket.subscribe("promotions", (msg) => handleIncomingMessage("promotions", msg));
//     socket.subscribe("limited-offers", (msg) => handleIncomingMessage("limited-offers", msg));
//     console.log("Subscribed to 'promotions' and 'limited-offers' topics");
//   };
//
//   // Connect and subscribe on mount
//   onMounted(() => {
//     socket.connect(); // Ensure socket is connected
//     subscribeToTopics();
//   });
//
//   // Disconnect on unmount
//   onUnmounted(() => {
//     socket.disconnect();
//   });
//
//   return {
//     messages,
//   };
// }
