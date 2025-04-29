import React from "react";
import { ChakraProvider, Box } from '@chakra-ui/react';
import Header from './components/Layout/Header';
import MainLayout from './components/Layout/MainLayout';
import theme from './styles/theme';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Box height="100%" bg="gray.50">
        <Header />
        <MainLayout />
      </Box>
    </ChakraProvider>
  );
}

export default App;
