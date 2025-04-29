
import React, { useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Text, Spinner, useToast } from '@chakra-ui/react';
import { useFilesStore } from '../../state/filesStore';
import { uploadFile } from '../../api/filesApi';

const SUPPORTED_EXTENSIONS = ['pdf', 'docx', 'txt', 'csv', 'xlsx'];
const MAX_SIZE_MB = 20;

const FileUpload = () => {
  const addFile = useFilesStore((state) => state.addFile);
  const setLoading = useFilesStore((state) => state.setLoading);
  const setError = useFilesStore((state) => state.setError);
  const loading = useFilesStore((state) => state.loading);
  const toast = useToast();
  const uploading = useRef(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      if (!file.name) {
        setError('File name is missing.');
        continue;
      }
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (!ext || !SUPPORTED_EXTENSIONS.includes(ext)) {
        toast({ title: 'Unsupported file type', status: 'error', duration: 4000 });
        continue;
      }
      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        toast({ title: 'File too large', status: 'error', duration: 4000 });
        continue;
      }
      setLoading(true);
      uploading.current = true;
      try {
        const uploaded = await uploadFile(file);
        addFile(uploaded);
        toast({ title: 'File uploaded', status: 'success', duration: 2000 });
      } catch (error: any) {
        setError(error?.toString() || 'Upload failed');
        toast({ title: 'Upload failed', description: error?.toString(), status: 'error', duration: 4000 });
      } finally {
        setLoading(false);
        uploading.current = false;
      }
    }
  }, [addFile, setLoading, setError, toast]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, multiple: true });

  return (
    <Box
      {...getRootProps()}
      border="2px dashed"
      borderColor={isDragActive ? 'blue.400' : 'gray.200'}
      borderRadius="md"
      p={4}
      textAlign="center"
      bg={isDragActive ? 'blue.50' : 'gray.50'}
      cursor="pointer"
      mb={2}
      position="relative"
    >
      <input {...getInputProps()} />
      {loading && uploading.current ? <Spinner size="sm" position="absolute" right={2} top={2} /> : null}
      <Text color="gray.500">
        {isDragActive ? 'Drop the files here...' : 'Drag & drop or click to upload'}
      </Text>
    </Box>
  );
};

export default FileUpload;
