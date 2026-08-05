import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';

export const useChatStore = create(
  persist(
    (set) => ({
      sessionId: uuidv4(),
      messages: [],
      addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
      clearMessages: () => set({ messages: [], sessionId: uuidv4() }),
    }),
    {
      name: 'trendly-chat-storage', // name of item in the storage (must be unique)
    }
  )
);
