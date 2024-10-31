// utils/publishMessage.js
export async function publishMessage(message) {
  const config = useRuntimeConfig(); // Access runtime config for the URL
  const url = config.public.FASTAPI_URL; // No prefix needed

  try {
    const response = await fetch(`${url}/publish_message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message),
    });

    if (!response.ok) {
      throw new Error(`Failed to publish message: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("Message published successfully:", data);
    return data;
  } catch (error) {
    console.error("Error publishing message:", error);
    throw error;
  }
}
