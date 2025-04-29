import React from 'react';
import { Box, VStack, Spinner, Flex } from '@chakra-ui/react';
import { useChatStore } from '../../state/chatStore';
import ChatBubble from './ChatBubble';
import ChatInput from './ChatInput';

const ChatArea = () => {
  const messages = useChatStore((state) => state.messages);
  const loading = useChatStore((state) => state.loading);
  const error = useChatStore((state) => state.error);
  return (
  <Flex direction="column" h="100%" minH={0} flex="1" position="relative">
    {error && (
      <Box mb={2} p={2} bg="red.50" color="red.600" borderRadius="md" fontSize="sm">
        {error}
      </Box>
    )}
    {/* Scrollable chat messages area */}
    <VStack spacing={3} align="stretch" flex="1" overflowY="auto" mb={2}>
      {messages.map((msg, idx) => (
        <ChatBubble key={idx} message={msg} />
      ))}
      {loading && (
        <Box alignSelf="flex-start" p={2}>
          <Spinner size="sm" color="blue.400" />
        </Box>
      )}
    </VStack>
    {/* Sticky chat input at the bottom */}
    <Box
      position="sticky"
      bottom={0}
      bg="white"
      p={2}
      borderTop="1px solid #eee"
      zIndex={1}
    >
      <ChatInput />
    </Box>
  </Flex>
);
};

export default ChatArea;
