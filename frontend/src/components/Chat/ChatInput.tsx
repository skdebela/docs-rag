import React, { useState } from 'react';
import { HStack, Input, IconButton, Spinner, useToast } from '@chakra-ui/react';
import { FaPaperPlane } from 'react-icons/fa';
import { useChatStore } from '../../state/chatStore';

const ChatInput = () => {
  const [value, setValue] = useState('');
  const sendChat = useChatStore((state) => state.sendChat);
  const loading = useChatStore((state) => state.loading);
  const error = useChatStore((state) => state.error);
  const toast = useToast();

  const handleSend = async () => {
    if (!value.trim() || loading) return;
    await sendChat(value);
    setValue('');
  };

    // Show error toast if error changes
  React.useEffect(() => {
    if (error) {
      toast({
        title: 'Chat Error',
        description: error,
        status: 'error',
        duration: 4000,
        isClosable: true,
        position: 'top',
      });
    }
  }, [error, toast]);

  return (
    <HStack spacing={2}>
      <Input
        placeholder="Ask about your documents..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        bg="white"
        borderRadius="xl"
        isDisabled={loading}
      />
      <IconButton
        icon={loading ? <Spinner size="sm" /> : <FaPaperPlane />}
        colorScheme="blue"
        aria-label="Send"
        onClick={handleSend}
        isDisabled={!value.trim() || loading}
      />
    </HStack>
  );
};

export default ChatInput;
