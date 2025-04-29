import React from "react";
import { Flex, Heading, Spacer, Menu, MenuButton, MenuList, MenuItem, IconButton } from '@chakra-ui/react';
import { FaRegUserCircle } from 'react-icons/fa';

const Header = () => (
  <Flex as="header" align="center" p={4} boxShadow="sm" bg="white" zIndex={10}>
    <Heading size="md" color="blue.600">Chat with Files</Heading>
    <Spacer />
    <Menu>
      <MenuButton as={IconButton} icon={<FaRegUserCircle />} variant="ghost" aria-label="User menu" />
      <MenuList>
        <MenuItem>Profile</MenuItem>
        <MenuItem>Settings</MenuItem>
        <MenuItem>Logout</MenuItem>
      </MenuList>
    </Menu>
  </Flex>
);

export default Header;
