import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView } from 'react-native';
import { useState } from 'react';

export default function App() {
  const [journalText, setJournalText] = useState('');
  const [aiResult, setAiResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!journalText.trim()) {
      alert('Please enter some journal text');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/ai/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: journalText,
          task_type: 'summarize'
        })
      });

      if (response.ok) {
        const result = await response.json();
        setAiResult(result);
      } else {
        alert('Failed to process text');
      }
    } catch (error) {
      alert('Error connecting to AI service');
      console.error(error);
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      
      <View style={styles.header}>
        <Text style={styles.title}>AI Journal Summarizer</Text>
        <Text style={styles.subtitle}>Express your thoughts, get AI insights</Text>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.inputSection}>
          <Text style={styles.label}>Journal Entry:</Text>
          <TextInput
            style={styles.textInput}
            placeholder="Write about your day, thoughts, or experiences..."
            value={journalText}
            onChangeText={setJournalText}
            multiline
            numberOfLines={6}
            textAlignVertical="top"
          />
          
          <TouchableOpacity 
            style={[styles.button, loading && styles.buttonDisabled]} 
            onPress={handleAnalyze}
            disabled={loading}
          >
            <Text style={styles.buttonText}>
              {loading ? 'Analyzing...' : 'Analyze with AI'}
            </Text>
          </TouchableOpacity>
        </View>

        {aiResult && (
          <View style={styles.resultSection}>
            <Text style={styles.resultTitle}>AI Summary:</Text>
            <View style={styles.resultCard}>
              <Text style={styles.resultText}>{aiResult.result}</Text>
              <View style={styles.metadata}>
                <Text style={styles.metadataText}>
                  Confidence: {Math.round(aiResult.confidence * 100)}%
                </Text>
                <Text style={styles.metadataText}>
                  Model: {aiResult.metadata.model}
                </Text>
              </View>
            </View>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#4A90E2',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  inputSection: {
    marginTop: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
    color: '#333',
  },
  textInput: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    minHeight: 120,
    borderWidth: 1,
    borderColor: '#ddd',
    marginBottom: 15,
  },
  button: {
    backgroundColor: '#4A90E2',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  resultSection: {
    marginTop: 20,
    marginBottom: 30,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 10,
    color: '#333',
  },
  resultCard: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  resultText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
    marginBottom: 10,
  },
  metadata: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingTop: 10,
  },
  metadataText: {
    fontSize: 12,
    color: '#666',
  },
});
