import React from 'react';
import { Text } from 'react-native';

export default function MinimalTest() {
  console.log('🚀 MinimalTest component mounting...');
  
  return React.createElement(Text, {
    style: {
      color: '#00d9ff',
      fontSize: 24,
      textAlign: 'center',
      padding: 50
    }
  }, '✅ React Native Web is working!');
}
