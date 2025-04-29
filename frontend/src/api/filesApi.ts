import axios from 'axios';

export const uploadFile = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error: any) {
    throw error?.response?.data?.detail || 'File upload failed';
  }
};

export const fetchFiles = async () => {
  try {
    const response = await axios.get('/api/files');
    return response.data;
  } catch (error: any) {
    throw error?.response?.data?.detail || 'Fetching files failed';
  }
};

export const deleteFile = async (fileId: number) => {
  try {
    const response = await axios.delete(`/api/files/${fileId}`);
    return response.data;
  } catch (error: any) {
    throw error?.response?.data?.detail || 'File deletion failed';
  }
};
