import React, { useEffect, useState } from 'react';
import { Box, Heading, VStack, Text, Divider, Spinner, Alert, AlertIcon, useToast } from '@chakra-ui/react';
import { useFilesStore } from '../../state/filesStore';
import { useChatStore } from '../../state/chatStore';
import { fetchFiles, deleteFile } from '../../api/filesApi';
import FilePill from './FilePill';
import FileUpload from './FileUpload';

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
    <Box display="flex" flexDirection="column" height="100vh" p={0}>
      <Box p={4} pb={0}>
        <Heading size="md" mb={4}>Files</Heading>
        <FileUpload />
        <Divider my={4} />
        {error && (
          <Alert status="error" mb={2} borderRadius="md">
            <AlertIcon />
            {error}
          </Alert>
        )}
      </Box>
      <Box flex={1} px={4}>
        {loading ? (
          <Spinner size="md" mx="auto" my={6} />
        ) : (
          <VStack align="stretch" spacing={2}>
            {(!Array.isArray(files) || files.length === 0) ? (
              <Text color="gray.400">No files uploaded yet.</Text>
            ) : (
              files.map((file) => (
                <FilePill
                  key={file.id}
                  file={file}
                  onDelete={handleDelete}
                  deleting={deletingId === file.id}
                />
              ))
            )}
          </VStack>
        )}
      </Box>
      <Box p={4} pt={0} mb={4} borderTopWidth={1} borderColor="gray.100" bg="white" boxShadow="sm" borderRadius="lg">
        <React.Suspense fallback={null}>
          {typeof window !== 'undefined' && <AdminPanel />}
        </React.Suspense>
      </Box>
    </Box>
  );
};

import AdminPanel from '../AdminPanel';
export default FilesSidebar;
