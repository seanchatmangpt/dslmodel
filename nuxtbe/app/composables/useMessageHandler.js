import {ref, onMounted, onUnmounted} from "vue";
import {io} from "socket.io-client"; // Import Socket.IO client for WebSocket support

export function useMessageHandler() {
  const messages = ref([]); // Reactive array to store incoming messages
  const socket = ref(null); // Socket.IO instance, initialized later
  const baseUrl = "http://localhost:8000"; // Backend URL, change if necessary

  // Function to initialize WebSocket connection with Socket.IO
  const connectSocket = () => {
    console.log("Connecting to socket");
    // // Connect to backend WebSocket server at /socket.io with 'websocket' as the only transport
    socket.value = io(`${baseUrl}`, {
      // Ensure the path matches the server's configuration
      transports: ['websocket'], // Forces use of WebSocket protocol only
    });

    // Listen for all events on WebSocket
    socket.value.onAny((event, msg) => {
      console.log(`Received event: ${event}, message: ${JSON.stringify(msg)}`);
      handleMessage(event, msg); // Handle each received event by passing it to handleMessage
    });

    // Debugging: Log successful connection to WebSocket
    socket.value.on("connect", () =>
      console.log("Connected to WebSocket server")
    );

    // Debugging: Log disconnection events
    socket.value.on("disconnect", () =>
      console.log("Disconnected from WebSocket server")
    );
  };

  // Function to process and store incoming messages in the messages array
  const handleMessage = (event, msg) => {
    messages.value.push({...msg, event}); // Store message with event name for context
    console.log(`Message stored: ${JSON.stringify(msg)}`); // Log the stored message
  };

  // Function to dynamically subscribe to specific topic or channel events
  const subscribe = (eventName) => {
    if (socket.value) {
      // Register event listener for specific topic or channel
      socket.value.on(eventName, (msg) => handleMessage(eventName, msg));
      console.log(`Subscribed to event: ${eventName}`); // Debugging: log subscription
    }
  };

  // Function to unsubscribe from a specific topic or channel
  const unsubscribe = (eventName) => {
    if (socket.value) {
      // Remove event listener for specific topic or channel
      socket.value.off(eventName);
      console.log(`Unsubscribed from event: ${eventName}`); // Debugging: log unsubscription
    }
  };

  // Function to send a test message using the /send_message endpoint
  const sendTestMessage = async () => {
    try {
      // Call the backend endpoint using $fetch with base URL
      const data = await $fetch("/send_message", {baseURL: baseUrl});
      console.log("Test message sent successfully:", data); // Debugging: log successful test message
      return data; // Return data for further use if needed
    } catch (error) {
      // Catch and log any errors during the request
      console.error("Error sending test message:", error);
    }
  };

  // Function to publish a custom message using the /publish_message endpoint
  const publishMessage = async (messageInput) => {
    try {
      // Post custom message data to the backend
      const data = await $fetch("/publish_message", {
        baseURL: baseUrl,
        method: "POST", // Specify HTTP POST method for creating messages
        body: messageInput, // Pass messageInput data in request body
      });
      console.log("Custom message published successfully:", data); // Debugging: log successful publication
      return data; // Return response data
    } catch (error) {
      // Catch and log any errors during the request
      console.error("Error publishing custom message:", error);
    }
  };

  // Automatically connect to WebSocket when component is mounted
  onMounted(() => connectSocket());

  // Disconnect from WebSocket when component is unmounted to avoid memory leaks
  onUnmounted(() => {
    if (socket.value) {
      socket.value.disconnect(); // Disconnect from WebSocket
      console.log("WebSocket connection closed"); // Debugging: log disconnection
    }
  });

  // Return reactive data and functions for use in the component
  return {
    messages, // Array of messages received from WebSocket
    sendTestMessage, // Function to send test message via HTTP endpoint
    publishMessage, // Function to publish custom message via HTTP endpoint
    subscribe, // Function to dynamically subscribe to topics/channels
    unsubscribe, // Function to unsubscribe from topics/channels
  };
}
