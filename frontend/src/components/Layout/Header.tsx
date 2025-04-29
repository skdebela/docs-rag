import React from "react";
import { Flex, Heading } from '@chakra-ui/react';

const Header = () => (
  <Flex as="header" align="center" p={4} boxShadow="sm" bg="white" zIndex={10}>
    <Heading size="md" color="blue.600">Local Chat RAG</Heading>
  </Flex>
);

export default Header;
