import React from 'react';
import { AppRegistry } from 'react-native';

function WebTest() {
  const containerStyle = {
    backgroundColor: '#0a0a0a',
    color: '#00d9ff',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    fontFamily: 'Arial, sans-serif',
    padding: '20px'
  };

  const titleStyle = {
    fontSize: '28px',
    marginBottom: '10px',
    fontWeight: 'bold'
  };

  const subtitleStyle = {
    fontSize: '18px',
    color: '#ffffff',
    marginBottom: '30px'
  };

  const cardStyle = {
    backgroundColor: '#1a1a2e',
    color: '#ffffff',
    padding: '20px',
    borderRadius: '10px',
    border: '1px solid #00d9ff',
    maxWidth: '400px',
    textAlign: 'center'
  };

  return (
    <div style={containerStyle}>
      <h1 style={titleStyle}>🤖 AI Journal Summarizer</h1>
      <p style={subtitleStyle}>Direct React Component Test</p>
      <div style={cardStyle}>
        <p>If you can see this, React is working properly!</p>
        <p style={{marginTop: '10px'}}>Testing without React Native Web components.</p>
      </div>
    </div>
  );
}

export default WebTest;

// Register for web platform
if (typeof document !== 'undefined') {
  AppRegistry.registerComponent('main', () => WebTest);
  AppRegistry.runApplication('main', {
    initialProps: {},
    rootTag: document.getElementById('root'),
  });
}
