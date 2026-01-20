import { describe, it, expect, beforeEach } from 'vitest';
import { ChatStore, InMemoryStorage, type StorageAdapter, type Message, type MessageListener } from '../src/ChatStore';

class MockStorage implements StorageAdapter {
  private data = new Map<string, Message[]>();

  async save(conversationId: string, messages: Message[]): Promise<void> {
    this.data.set(conversationId, JSON.parse(JSON.stringify(messages)));
  }

  async load(conversationId: string): Promise<Message[]> {
    return JSON.parse(JSON.stringify(this.data.get(conversationId) || []));
  }
}

describe('ChatStore', () => {
  it('can send and retrieve messages', async () => {
    const store = new ChatStore();
    const msg = await store.sendMessage('conv1', 'Hello', 'user1');

    expect(msg.content).toBe('Hello');
    expect(msg.userId).toBe('user1');

    const messages = await store.getMessages('conv1');
    expect(messages).toHaveLength(1);
    expect(messages[0].content).toBe('Hello');
  });

  it('persists messages through storage adapter', async () => {
    const storage = new MockStorage();
    const store1 = new ChatStore(storage);

    await store1.sendMessage('conv1', 'Message 1', 'user1');
    await store1.sendMessage('conv1', 'Message 2', 'user2');

    const store2 = new ChatStore(storage);
    const messages = await store2.getMessages('conv1');

    expect(messages).toHaveLength(2);
    expect(messages[0].content).toBe('Message 1');
    expect(messages[1].content).toBe('Message 2');
  });

  it('reloads messages from storage after refresh', async () => {
    const storage = new MockStorage();
    const store = new ChatStore(storage);

    await store.sendMessage('conv1', 'Original', 'user1');
    
    const reloaded = await store.reload('conv1');
    expect(reloaded).toHaveLength(1);
    expect(reloaded[0].content).toBe('Original');
  });

  it('notifies subscribers of new messages in real-time', async () => {
    const storage = new MockStorage();
    const storeA = new ChatStore(storage);
    const storeB = new ChatStore(storage);

    const receivedMessages: Message[] = [];
    storeA.subscribe('conv1', (message) => {
      receivedMessages.push(message);
    });

    await storeB.sendMessage('conv1', 'Hello from B', 'userB');

    expect(receivedMessages).toHaveLength(0);
  });

  it('allows unsubscribing from message notifications', async () => {
    const store = new ChatStore();
    const receivedMessages: Message[] = [];

    const unsubscribe = store.subscribe('conv1', (message) => {
      receivedMessages.push(message);
    });

    await store.sendMessage('conv1', 'First', 'user1');
    expect(receivedMessages).toHaveLength(1);

    unsubscribe();

    await store.sendMessage('conv1', 'Second', 'user1');
    expect(receivedMessages).toHaveLength(1);
  });

  it('notifies multiple subscribers for the same conversation', async () => {
    const store = new ChatStore();
    const received1: Message[] = [];
    const received2: Message[] = [];

    store.subscribe('conv1', (msg) => received1.push(msg));
    store.subscribe('conv1', (msg) => received2.push(msg));

    await store.sendMessage('conv1', 'Broadcast', 'user1');

    expect(received1).toHaveLength(1);
    expect(received2).toHaveLength(1);
    expect(received1[0].content).toBe('Broadcast');
    expect(received2[0].content).toBe('Broadcast');
  });
});
