<template>
  <div>
    <h2>Real-time Messaging Interface</h2>

    <!-- Subscription Management -->
    <div>
      <h3>Manage Subscriptions</h3>
      <UInput v-model="subscriptionName" placeholder="Enter topic or channel name"/>
      <UButton @click="subscribeToEvent">Subscribe</UButton>
      <UButton @click="unsubscribeFromEvent">Unsubscribe</UButton>
    </div>

    <!-- Send Test Message -->
    <div>
      <h3>Send Test Message</h3>
      <UButton @click="sendTestMessage">Send Test Message</UButton>
    </div>

    <!-- Publish Custom Message -->
    <div>
      <h3>Publish Custom Message</h3>
      <UInput v-model="customMessage.content" placeholder="Message content"/>
      <UInput v-model="customMessage.topic" placeholder="Topic (optional)"/>
      <UInput v-model="customMessage.channel" placeholder="Channel (optional)"/>
      <UInput v-model="customMessage.sender" placeholder="Sender (optional)"/>
      <UInput v-model="customMessage.routingKey" placeholder="Routing Key (optional)"/>
      <UButton @click="publishCustomMessage">Publish Message</UButton>
    </div>

    <!-- Message Log Display -->
    <div>
      <h3>Messages</h3>
      <ul>
        <li v-for="msg in messages" :key="msg.id">
          <strong>{{ msg.event || msg.topic || msg.channel }}:</strong>
          <span>{{ msg.sender }} - {{ msg.content }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import {useMessageHandler} from '@/composables/useMessageHandler';

// Composable functions and data
const {messages, sendTestMessage, publishMessage, subscribe, unsubscribe} = useMessageHandler();

// Local state for UI UInputs
const subscriptionName = ref('');
const customMessage = ref({
  content: '',
  topic: '',
  channel: '',
  sender: 'user',
  routingKey: 'default-slug',
});

// Functions to handle user actions
const subscribeToEvent = () => {
  if (subscriptionName.value) {
    subscribe(subscriptionName.value);
    console.log(`Subscribed to: ${subscriptionName.value}`);
  }
};

const unsubscribeFromEvent = () => {
  if (subscriptionName.value) {
    unsubscribe(subscriptionName.value);
    console.log(`Unsubscribed from: ${subscriptionName.value}`);
  }
};

const publishCustomMessage = () => {
  const messageInput = {
    content: customMessage.value.content,
    topic: customMessage.value.topic || undefined,
    channel: customMessage.value.channel || undefined,
    sender: customMessage.value.sender,
    routing_key: customMessage.value.routingKey,
  };
  publishMessage(messageInput).then(() => {
    console.log('Custom message published');
  });
};
</script>
