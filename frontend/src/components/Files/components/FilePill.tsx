import React from 'react';
import { HStack, Icon, Text, Box, IconButton } from '@chakra-ui/react';
import { FaFileAlt, FaTrash } from 'react-icons/fa';
import { FileMeta } from 'state/filesStore';

const getFileExt = (filename?: string) => {
  if (!filename) return '';
  const parts = filename.split('.');
  return parts.length > 1 ? parts.pop()?.toLowerCase() : '';
};

type FilePillProps = {
  file: FileMeta;
  onDelete?: (id: number) => void;
  deleting?: boolean;
};

const FilePill = ({ file, onDelete, deleting }: FilePillProps) => (
  <HStack spacing={2} px={3} py={2} borderRadius="full" bg="gray.100" _hover={{ bg: 'blue.50' }}>
    <Icon as={FaFileAlt} color="blue.400" />
    <Text fontSize="sm" isTruncated>{file.filename}</Text>
    <Box as="span" fontSize="xs" color="gray.500">{getFileExt(file.filename)}</Box>
    {onDelete && (
      <IconButton
        aria-label="Delete file"
        icon={<FaTrash />}
        size="xs"
        colorScheme="red"
        variant="ghost"
        isLoading={deleting}
        onClick={() => onDelete(file.id)}
      />
    )}
  </HStack>
);

export default FilePill;
