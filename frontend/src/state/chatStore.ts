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
    fileId?: string | null,
    keywords?: string[],
    metadataFilter?: Record<string, any>,
    k?: number
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
    fileId?: string | null,
    keywords?: string[],
    metadataFilter?: Record<string, any>,
    useMMR?: boolean,
    k?: number
  ) => {
    set({ loading: true, error: null });
    try {
      set((state) => ({ messages: [...state.messages, { sender: 'user', text: question }] }));
      // If any advanced options provided, use new API signature
      if (keywords || metadataFilter || k !== undefined) {
        const response = await sendChatApi({
          question,
          fileId,
          keywords,
          metadataFilter,

          k,
        });
        set((state) => ({
          messages: [...state.messages, { sender: 'ai', text: response.answer, sources: response.sources }],
          loading: false,
          error: null,
        }));
      } else {
        // Legacy usage
        const response = await sendChatApi(fileId ?? null, question);
        set((state) => ({
          messages: [...state.messages, { sender: 'ai', text: response.answer, sources: response.sources }],
          loading: false,
          error: null,
        }));
      }
    } catch (err: any) {
      set({ loading: false, error: typeof err === 'string' ? err : 'Chat failed' });
    }
  },
}));
