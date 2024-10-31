// models/Message.js

export class Message {
  constructor({
                content,
                topic = null,
                channel = null,
                routingKey = "default-slug",
                contentType = "application/json",
                sender = "system",
                messageType = null,
                attributes = {},
                rawData = null,
              }) {
    this.id = generateUUID();
    this.topic = topic;
    this.channel = channel;
    this.routingKey = routingKey;
    this.contentType = contentType;
    this.content = content;
    this.sender = sender;
    this.timestamp = new Date().toISOString();
    this.messageType = messageType;
    this.attributes = attributes;
    this.rawData = rawData || content;
  }

  // Convert instance to JSON format
  toJSON() {
    return {
      id: this.id,
      topic: this.topic,
      channel: this.channel,
      routingKey: this.routingKey,
      contentType: this.contentType,
      content: this.content,
      sender: this.sender,
      timestamp: this.timestamp,
      messageType: this.messageType,
      attributes: this.attributes,
      rawData: this.rawData,
    };
  }
}
