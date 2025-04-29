import React from "react";
import { Flex, Box } from '@chakra-ui/react';
import FilesSidebar from '../Files/FilesSidebar';
import ChatArea from '../Chat/ChatArea';

const MainLayout = () => (
  <Flex height="100vh" direction="row" overflow="hidden" bg="#fff">
    <Box width={{ base: '100px', md: '320px' }} bg="#fff" boxShadow="md" zIndex={5}>
      <FilesSidebar />
    </Box>
    <Box
      flex="1"
      display="flex"
      flexDirection="column"
      minWidth={0}
      justifyContent="center"
      alignItems="center"
      px={{ base: 2, sm: 4, md: 8 }}
      py={{ base: 2, md: 6 }}
    >
      <Box
        w="100%"
        maxW="900px"
        mx="auto"
        display="flex"
        flexDirection="column"
        overflow="hidden"
      >
        <ChatArea />
      </Box>
    </Box>
  </Flex>
);

export default MainLayout;
