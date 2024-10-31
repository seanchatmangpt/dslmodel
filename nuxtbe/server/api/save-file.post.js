export default defineEventHandler(async (event) => {
  const storage = useStorage("sharedData"); // Using 'sharedData' Redis storage
  const { filename, content } = await readBody(event); // Read data from POST request

  await storage.setItem(filename, content); // Save content to Redis under the filename key

  return { message: `File ${filename} saved to Redis`, content };
});
