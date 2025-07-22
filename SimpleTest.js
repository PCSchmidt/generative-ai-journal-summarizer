import React from 'react';

export default function SimpleTest() {
  return (
    <div style={{
      backgroundColor: '#0a0a0a',
      color: '#00d9ff',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif',
      padding: '20px'
    }}>
      <h1 style={{ fontSize: '28px', marginBottom: '10px' }}>
        🤖 AI Journal Summarizer
      </h1>
      <p style={{ fontSize: '18px', color: '#ffffff', marginBottom: '30px' }}>
        Simple React Test (No React Native)
      </p>
      <div style={{
        backgroundColor: '#1a1a2e',
        color: '#ffffff',
        padding: '20px',
        borderRadius: '10px',
        border: '1px solid #00d9ff',
        maxWidth: '400px',
        textAlign: 'center'
      }}>
        <p>If you can see this, basic React is working!</p>
        <p>Issue might be with React Native Web components.</p>
      </div>
    </div>
  );
}
