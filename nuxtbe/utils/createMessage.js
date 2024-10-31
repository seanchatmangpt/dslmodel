// utils/createMessage.js

/**
 * Generates a UUID for message ID.
 * @returns {string} A UUID string.
 */
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (char) => {
    const random = (Math.random() * 16) | 0
    const value = char === 'x' ? random : (random & 0x3) | 0x8
    return value.toString(16)
  })
}

/**
 * Creates a message object with default values.
 * @param {Object} params - Parameters for message creation.
 * @param {*} params.content - The content of the message.
 * @param {string|null} [params.topic=null] - The topic of the message.
 * @param {string|null} [params.channel=null] - The channel of the message.
 * @param {string} [params.routingKey='default-slug'] - The routing key.
 * @param {string} [params.contentType='application/json'] - The content type.
 * @param {string} [params.sender='system'] - The sender of the message.
 * @param {string|null} [params.messageType=null] - The type of the message.
 * @param {Object} [params.attributes={}] - Additional attributes.
 * @param {*} [params.rawData=null] - Raw data of the message.
 * @returns {Object} The created message object.
 */
export function createMessage({
                                content,
                                topic = null,
                                channel = null,
                                routingKey = 'default-slug',
                                contentType = 'application/json',
                                sender = 'system',
                                messageType = null,
                                attributes = {},
                                rawData = null,
                              }) {
  return {
    id: generateUUID(),
    topic,
    channel,
    routingKey,
    contentType,
    content,
    sender,
    timestamp: new Date().toISOString(),
    messageType,
    attributes,
    rawData: rawData || content,
  }
}
