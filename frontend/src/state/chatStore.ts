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
  sendChat: (
    question: string,
    options?: {
      fileId?: string | null;
      keywords?: string[];
      metadataFilter?: Record<string, any>;
      k?: number;
    }
  ) => Promise<void>;
}

import { sendChat as sendChatApi } from '../api/chatApi';

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  loading: false,
  error: null,
  sendMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  receiveMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  clearChat: () => set({ messages: [] }),
  /**
   * Send a chat message with hybrid retrieval options.
   * Accepts (question, fileId?, keywords?, metadataFilter?, useMMR?, k?) or legacy (question, fileId?).
   */
  sendChat: async (
    question: string,
    options?: {
      fileId?: string | null;
      keywords?: string[];
      metadataFilter?: Record<string, any>;
      k?: number;
    }
  ) => {
    set({ loading: true, error: null });
    try {
      set((state) => ({ messages: [...state.messages, { sender: 'user', text: question }] }));
      // Use options-object-based API only
      const response = await sendChatApi({
        question,
        ...options,
      });
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
