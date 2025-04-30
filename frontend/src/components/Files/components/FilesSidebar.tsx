import React, { useEffect, useState } from 'react';
import { Box, Heading, Divider, useToast } from '@chakra-ui/react';
import { useFilesStore } from 'state/filesStore';
import { useChatStore } from 'state/chatStore';
import { fetchFiles, deleteFile } from 'api/filesApi';
import { FileUpload, FilesList, FileErrorAlert } from 'components/Files';
import { AdminPanel } from 'components/Admin';

const FilesSidebar = () => {
  const files = useFilesStore((state) => state.files);
  const setFiles = useFilesStore((state) => state.setFiles);
  const loading = useFilesStore((state) => state.loading);
  const setLoading = useFilesStore((state) => state.setLoading);
  const error = useFilesStore((state) => state.error);
  const setError = useFilesStore((state) => state.setError);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const toast = useToast();

  useEffect(() => {
    const loadFiles = async () => {
      setLoading(true);
      try {
        const backendFiles = await fetchFiles();
        setFiles(backendFiles);
        setError(null);
      } catch (err: any) {
        setError(err?.toString() || 'Failed to fetch files');
      } finally {
        setLoading(false);
      }
    };
    loadFiles();
  }, [setFiles, setLoading, setError]);

  // Show backend warning/error message if present
  const handleDelete = async (id: number) => {
    setDeletingId(id);
    try {
      const resp = await deleteFile(id);
      const updatedFiles = files.filter((f) => f.id !== id);
      setFiles(updatedFiles);
      if (resp && resp.warnings && resp.warnings.length > 0) {
        setError(resp.warnings.join('\n'));
        toast({ title: 'File deleted with warnings', description: resp.warnings.join('\n'), status: 'warning', duration: 4000, isClosable: true });
      } else {
        setError(null);
        toast({ title: 'File deleted', status: 'success', duration: 2000, isClosable: true });
      }
      if (updatedFiles.length === 0) {
        useChatStore.getState().clearChat();
      }
    } catch (error: any) {
      // Prefer backend error message if present
      const msg = error?.response?.data?.detail || error?.message || 'File deletion failed';
      setError(msg);
      toast({ title: 'File deletion failed', description: msg, status: 'error', duration: 4000, isClosable: true });
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <Box display="flex" flexDirection="column" h={{ base: '100dvh', md: '100vh' }} minW={{ base: '100vw', md: '320px' }} maxW={{ base: '100vw', md: '400px' }} p={0} bg="white" boxShadow={{ base: 'none', md: 'md' }}>
      <Box p={{ base: 3, md: 4 }} pb={0}>
        <Heading size="md" mb={4} fontSize={{ base: 'lg', md: 'xl' }}>Local RAG</Heading>
        <FileUpload />
        <Divider my={4} />
        <FileErrorAlert error={error} />
      </Box>
      <Box flex={1} px={{ base: 2, md: 4 }} overflowY="auto" minH={0}>
        <FilesList files={files} loading={loading} deletingId={deletingId} onDelete={handleDelete} />
      </Box>
      <Box p={{ base: 2, md: 4 }} pt={0} mb={{ base: 2, md: 4 }} borderTopWidth={1} borderColor="gray.100" bg="white" boxShadow="sm" borderRadius="lg">
        <React.Suspense fallback={null}>
          {typeof window !== 'undefined' && <AdminPanel />}
        </React.Suspense>
      </Box>
    </Box>
  );
};

export default FilesSidebar;
