export default defineEventHandler(async (event) => {
  const storage = useStorage("sharedData");
  const { filename } = getQuery(event);

  const content = await storage.getItem(filename);
  return content ? { filename, content } : { error: "File not found" };
});
