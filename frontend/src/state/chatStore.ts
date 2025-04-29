import { create } from 'zustand';

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  sources?: string[];
}

interface ChatState {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  sendMessage: (msg: ChatMessage) => void;
  receiveMessage: (msg: ChatMessage) => void;
  clearChat: () => void;
  sendChat: (question: string, fileId?: string | null) => Promise<void>;
}

import { sendChat as sendChatApi } from '../api/chatApi';

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  loading: false,
  error: null,
  sendMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  receiveMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  clearChat: () => set({ messages: [] }),
  sendChat: async (question, fileId = null) => {
    set({ loading: true, error: null });
    try {
      // Add user message
      set((state) => ({ messages: [...state.messages, { sender: 'user', text: question }] }));
      const response = await sendChatApi(fileId, question);
      set((state) => ({
        messages: [...state.messages, { sender: 'ai', text: response.answer, sources: response.sources }],
        loading: false,
        error: null,
      }));
    } catch (err: any) {
      set({ loading: false, error: typeof err === 'string' ? err : 'Chat failed' });
    }
  },
}));
