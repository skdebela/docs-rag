import React from 'react';
import { Box, VStack, Spinner, Flex, Alert, AlertIcon } from '@chakra-ui/react';
import { useChatStore } from '../../state/chatStore';
import ChatBubble from './ChatBubble';
import ChatInput from './ChatInput';
import { useFilesStore } from '../../state/filesStore';

// Show friendly message if no files are uploaded
const ChatArea = () => {
  const messages = useChatStore((state) => state.messages);
  const files = useFilesStore((state) => state.files);
  const noFiles = !files || files.length === 0;
  const loading = useChatStore((state) => state.loading);
  const error = useChatStore((state) => state.error);

  return (
    <Flex direction="column" h="100%" minH={0} flex="1" px={{ base: 2, sm: 4, md: 8 }}>
      {noFiles ? (
        <Box flex="1">
          <Alert status="info" borderRadius="md" maxW="sm" mt={6} mx="auto">
            <AlertIcon />
            Please upload a file to start chatting.
          </Alert>
        </Box>
      ) : (
        <>
          {error && (
            <Box mb={2} p={2} bg="red.50" color="red.600" borderRadius="md" fontSize="sm">
              {error}
            </Box>
          )}
          <VStack spacing={3} align="stretch" flex="1">
            {messages.map((msg, idx) => (
              <ChatBubble key={idx} message={msg} />
            ))}
            {loading && (
              <Box alignSelf="flex-start" p={2}>
                <Spinner size="sm" color="blue.400" />
              </Box>
            )}
          </VStack>
        </>
      )}
      <Box
        position="sticky"
        bottom={0}
        p={2}
        mt={6}
        borderTop="1px solid #eee"
        zIndex={1}
        bg="white"
        boxShadow="sm"
        borderRadius="lg"
      >
        <ChatInput />
      </Box>
    </Flex>
  );
};

export default ChatArea;
