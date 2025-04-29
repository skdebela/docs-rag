import React from "react";
import { Flex, Box } from '@chakra-ui/react';
import FilesSidebar from '../Files/FilesSidebar';
import ChatArea from '../Chat/ChatArea';

const MainLayout = () => (
  <Flex height="100vh" direction="row" bg="gray.50">
    <Box width={{ base: '100px', md: '320px' }} bg="white" boxShadow="md" zIndex={5}>
      <FilesSidebar />
    </Box>
    <Box flex="1" display="flex" flexDirection="column" minWidth={0}>
      <ChatArea />
    </Box>
  </Flex>
);

export default MainLayout;
