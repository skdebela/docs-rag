import { create } from 'zustand';

export interface FileMeta {
  id: number;
  filename: string;
  upload_time: string;
  metadata: any;
}

interface FilesState {
  files: FileMeta[];
  loading: boolean;
  error: string | null;
  setFiles: (files: FileMeta[]) => void;
  addFile: (file: FileMeta) => void;
  removeFile: (id: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearFiles: () => void;
}

export const useFilesStore = create<FilesState>((set) => ({
  files: [],
  loading: false,
  error: null,
  setFiles: (files) => set({ files }),
  addFile: (file) => set((state) => ({ files: [...state.files, file] })),
  // Only remove from local state after backend confirms deletion
removeFile: (id) => set((state) => ({ files: state.files.filter((f) => f.id !== id) })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearFiles: () => set({ files: [] }),
}));
