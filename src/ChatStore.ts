export interface Message {
  id: string;
  conversationId: string;
  content: string;
  timestamp: number;
  userId: string;
}

export interface StorageAdapter {
  save(conversationId: string, messages: Message[]): Promise<void>;
  load(conversationId: string): Promise<Message[]>;
}

export type MessageListener = (message: Message) => void;

export class InMemoryStorage implements StorageAdapter {
  private storage = new Map<string, Message[]>();

  async save(conversationId: string, messages: Message[]): Promise<void> {
    this.storage.set(conversationId, messages);
  }

  async load(conversationId: string): Promise<Message[]> {
    return this.storage.get(conversationId) || [];
  }
}

export class LocalStorageAdapter implements StorageAdapter {
  async save(conversationId: string, messages: Message[]): Promise<void> {
    localStorage.setItem(`chat_${conversationId}`, JSON.stringify(messages));
  }

  async load(conversationId: string): Promise<Message[]> {
    const data = localStorage.getItem(`chat_${conversationId}`);
    return data ? JSON.parse(data) : [];
  }
}

export class ChatStore {
  private messages = new Map<string, Message[]>();
  private storage: StorageAdapter;
  private listeners = new Map<string, Set<MessageListener>>();

  constructor(storage?: StorageAdapter) {
    this.storage = storage || new InMemoryStorage();
  }

  async sendMessage(conversationId: string, content: string, userId: string): Promise<Message> {
    const message: Message = {
      id: crypto.randomUUID(),
      conversationId,
      content,
      timestamp: Date.now(),
      userId,
    };

    const messages = await this.getMessages(conversationId);
    messages.push(message);
    this.messages.set(conversationId, messages);
    await this.storage.save(conversationId, messages);

    this.notifyListeners(conversationId, message);

    return message;
  }

  async getMessages(conversationId: string): Promise<Message[]> {
    if (!this.messages.has(conversationId)) {
      const loaded = await this.storage.load(conversationId);
      this.messages.set(conversationId, loaded);
    }
    return this.messages.get(conversationId) || [];
  }

  async reload(conversationId: string): Promise<Message[]> {
    const loaded = await this.storage.load(conversationId);
    this.messages.set(conversationId, loaded);
    return loaded;
  }

  subscribe(conversationId: string, listener: MessageListener): () => void {
    if (!this.listeners.has(conversationId)) {
      this.listeners.set(conversationId, new Set());
    }
    this.listeners.get(conversationId)!.add(listener);

    return () => {
      const listeners = this.listeners.get(conversationId);
      if (listeners) {
        listeners.delete(listener);
      }
    };
  }

  private notifyListeners(conversationId: string, message: Message): void {
    const listeners = this.listeners.get(conversationId);
    if (listeners) {
      listeners.forEach(listener => listener(message));
    }
  }
}
