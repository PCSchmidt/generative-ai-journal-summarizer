import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      <Text style={styles.title}>🤖 AI Journal Summarizer</Text>
      <Text style={styles.subtitle}>React Native Web Test</Text>
      <View style={styles.card}>
        <Text style={styles.cardText}>If you can see this, React Native Web is working!</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#00d9ff',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: '#ffffff',
    marginBottom: 30,
    textAlign: 'center',
  },
  card: {
    backgroundColor: '#1a1a2e',
    padding: 20,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#00d9ff',
    maxWidth: 400,
  },
  cardText: {
    color: '#ffffff',
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
  },
});
