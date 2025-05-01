import axios from 'axios';

export interface ChatOptions {
  question: string;
  fileId?: string | null;
  keywords?: string[];
  metadataFilter?: Record<string, any>;
  k?: number;
}

export const sendChat = async (
  optsOrFileId: ChatOptions | string | null,
  question?: string
) => {
  // Support both (fileId, question) and (ChatOptions) signatures
  let payload: any;
  if (
    optsOrFileId &&
    typeof optsOrFileId === 'object' &&
    ('question' in optsOrFileId || 'fileId' in optsOrFileId)
  ) {
    // New hybrid API usage
    const response = await axios.post('/api/chat', {
      question: optsOrFileId.question,
      file_id: optsOrFileId.fileId,
      keywords: optsOrFileId.keywords,
      metadata_filter: optsOrFileId.metadataFilter,
      k: optsOrFileId.k,
    });
    return response.data;
  }
  // Legacy usage
  payload = { question, file_id: optsOrFileId };
  try {
    const response = await axios.post('/api/chat', payload);
    return response.data;
  } catch (error: any) {
    throw error?.response?.data?.detail || 'Chat request failed';
  }
};
