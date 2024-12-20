<script setup>
import { ref, onMounted } from 'vue';
import { useFetch } from '#app';

const props = defineProps({
  name: {
    type: String,
    default: 'World'
  }
});

const { data: weatherData, pending, error } = await useFetch('https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY');

const weatherInfo = ref(null);

onMounted(async () => {
  if (weatherData.value) {
    weatherInfo.value = {
      temperature: weatherData.value.main.temp,
      humidity: weatherData.value.main.humidity,
      windSpeed: weatherData.value.wind.speed,
      weatherDescription: weatherData.value.weather[0].description
    };
  }
});
</script>

<template>
  <div>
    <h1>Hello, {{ name }}!</h1>
    <div v-if="$fetchState.pending">Loading...</div>
    <div v-else-if="$fetchState.error">Error: {{ $fetchState.error.message }}</div>
    <div v-else>
      <h2>Weather Data:</h2>
      <ul>
        <li v-for="(value, key) in weatherData" :key="key">
          {{ key }}: {{ value }}
        </li>
      </ul>
    </div>
  </div>
</template>
<style scoped>
</style>