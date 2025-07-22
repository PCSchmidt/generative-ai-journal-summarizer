import React from 'react';

export default function MinimalTest() {
  console.log('🚀 MinimalTest component mounting...');
  
  // Use pure React instead of React Native components
  return React.createElement('div', {
    style: {
      backgroundColor: '#0a0a0a',
      color: '#00d9ff',
      fontSize: '24px',
      textAlign: 'center',
      padding: '50px',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif'
    }
  }, '✅ JavaScript Bundle is Executing!');
}
