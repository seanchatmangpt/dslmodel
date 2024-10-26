import { defineNuxtPlugin } from "#app";
import annyang from "annyang";

export default defineNuxtPlugin((nuxtApp) => {
  console.log("plugins/voice.client.js", "annyang", annyang);
  nuxtApp.provide("annyang", annyang);
  window.annyang = annyang; // Ensure annyang is available on the window object
});
