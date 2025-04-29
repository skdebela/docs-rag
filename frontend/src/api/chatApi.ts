import axios from 'axios';

export const sendChat = async (fileId: string | null, question: string) => {
  try {
    const params = new URLSearchParams();
    params.append('question', question);
    if (fileId) params.append('file_id', fileId);
    const response = await axios.post(`/api/chat?${params.toString()}`);
    return response.data;
  } catch (error: any) {
    throw error?.response?.data?.detail || 'Chat request failed';
  }
};
