import React, { useEffect, useState } from 'react';
import { Box, Heading, VStack, Text, Divider, Spinner, Alert, AlertIcon, useToast } from '@chakra-ui/react';
import { useFilesStore } from '../../state/filesStore';
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

  const handleDelete = async (id: number) => {
    setDeletingId(id);
    try {
      await deleteFile(id);
      setFiles(files.filter((f) => f.id !== id));
      toast({ title: 'File deleted', status: 'success', duration: 2000 });
    } catch (err: any) {
      setError(err?.toString() || 'Failed to delete file');
      toast({ title: 'Delete failed', description: err?.toString(), status: 'error', duration: 4000 });
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <Box p={4} height="100vh" overflowY="auto">
      <Heading size="md" mb={4}>Files</Heading>
      <FileUpload />
      <Divider my={4} />
      {error && (
        <Alert status="error" mb={2} borderRadius="md">
          <AlertIcon />
          {error}
        </Alert>
      )}
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
  );
};

export default FilesSidebar;
